import webbrowser
from datetime import datetime
import json
import os
import msal

# Definiert die API-URL für Microsoft Graph
GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'

def generate_access_token(app_id, scopes):
    # Speichert das Session-Token als Token-Datei
    access_token_cache = msal.SerializableTokenCache()

    # Überprüft, ob eine gespeicherte Token-Datei existiert
    if os.path.exists('ms_token.json'):
        # Liest das gespeicherte Token aus der Datei        
        access_token_cache.deserialize(open("ms_token.json", "r").read())
        token_detail = json.load(open('ms_token.json',))
        
        # Extrahiert das Ablaufdatum des Tokens
        token_detail_key = list(token_detail['AccessToken'].keys())[0]
        token_expiration = datetime.fromtimestamp(int(token_detail['AccessToken'][token_detail_key]['expires_on']))
        
        # Wenn das Token abgelaufen ist, wird die gespeicherte Datei gelöscht
        if datetime.now() > token_expiration:
            os.remove('ms_token.json')
            access_token_cache = msal.SerializableTokenCache()

    # Initialisiert die Microsoft-Authentifizierungsanwendung mit der Serialisierbaren Token-Cache-Instanz
    client = msal.PublicClientApplication(client_id=app_id, token_cache=access_token_cache)

    # Versucht, vorhandene Accounts zu holen (also ein gespeichertes Token zu nutzen)
    accounts = client.get_accounts()
    
    if accounts:
        # Wenn es ein gespeichertes Token gibt, wird dieses verwendet
        token_response = client.acquire_token_silent(scopes, accounts[0])
    else:
        # Wenn es kein gespeichertes Token gibt, muss der Benutzer sich erneut authentifizieren
        flow = client.initiate_device_flow(scopes=scopes)
        #print('user_code: ' + flow['user_code'])
        
        # Zeigt dem Benutzer die URL und den Authentifizierungscode an
        print(flow['message'])  # Zeigt dem Benutzer die URL und den Code an
        webbrowser.open(flow['verification_uri']) # Öffnet die URL im Browser
        #webbrowser.open('https://microsoft.com/devicelogin')
        
        # Führt den Device-Flow aus, um das Token zu erhalten
        token_response = client.acquire_token_by_device_flow(flow)

    # Speichert das erhaltene Token im Cache, damit es für zukünftige Anfragen verwendet werden kann
    with open('ms_token.json', 'w') as _f:
        _f.write(access_token_cache.serialize())

    return token_response
