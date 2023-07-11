Right now, without using AWS Step Functions, this is how I see our current set of scripts working:

## User requests restore of files from AWS Glacier

Start EC2 instance in the free tier
	(background process to send notification every 24 hours that instance is running)

Git pull to retrieve code.
```
./scripts/bucket-halt-changes <user> <host>

./scripts/athena-setup.py <user> <host>

./scripts/athena-query-from-file.py <user> <host> <file with list of files to restore>

./scripts/athena-query-job-status.py <user> <host> <output from previous command>
	loop here until successful or errors
	(manual cleanup after investigation)
```
If errors, halt and send notification to rcic-admin
```
./scripts/athena-teardown.py <user> <host>

./scripts/glacier-restore-from-file.py <user> <host> <output from athena-query-job-status.py>

./scripts/glacier-query-job-status.py <user> <host> <output from previous command>
	loop here until successful or errors
	(manual cleanup after investigation)
```
If errors, halt and send notification to rcic-admin

Send notification to user and delete EC2 instance


## User invokes rclone to retrieve files

This occurs on user's machine.


## After user confirms that they recovered all files
```
./scripts/bucket-resume-changes.py <user> <host>
```
