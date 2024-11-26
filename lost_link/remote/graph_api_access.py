from datetime import datetime
import requests
import json
import os

from lost_link.remote.graph_api_authentication import GraphAPIAuthentication


class GraphAPIAccess:

    @staticmethod
    def api_request(request_url: str):
        headers = GraphAPIAuthentication.get_access_token_header(['User.Read', 'Files.Read'])
        headers["Prefer"] = "deltaExcludeParent"      
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
    def get_delta_changes():
        request_url = "https://graph.microsoft.com/v1.0/me/drive/root/delta"
        delta_link = GraphAPIAccess.read_delta_link()
        if delta_link:
            request_url = delta_link
        
        response = GraphAPIAccess.api_request(request_url)
        new_delta_link = response.get("@odata.deltaLink", "")
        next_link = response.get("@odata.nextLink", "")
        delta_changes = response.get("value", "")

        while next_link:
            next_link_response = GraphAPIAccess.api_request(next_link)
            new_delta_link = next_link_response.get("@odata.deltaLink", "")
            next_link = next_link_response.get("@odata.nextLink", "")
            delta_changes = delta_changes + next_link_response.get("value", "")

        if new_delta_link:
            GraphAPIAccess.save_delta_link(new_delta_link)
        return delta_changes
    
    staticmethod
    def search_drive_item(item_id: str):
        request_url = "https://graph.microsoft.com/v1.0/me/drive/items/" + item_id
        response = GraphAPIAccess.api_request(request_url)
        return response

