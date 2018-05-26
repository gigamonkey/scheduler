"Get OAuth credentials."

from oauth2client import file

scopes = 'https://www.googleapis.com/auth/calendar'
store  = file.Storage('credentials.json')
creds  = store.get()
