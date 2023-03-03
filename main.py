import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.auth
from email.message import EmailMessage
"""
    Python code to demonstrate Gmail APIs
    Message sending and search functionalities has been implemented
    Date : 01.03.2023
    Developer: Justine Paul Mundackal
    
"""
# Class has been defined to handle the scenario
# init method will handle the authentication 
# gmail_send_message method will handle the email sending process
# search method will handle the search logic
class gmailAPI:
    #Credentials json file needs to be maintained in the directory and pass the file name when create the object
    def __init__(self,credjson):
        #Scopes needs to be added as per the change in functionality and token needs to be recreated in case of any change
        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.send']
        self.creds = None
        # Token file will be created when run the code for the first time so no validation required later
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credjson, SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

        try:
        
            # Call the Gmail API(Labels) for testing the credentials
            service = build('gmail', 'v1', credentials=self.creds)
            results = service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])

            if not labels:
                print('No labels found.')
                return
            print('Authentication Successful via Credentials.json or Token.json')

        except HttpError as error:
            print(f'An error occurred: {error}')

    # Write and send logic, need to pass to address, subject and message
    def gmail_send_message(self, to, sub, msg ):

        try:
            service = build('gmail', 'v1', credentials=self.creds)
            message = EmailMessage()

            message.set_content(msg)
            message['To'] = to
            message['Subject'] = sub

            # encoded message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
                .decode()

            create_message = {
                'raw': encoded_message
            }
            # Calling message send API with inputs
            send_message = (service.users().messages().send
                            (userId="me", body=create_message).execute())
            print(F'Message sent and the id is : {send_message["id"]}')
        except HttpError as error:
            print(F'An error occurred: {error}')
            send_message = None
        return send_message
    
    # Search functionality works with keyword
    def search(self,keyword):
        try:
            service = build('gmail', 'v1', credentials=self.creds)
            # Gmail API for search
            search_ids = service.users().messages().list(userId="me", q=keyword).execute()
        except HttpError as error:
            print(F'An error occurred: {error}')
        # Hits are limited for display            
        limit = 5
        # Looping through the search result and display the details
        for index, i in enumerate(search_ids["messages"]):
            if index == limit:
                print(f'Search is limited to {limit}')
                break
            message = service.users().messages().get(userId="me", id=i["id"] ,format='full').execute()
            # Looping the header for information
            for j in message["payload"]["headers"]:
                if j["name"] == 'To':
                    print("To: ",j['value'])
                if j["name"] == 'Subject':
                    print("Subject: ",j['value'])
                if j["name"] == 'Date':
                    print("Date: ",j['value'])
                if j["name"] == 'From':
                    print("From: ",j['value'])                        
            decoded_data = base64.b64decode(message["payload"]["body"]["data"]).decode('utf-8')
            print("Message:\n ", decoded_data)

if __name__ == '__main__':
    # Please maintain the 'credentials.json' file in project directory
    # Code can be enhanced to handle more than one credentials using this Class
    obj = gmailAPI('credentials.json')
    choice = '0'
    # User input
    while(choice != '3'):
        print("\nGMAIL API DEMO, \
          \n\n1. Write Email \
          \n2. Search Email \
          \n3. Exit")
        choice = input("Enter the option(1,2,3): ")
        if choice == '1':
            to = input("To address: ")
            subject = input("Email Subject: ")
            message = input("Enter Mail Content:\n ")
            # Call send method with inputs
            obj.gmail_send_message(to, subject, message)
        elif choice == '2':
            keyword = input("Enter search keyword: ")
            obj.search(keyword)
        elif choice == '3':
            print("\nThanks for using the service. Cheers !!")
        else:
            print("Wrong input !!")

            