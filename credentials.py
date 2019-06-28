"Get OAuth credentials."

from oauth2client import file

scopes = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/admin.directory.resource.calendar.readonly",
]
store = file.Storage("credentials.json")
creds = store.get()
