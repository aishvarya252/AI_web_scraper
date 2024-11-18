
# AI Web Scraper for Information Retrieval

This project is an AI-driven information retrieval dashboard that allows users to search for and extract specific information from various sources. It supports CSV uploads and Google Sheets for data sources, utilizes OpenAI for language models, and integrates with Google Sheets for seamless data management. Users can run custom queries, extract relevant data, and download results in a CSV format or update them directly in Google Sheets.

## Features

- Upload data via CSV file or Google Sheets.
- Use custom prompts for specific information retrieval from the web.
- Display extracted data in a user-friendly table.
- Download results as a CSV or update results in Google Sheets.
- Utilizes OpenAI language models and SerpAPI for enhanced search and information extraction.

---

## Table of Contents

- [Installation](#installation)
- [Setup Instructions](#setup-instructions)
- [Usage Guide](#usage-guide)
- [API Keys and Environment Variables](#api-keys-and-environment-variables)
- [Optional Features](#optional-features)
- [Troubleshooting](#troubleshooting)

---

## Installation

### 1. Clone the Repository:

```bash
git clone https://github.com/your-username/AI-web-scraper.git
cd AI-web-scraper
```

### 2. Create a Virtual Environment:

```bash
python -m venv myenv
source myenv/bin/activate    # On Windows: myenv\Scriptsctivate
```

### 3. Install Dependencies:

Make sure pip is up-to-date and install all necessary packages:

```bash
pip install -r requirements.txt
```

---

## Setup Instructions

### 1. Obtain API Keys

To run this application, you need API keys for both OpenAI and SerpAPI, as well as a Google Sheets API credential file.

#### OpenAI API Key:
- Sign up at OpenAI and obtain an API key.

#### SerpAPI Key:
- Sign up at SerpAPI and get an API key.

#### Google Sheets API Credentials:
- Go to the [Google Cloud Console](https://console.cloud.google.com/).
- Enable the Google Sheets API.
- Create service account credentials.
- Download the credentials.json file and save it in the root directory of this project.

### 2. Set Up Environment Variables

It is recommended to use an `.env` file to store sensitive information such as API keys and file paths.

Create a `.env` file in the root directory:

```plaintext
OPENAI_API_KEY=your_openai_api_key
SERPAPI_API_KEY=your_serpapi_api_key
GOOGLE_CREDENTIALS_PATH=path/to/credentials.json
```

Update the code to read these variables. This is already set up in `utils.py` using the `dotenv` library:

```python
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")
```

### 3. Google Sheets Setup

If you plan to use Google Sheets as a data source, make sure to:

- Share the Google Sheet with the service account email found in the `credentials.json` file.
- Obtain the Google Sheets URL or Sheet ID for use in the app.

---

## Usage Guide

### 1. Run the Application:

```bash
streamlit run app.py --server.port 5000
```

### 2. Using the Dashboard:

1. **Select the data source** by choosing either to upload a CSV file or connect to Google Sheets.
2. If uploading a CSV, upload the file directly. For Google Sheets, enter the URL or Sheet ID.
3. **Choose a column** from the data where the entities for extraction are stored.
4. **Enter a custom prompt template** using `{entity}` as a placeholder for the chosen data (e.g., "Get me the email address of {entity}").
5. **Click Start Search** to retrieve and extract the relevant information.
6. The results will display in a table format. Use the **Download CSV** button to save results locally or update them in the Google Sheet.

---

## API Keys and Environment Variables

Ensure the following environment variables are set in the `.env` file (replace placeholders with actual values):

```plaintext
OPENAI_API_KEY=your_openai_api_key
SERPAPI_API_KEY=your_serpapi_api_key
GOOGLE_CREDENTIALS_PATH=path/to/credentials.json
```

- **OpenAI API Key**: Used for language model queries.
- **SerpAPI Key**: Used for enhanced search capabilities.
- **Google Sheets API Credentials**: JSON file path for Google Sheets API access.

---

## Optional Features

- **Google Sheets Update**: After extracting data, you can directly update a Google Sheet with the new information if you’re using Google Sheets as the data source.
- **Custom Prompts**: Users can provide custom processing commands, such as "find unique values" or "sort by column".
- **Error Handling**: Detailed error messages for invalid Google Sheet URLs or unauthorized access.
- **Data Range Selection**: Flexible sheet range processing (configurable in the code).
- **Scalability**: Supports larger datasets using paginated API requests.

---

## Troubleshooting

### 1. **ModuleNotFoundError for gspread or oauth2client:**

Ensure all dependencies are installed by running:

```bash
pip install -r requirements.txt
```

### 2. **Connection Issues with API:**

Make sure you have a stable internet connection and valid API keys. Double-check the API endpoints if custom endpoints are used.

### 3. **Google Sheets API Errors:**

- Confirm the `credentials.json` file path is correct.
- Verify the service account has permission to access the Google Sheet.

### 4. **Environment Variables Not Loading:**

- Check that your `.env` file is correctly formatted and that variables are named correctly.

---

## Loom Video Walkthrough

Watch the walkthrough video [here](#).

---

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for review.

---

## License

This project is licensed under the MIT License.

---

