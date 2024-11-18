import streamlit as st
import pandas as pd
from utils import load_data, perform_search, extract_using_llm, save_results, load_google_sheet_data, update_google_sheet
import logging

st.title("AI Agent for Information Retrieval")

# Choose Data Source (CSV Upload or Google Sheets)
data_source = st.radio("Choose Data Source", ["Upload CSV File", "Connect to Google Sheets"])

data = None
column = None

if data_source == "Upload CSV File":
    uploaded_file = st.file_uploader("Upload CSV File", type="csv")
    if uploaded_file:
        try:
            data = load_data(uploaded_file)
            if data.empty:
                st.warning("Uploaded CSV is empty. Please upload a valid file.")
            else:
                st.write("Data Preview:", data.head())
                column = st.selectbox("Select Column for Entity Extraction", data.columns)
        except ValueError as ve:
            st.error(f"Error loading CSV file: {ve}")
        except Exception as e:
            st.error(f"Unexpected error occurred: {e}")
        
elif data_source == "Connect to Google Sheets":
    # Google Sheets Connection
    sheet_url = st.text_input("Enter Google Sheets URL")
    if sheet_url:
        try:
            data = load_google_sheet_data(sheet_url)
            if data.empty:
                st.warning("No data found in the Google Sheet. Please ensure the sheet is not empty.")
            else:
                st.write("Data Preview:", data.head())
                column = st.selectbox("Select Column for Entity Extraction", data.columns)
        except ValueError as ve:
            st.error(f"Value Error: {ve}")
        except Exception as e:
            st.error(f"Unexpected error occurred: {e}")

prompt_template = st.text_input("Enter custom prompt (use {entity} as placeholder)", "Get me the email address of {entity}")

st.info("Use {entity} as a placeholder in the prompt, and it will be replaced by values from the selected column (e.g., {company}).")

if prompt_template and "{entity}" not in prompt_template:
    st.error("Your prompt must include the placeholder '{entity}'. Please modify your prompt.")
elif prompt_template:
    st.write(f"Your prompt preview: {prompt_template.format(entity='Example Company')}")

# Search and Extraction Process
if st.button("Start Search"):
    if column and prompt_template:
        if "{entity}" not in prompt_template:
            st.error("The prompt must include the placeholder {entity}.")
            st.stop()
            
        results = []
        progress_bar = st.progress(0)
        entities = data[column].dropna().unique()

        with st.spinner("Processing entities..."):
            for i, entity in enumerate(entities):
                try:
                    progress_bar.progress((i + 1) / len(entities))
                    search_prompt = prompt_template.format(entity=entity)

                    search_results = perform_search(search_prompt)

                    # Extract the information using LLM
                    extracted_data = extract_using_llm(search_results, prompt_template, entity)

                    for result in search_results:
                        results.append({
                            "entity": entity,
                            "title": result["title"],
                            "link": result["link"],
                            "snippet": result["snippet"],
                            "extracted_data": extracted_data
                        })
                    
                except Exception as e:
                    logging.error(f"Error occurred for entity '{entity}': {e}")
                    st.warning(f"Could not process entity '{entity}'. Check logs for details.")

        
        # Display Extracted Data
        if results:
            results_df = pd.DataFrame(results)
            st.write("Extracted Data", results_df)
            
            st.download_button("Download Results as CSV", results_df.to_csv(index=False).encode('utf-8'), "extracted_data.csv")

            # Update Google Sheets (if Google Sheets was used as source)
            if data_source == "Connect to Google Sheets":
                update_sheet = st.button("Update Google Sheet with Extracted Data")
                with st.spinner("Updating Google Sheet..."):
                        try:
                            update_google_sheet(sheet_url, results_df)
                            st.success("Google Sheet updated successfully!")
                        except Exception as e:
                            logging.error(f"Error updating Google Sheet: {e}")
                            st.error(f"Failed to update Google Sheet: {e}")
        else:
            st.warning("No results found. Please check your prompt and data.")
    else:
        st.warning("Please upload a file, select a column, and enter a prompt.")
