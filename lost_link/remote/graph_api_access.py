from datetime import datetime
import requests
import json
import os

from remote.graph_api_authentication import GraphAPIAuthentication
from models.delta_link_manager import DeltaLinkManager 


class GraphAPIAccess:

    @staticmethod
    def api_request(request_url: str):
        headers = GraphAPIAuthentication.get_access_token_header(['User.Read', 'Files.Read'])
        headers["Prefer"] = "deltaExcludeParent"      
        response = requests.get(request_url, headers=headers)
        return response.json()


class OneDriveAccess:

    def __init__(self, delta_link_manager: DeltaLinkManager):
        self._delta_link_manager = delta_link_manager

    def get_delta_changes(self):
        request_url = "https://graph.microsoft.com/v1.0/me/drive/root/delta"
        delta_link = self._delta_link_manager.get_delta_link("OneDrive")
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
            self._delta_link_manager.save_delta_link("OneDrive", new_delta_link)
        return delta_changes
    
    staticmethod
    def search_drive_item(item_id: str):
        request_url = "https://graph.microsoft.com/v1.0/me/drive/items/" + item_id
        response = GraphAPIAccess.api_request(request_url)
        return response

