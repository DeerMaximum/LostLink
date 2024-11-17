import requests
import json
import os

from lost_link.graph_api_authentication import GraphAPIAuthentication


class GraphAPIAccess:

    @staticmethod
    def api_request(request_url: str):
        headers = GraphAPIAuthentication.get_access_token_header(['User.Read', 'Files.Read'])
        response = requests.get(request_url, headers=headers)
        return response.json()

    @staticmethod
    def save_delta_link(delta_link: str, file_path: str="delta_links.json", domain: str="OneDrive"):
        data = {}
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)
        data[domain] = delta_link

        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    @staticmethod
    def read_delta_link(file_path: str = "delta_links.json", domain: str = "OneDrive") -> str:
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)
                return data.get(domain, "")
        return ""


class OneDriveAccess:

    @staticmethod
    def update():
        delta_link = GraphAPIAccess.read_delta_link()
        
        if delta_link:
            # Führe die Delta-Abfrage mit dem gespeicherten Delta-Link aus
            request_url = delta_link
            response = GraphAPIAccess.api_request(request_url)
            new_delta_link = response.get("@odata.deltaLink", "")
            files = response.get("value", "")
            
            for file in files:
                print(file)     #TODO: Auswerten und in DB aktualisieren

            if new_delta_link:
                GraphAPIAccess.save_delta_link(new_delta_link)
        else:
            # Führe die erste Delta-Abfrage ohne Delta-Link aus
            request_url = "https://graph.microsoft.com/v1.0/me/drive/root/delta"
            response = GraphAPIAccess.api_request(request_url)
            new_delta_link = response.get("@odata.deltaLink", "")
            files = response.get("value", "")

            for file in files:
                print(file)     #TODO: Auswerten und in DB aktualisieren
            
            # Speichere den initialen Delta-Link
            if new_delta_link:
                GraphAPIAccess.save_delta_link(new_delta_link)



