import webbrowser
import msal
from msal import PublicClientApplication

APPLICATION_ID = '792e4432-f94f-4e9a-ae07-d4d155c30a9c'
authority_url = 'https://login.microsoftonline.com/consumers/'

class GraphAPIAuthentication:

    @staticmethod
    def get_access_token_header(permission_scopes: list[str]) -> dict[str, str]:
        # or take existing access_token from session management
        access_token = GraphAPIAuthentication.get_new_access_token(permission_scopes)
        headers = {'Authorization': 'Bearer ' + access_token}
        return headers

    @staticmethod
    def get_new_access_token(permission_scopes: list[str]) -> str:
        app = PublicClientApplication(APPLICATION_ID, authority= authority_url)
        flow = app.initiate_device_flow(scopes=permission_scopes)
        print(flow['message'])
        webbrowser.open(flow['verification_uri'])
        result = app.acquire_token_by_device_flow(flow)
        acces_token = result['access_token']
        return acces_token