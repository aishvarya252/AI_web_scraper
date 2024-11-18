from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

# OAuth setup
flow = InstalledAppFlow.from_client_secrets_file(
    'client_secret_275521754050-moth9fakquhojcksadq96tdgi5751vef.apps.googleusercontent.com.json', 
    ['https://www.googleapis.com/auth/spreadsheets.readonly']
)

creds = flow.run_local_server(port=0)

service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

# Provide sheet ID and range
sheet_id = 'your-sheet-id-here'
range_name = 'Sheet1!A1:D10'

result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
values = result.get('values', [])

if not values:
    print('No data found.')
else:
    for row in values:
        print(row)
