import pandas as pd
import requests
import openai
import serpapi

import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
import time
import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials

logging.basicConfig(level=logging.INFO)

load_dotenv(".env")
SEARCH_API_KEY = os.getenv('SEARCH_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY


def load_data(file):
    try:
        return pd.read_csv(file)
    except Exception as e:
        raise ValueError(f"Error loading data: {e}")

def authenticate_google_sheets():
    logging.info("Authenticating Google Sheets...")

    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly'])
            creds = flow.run_local_server(port=5000)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def load_google_sheet_data(sheet_url_or_id):
    sheet_id = sheet_url_or_id.split('/')[-2]
    range_name = "Sheet1"
    creds = authenticate_google_sheets()
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    
    result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
    
    logging.info(f"Google Sheets API response: {result}")
        
    values = result.get('values', [])
    
    if not values:
        logging.warning("No data found in the specified range.")
        raise ValueError("No data found in the sheet.")
    
    # Assuming the first row contains headers
    columns = values[0]
    rows = values[1:]
    
    df = pd.DataFrame(rows, columns=columns)
    logging.info("Data successfully loaded from Google Sheets.")
    return df

#Search Function with Rate Limiting and Structured Results
def perform_search(query):
    api_key = os.getenv("SEARCH_API_KEY")
    if not api_key:
        raise EnvironmentError("Search API key is missing. Please add it to the .env file.")

    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "hl": "en",
        "api_key": SEARCH_API_KEY,
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        search_results = response.json().get("organic_results", [])

        results = []
        for result in search_results:
            results.append({
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "snippet": result.get("snippet", "")
            })
        
        # Simulated rate limit handling by adding delay
        time.sleep(1) 
        return results

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"An error occurred with the request: {e}")

def generate_dynamic_prompt(df, column_name, prompt_template):
    """
    :param df: The DataFrame containing the data.
    :param column_name: The column name containing the entities
    :param prompt_template: The prompt template with placeholders

    """
    responses = []
    all_search_results = []
    
    for entity_value in df[column_name]:
        
        prompt = prompt_template.format(company=entity_value)
        
        search_results = perform_search(prompt)
        all_search_results.append({"entity": entity_value, "search_results": search_results})
        
        response = extract_information(search_results, prompt)
        responses.append(response)
    
    return responses, all_search_results

def process_google_sheet(sheet_url_or_id, column_name, prompt_template):
    """
    Args:
    - sheet_url_or_id: The URL or ID of the Google Sheet.
    - column_name: The column name containing entities to process.
    - prompt_template: Prompt template with placeholders for processing.

    """
    try:
        # Load data from Google Sheet
        df = load_google_sheet_data(sheet_url_or_id)
        
        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found in the sheet.")

        extracted_data = []

        for entity_value in df[column_name]:
     
            prompt = prompt_template.format(entity=entity_value)
            search_results = perform_search(prompt)

            extracted_info = extract_using_llm(search_results, prompt_template, entity_value)
            extracted_data.append(extracted_info)
        
        df["Extracted Information"] = extracted_data
        logging.info("Data processed and extracted successfully.")
        return df
    except Exception as e:
        logging.error(f"Error processing Google Sheet data: {e}")
        raise e

def extract_information(search_results, prompt_template, entity_value=None):

    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise EnvironmentError("OpenAI API key is missing.")

    prompt = prompt_template.format(company=entity_value) if entity_value else prompt_template
    
    messages = [{"role": "system", "content": "Extract relevant information as requested."}]
    
    for result in search_results:
        messages.append({"role": "user", "content": f"{prompt}\n\nContent: {result.get('snippet', '')}"})

    try:
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        return response.choices[0].message["content"].strip()
    except Exception as e:
        raise RuntimeError(f"LLM extraction failed: {e}")

def extract_using_llm(search_results, prompt_template, entity):
    """
    Function to send the search results and the user prompt to the LLM for processing.
    Extracts the requested information based on the prompt.
    
    Args:
    - search_results: List of search result objects (links, titles, snippets)
    - prompt_template: The prompt to send to the LLM, with a placeholder for entity
    - entity: The specific entity (company, person, etc.) to extract information for

    """
    try:

        prompt = prompt_template.format(entity=entity)
        web_content = "\n".join([result["snippet"] for result in search_results]) 

        full_prompt = f"{prompt}\n\nWeb Results:\n{web_content}"

        response = openai.Completion.create(
            model="text-davinci-003", 
            prompt=full_prompt,
            max_tokens=500,  
            temperature=0.5,  
            n=1,  
            stop=["\n"] 
        )
        
        extracted_data = response.choices[0].text.strip()
        return extracted_data
    
    except Exception as e:
        logging.error(f"Error while extracting using LLM: {e}")
        return None
    
def update_google_sheet(sheet_url, data_df):

    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("C:/Projects/breakoutai-441218-396601674713.json", scope)  # Replace with your path
        client = gspread.authorize(creds)

        sheet = client.open_by_url(sheet_url).sheet1

        data = [data_df.columns.tolist()] + data_df.values.tolist()

        sheet.insert_rows(data, 2)

    except Exception as e:
        print(f"Error updating Google Sheet: {e}")
        raise e

def save_results(dataframe, filename):
    try:
        dataframe.to_csv(filename, index=False)
    except Exception as e:
        raise IOError(f"Error saving results: {e}")
