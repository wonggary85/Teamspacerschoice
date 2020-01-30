#!/usr/bin/env python3
from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def getSMS():
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    creds = None
    userId = 'me'
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                #flow = InstalledAppFlow.from_client_secrets_file('client_secret_899484416059-9b1jv1s492b1r1srrebcfovfifcv2v12.apps.googleusercontent.com.json', SCOPES)
                creds = flow.run_local_server(port=0)
            except FileNotFoundError:
                print("Enable the Gmail API, create an OAuth client ID (type:Other),  and download the client_secret.json to the same directory.\nSee: https://console.developers.google.com/\n")
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    response = service.users().messages().list(userId='me', labelIds=['CHAT'], maxResults=1).execute()
    thread_id = response['messages'][0]['threadId']
    thread = service.users().threads().get(userId='me', id=thread_id).execute()
    msg = thread['messages'][len(thread['messages'])-1]['snippet'].split(':')[1].strip()

    return msg
