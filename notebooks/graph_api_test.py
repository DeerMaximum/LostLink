import webbrowser
import requests
import msal
from msal import PublicClientApplication

APPLICATION_ID = '792e4432-f94f-4e9a-ae07-d4d155c30a9c'
authority_url = 'https://login.microsoftonline.com/consumers/'
base_graph_request_url = 'https://graph.microsoft.com/v1.0/'

SCOPES = ['User.Read', 'Files.Read']        # needed permissions

app = PublicClientApplication(APPLICATION_ID, authority= authority_url)

flow = app.initiate_device_flow(scopes=SCOPES)
print(flow['message'])
webbrowser.open(flow['verification_uri'])

result = app.acquire_token_by_device_flow(flow)
acces_token_id = result['access_token']
headers = {'Authorization': 'Bearer ' + acces_token_id}

#graph_request_url = base_graph_request_url + 'me'
# graph_request_url = base_graph_request_url + '/me/drive/search(q=\'.pdf\')'
graph_request_url = base_graph_request_url + '/me/drive/root/delta'

response = requests.get(graph_request_url, headers=headers)

json = response.json()["value"]
print(response.json()["@odata.deltaLink"])

for entry in json:
    print('name: ', entry['name'], 'lastModified: ', entry['lastModifiedDateTime'])
    # download_url = entry['@microsoft.graph.downloadUrl']
    # download_response = requests.get(download_url)
    # with open(f"file-downloads/{entry['name']}", mode="wb") as file:
    #     file.write(download_response.content)
