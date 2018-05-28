# scheduler

Code for scheduling meetings on Google calendar.

Once you've got a `client_secrets.json` from the Google API console you can run:

```
./get_credentials
```

to go through the OAuth dance via your web browser to let the app access your calendar. Instructions for obtaining a `client_secrets.json` are at https://support.google.com/googleapi/answer/6158849.

Then run:

```
./schedule calendars.txt
```

or

```
cat calendars.txt | ./schedule
```

where `calendars.txt` is a file containing one email addresses per line. The program will
find a schedule of 1:1s for the first person listed in the file with every other person
in the file.
