from datetime import datetime
import json
import os
import webbrowser
import msal
from msal import PublicClientApplication

APPLICATION_ID = '792e4432-f94f-4e9a-ae07-d4d155c30a9c'
authority_url = 'https://login.microsoftonline.com/consumers/'
file_path = "ms_token.json"

class GraphAPIAuthentication:
    """
    This class provides methods to authenticate with Microsoft Graph API using the Microsoft Authentication Library (MSAL).
    It supports token caching to avoid unnecessary re-authentication.
    """

    @staticmethod
    def get_access_token_header(permission_scopes: list[str]) -> dict[str, str]:
        """
        Generates an HTTP header for authenticating requests to Microsoft Graph API using a valid access token.

        Args:
            permission_scopes (list[str]):  List of required permission scopes (e.g., ['User.Read', 'Mail.Read'])

        Returns:
            dict[str, str]: HTTP-Header {'Authorization': 'Bearer <Access Token>'}
        """
        token_response = GraphAPIAuthentication.get_access_token(permission_scopes)
        access_token = token_response['access_token']
        headers = {'Authorization': 'Bearer ' + access_token}
        return headers
    

    @staticmethod
    def get_access_token(permission_scopes: list[str]) -> dict:
        """
        Retrieves an access token for the specified permission scopes. 
        Uses the cached token if available and valid; otherwise, generates a new token via the MSAL device code flow. 

        Args:
            permission_scopes (list[str]): List of required permission scopes

        Returns:
            dict: A dictionary containing the token response, including the access_token
        """
        token_cache = GraphAPIAuthentication._get_serialized_token_cache(permission_scopes)
        client = msal.PublicClientApplication(client_id=APPLICATION_ID, token_cache=token_cache)

        accounts = client.get_accounts()

        if accounts:
            token_response = client.acquire_token_silent(permission_scopes, accounts[0])
        else:
            token_response = GraphAPIAuthentication._generate_new_access_token(client=client, permission_scopes=permission_scopes)

        return token_response
    
    @staticmethod
    def _save_token_cache(token_cache: msal.SerializableTokenCache):
        with open(file_path, 'w') as f:
            f.write(token_cache.serialize())

    @staticmethod
    def _get_serialized_token_cache(permission_scopes: list[str]) -> msal.SerializableTokenCache:
        token_cache = msal.SerializableTokenCache()
        if os.path.exists(file_path) and GraphAPIAuthentication._is_token_cache_valid(permission_scopes):
            token_cache.deserialize(open(file_path, 'r').read())
        return token_cache

        
    @staticmethod
    def _is_token_cache_valid(requested_scopes: list[str]) -> bool:
        if not os.path.exists(file_path):
            return False

        try:
            # load token-cache
            token_detail = json.load(open(file_path))
            
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


    @staticmethod
    def _generate_new_access_token(client: msal.PublicClientApplication, permission_scopes: list[str]) -> dict:
            flow = client.initiate_device_flow(scopes=permission_scopes)
            
            print(flow['message'])
            webbrowser.open(flow['verification_uri'])
            
            token_response = client.acquire_token_by_device_flow(flow)
        
            GraphAPIAuthentication._save_token_cache(client.token_cache)
            
            return token_response

    