import os
import requests
import pytz
from datetime import datetime
from api_token import generate_access_token  # Importiere die Funktion

# Azure App Informationen
APPLICATION_ID = 'APP_ID'  # Ersetzen Sie dies durch Ihre Azure App ID
authority_url = 'https://login.microsoftonline.com/consumers/'
base_graph_request_url = 'https://graph.microsoft.com/v1.0/'

# Berechtigungen für den Zugriff auf E-Mails und Anhänge
SCOPES = ['User.Read', 'Mail.Read']

# Dateipfad für den gespeicherten Zeitstempel
timestamp_file = 'last_run_timestamp.txt'

# Versuchen, den letzten Zeitstempel zu laden, falls vorhanden
last_run_timestamp = None
if os.path.exists(timestamp_file):
    with open(timestamp_file, 'r') as file:
        last_run_timestamp = file.read().strip()

# Access Token abrufen
access_token_response = generate_access_token(app_id=APPLICATION_ID, scopes=SCOPES)

if 'access_token' in access_token_response:
    access_token = access_token_response['access_token']
    headers = {'Authorization': 'Bearer ' + access_token}

    # E-Mail-Anfrage: Nur E-Mails nach dem letzten Zeitstempel abrufen
    graph_request_url = base_graph_request_url + 'me/messages'
    
    # Wenn ein Zeitstempel existiert, nur Mails nach diesem abrufen
    if last_run_timestamp:
        graph_request_url += f"?$filter=receivedDateTime ge {last_run_timestamp}"

    response = requests.get(graph_request_url, headers=headers)
    messages = response.json().get("value", [])

    # Prüfen, ob Nachrichten vorhanden sind und Anhänge herunterladen
    if not os.path.exists('file-downloads'):
        os.makedirs('file-downloads')

    for message in messages:
        print(f"Überprüfe Nachricht: {message.get('subject', 'Kein Betreff')}")

        # Abrufen der Anhänge der Nachricht
        message_id = message['id']
        attachments_url = f'{base_graph_request_url}/me/messages/{message_id}/attachments'
        attachments_response = requests.get(attachments_url, headers=headers)
        attachments = attachments_response.json().get("value", [])

        for attachment in attachments:
            if '@odata.mediaContentType' in attachment:  # Prüfen, ob es sich um eine Datei handelt
                attachment_id = attachment['id']
                download_url = f"{base_graph_request_url}/me/messages/{message_id}/attachments/{attachment_id}/$value"
                download_response = requests.get(download_url, headers=headers)
                
                # Dateiname mit Zeitstempel, um Überschreibungen zu vermeiden
                timestamp = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
                filename = attachment.get('name', 'Unbenannt')
                filename_with_timestamp = f"{timestamp}_{filename}"
                filepath = f"file-downloads/{filename_with_timestamp}"

                # Datei speichern
                with open(filepath, mode="wb") as file:
                    file.write(download_response.content)
                print(f"Anhang '{filename}' wurde erfolgreich heruntergeladen und unter '{filepath}' gespeichert.")      

    # Speichern des aktuellen Zeitstempels, um die nächste Anfrage darauf abzustimmen
    timestamp = datetime.now(pytz.UTC).isoformat()
    current_timestamp = timestamp[:-6] + 'Z'
    with open(timestamp_file, 'w') as file:
        file.write(current_timestamp)
        
    print(graph_request_url)
else:
    print("Fehler bei der Authentifizierung oder Token-Abruf.")
