from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

creds = service_account.Credentials.from_service_account_file(
    '01 Derecho Constitucional/dip-python-490901-a9641d72ce14.json', scopes=SCOPES)

service = build('drive', 'v3', credentials=creds)

FOLDER_ID = "1TQwJMW-JRI8iq2dakW9-70fLKbGhkCk5"

results = service.files().list(
    q=f"'{FOLDER_ID}' in parents",
    fields="files(id, name)"
).execute()

for f in results.get('files', []):
    print(f)