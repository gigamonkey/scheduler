# scheduler

Code for scheduling meetings on Google calendar.

Once you've got a `client_secrets.json` from the Google API console. (I don't really 
understand this part but have cargo culted it a few times now.) you can run:

```
./get_credentials
```

to go through the OAuth dance via your web browser to let the app access your calendar.

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
