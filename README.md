# scheduler

Code for scheduling meetings on Google calendar.

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

or

```
cat calendars.txt | ./schedule
```

where `meetings.txt` is a file containing one meeting per line in the format:

```
A meeting name: harry@example.com, sally@example.com
Another meeting name: sally@example.com, linda@example.com, bobby@example.com
```

The program will find a schedule for all the meetings taking into account
everyone's current calendar and the need to not schedule conflicting meetings.
