from datetime import datetime
import json
import os
import webbrowser
import msal

from lost_link.const import API_SCOPE
from lost_link.dir_manager import DirManager
from lost_link.settings import Settings

authority_url = 'https://login.microsoftonline.com/consumers/'

class GraphAPIAuthentication:
    """
    This class provides methods to authenticate with Microsoft Graph API using the Microsoft Authentication Library (MSAL).
    It supports token caching to avoid unnecessary re-authentication.
    """

    def __init__(self, dir_manager: DirManager, settings: Settings):
        self.application_id = settings.get(Settings.KEY_APP_ID)
        self.token_path = dir_manager.get_auth_token_path()

    def get_access_token_header(self) -> dict[str, str]:
        """
        Generates an HTTP header for authenticating requests to Microsoft Graph API using a valid access token.

        Args:
            permission_scopes (list[str]):  List of required permission scopes (e.g., ['User.Read', 'Mail.Read'])

        Returns:
            dict[str, str]: HTTP-Header {'Authorization': 'Bearer <Access Token>'}
        """
        token_response = self.get_access_token()
        access_token = token_response['access_token']
        headers = {'Authorization': 'Bearer ' + access_token}
        return headers

    def login_if_needed(self):
        token_cache = self._get_serialized_token_cache(API_SCOPE)
        client = msal.PublicClientApplication(client_id=self.application_id, token_cache=token_cache)

        accounts = client.get_accounts()

        if not accounts:
            print("Login erforderlich, bitte den Anweisungen folgen:")
            self._generate_new_access_token(client=client, permission_scopes=API_SCOPE)


    def get_access_token(self) -> dict:
        """
        Retrieves an access token for the specified permission scopes. 
        Uses the cached token if available and valid; otherwise, generates a new token via the MSAL device code flow. 

        Args:
            permission_scopes (list[str]): List of required permission scopes

        Returns:
            dict: A dictionary containing the token response, including the access_token
        """
        token_cache = self._get_serialized_token_cache(API_SCOPE)
        client = msal.PublicClientApplication(client_id=self.application_id, token_cache=token_cache)

        accounts = client.get_accounts()

        if accounts:
            token_response = client.acquire_token_silent(API_SCOPE, accounts[0])
        else:
            token_response = self._generate_new_access_token(client=client, permission_scopes=API_SCOPE)

        return token_response
    

    def _save_token_cache(self, token_cache: msal.SerializableTokenCache):
        with open(self.token_path, 'w') as f:
            f.write(token_cache.serialize())

    
    def _get_serialized_token_cache(self, permission_scopes: list[str]) -> msal.SerializableTokenCache:
        token_cache = msal.SerializableTokenCache()
        if os.path.exists(self.token_path) and self._is_token_cache_valid(permission_scopes):
            token_cache.deserialize(open(self.token_path, 'r').read())
        return token_cache

        
    def _is_token_cache_valid(self, requested_scopes: list[str]) -> bool:
        if not os.path.exists(self.token_path):
            return False

        try:
            # load token-cache
            token_detail = json.load(open(self.token_path))
            
            # check expiration date
            token_key = list(token_detail['AccessToken'].keys())[0]
            token_expiration = datetime.fromtimestamp(
                int(token_detail['AccessToken'][token_key]['expires_on'])
            )
            if datetime.now() > token_expiration:
                return False

            # compare scopes
            cached_scopes = token_detail['AccessToken'][token_key]['target'].split()
            if not all(scope in cached_scopes for scope in requested_scopes):
                return False

            return True
        
        except (KeyError, ValueError, FileNotFoundError, json.JSONDecodeError):
            return False


    def _generate_new_access_token(self, client: msal.PublicClientApplication, permission_scopes: list[str]) -> dict:
            flow = client.initiate_device_flow(scopes=permission_scopes)
            
            print(flow['message'])
            webbrowser.open(flow['verification_uri'])
            
            token_response = client.acquire_token_by_device_flow(flow)
        
            self._save_token_cache(client.token_cache)
            
            return token_response

    