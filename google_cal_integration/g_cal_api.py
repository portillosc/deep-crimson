from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
import pymongo

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    
    events = events_result.get('items', [])
    for event in events:
        event['cal_id']='samio.portillo@gmail.com'

    events_result = service.events().list(calendarId='sportillo@ippon.fr', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events_2 = events_result.get('items', [])
    for event in events_2:
        event['cal_id']='sportillo@ippon.fr'

    events = events + events_2

    if not events:
        print('No upcoming events found.')
    # for event in events:
    #     start = event['start'].get('dateTime', event['start'].get('date'))
    #     #print(start, event['summary'])
    #     event_data = json.dumps(event,indent=3)
    #     print(event_data)
        
        # with open('event_data.json', 'w', encoding='utf-8') as f:
        #     json.dump(event_data, f, ensure_ascii=False)
    else:
        uri = "mongodb://weather-report-mongodb:2YCR1nxsdoHtvyFJRYwEESBAbkDDmC9QGtnh3cK9zarK5uvWDFCWLpy3jA0vErtr6muGmVpwWz5mQ3TxeEKOOw==@weather-report-mongodb.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@weather-report-mongodb@&retrywrites=false"
        client = pymongo.MongoClient(uri)
        wrdb = client["g_cal_data"]
        cont1 = wrdb["events"]
        #x = cont1.update_many(events,upsert=True)
        for event in events:
            # get the id
            e_id = event['id']
            res = cont1.update_one({'id':e_id},{'$set':event},upsert=True)


if __name__ == '__main__':
    main()