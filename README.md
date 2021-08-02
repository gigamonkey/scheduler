# scheduler

Code for scheduling multiple meetings on Google calendar, finding a
schedule for all the meetings taking into account everyone's current
calendar and the need to not schedule conflicting meetings.

Once you've got a `client_secrets.json` from the Google API console you can run:

```
./get_credentials
```

to go through the OAuth dance via your web browser to let the app access your
calendar. Instructions for obtaining a `client_secrets.json` are at
https://support.google.com/googleapi/answer/6158849.

Then run:

```
./schedule meetings.txt
```

to see when it would schedule the meetings where `meetings.txt` is a
file containing one meeting per line in the format:

```
[30] A meeting name: harry@example.com, sally@example.com
[60] Another meeting name: sally@example.com, linda@example.com, bobby@example.com
```

The number in brackets is the duration in minutes of the meeting, the
text up to the colon is the title of the meeting, and everything after
the colon is a comma-delimited list of attendees.

Run:

```
./schedule --calendar sally@example.com meetings.txt
```

Where `sally@example.com` is the calendar you want to schedule on
(presumably yours) to actually schedule them on people's calendars.
