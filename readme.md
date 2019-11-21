Usage

This is composed of two scripts, Groundbreaker.py and Teamspacerschoice.py. Groundbreaker can be used without Teamspacerschoice.

Use Groundbreaker to immediately run a single check-in. Use Teamspacerschoice to schedule a single non-recurring check-in.

Groundbreaker.py 
    This script will fetch a list of pre-recorded responses in love.txt, loathe.txt, priority.txt, and help.txt, and randomly select a single response to use.

    Login credentials can be stored with option '-k' or '--keychain'. The credentials is saved to the native 'Keychain Access' app in macOS or 'Windows Credential Locker' on Windows.

    The script can also use single use responses with CLI arguments or recorded in singleuse.txt. Singleuse responses take precedence over pre-recorded responses.

Teamspacerschoice.py
    This uses the bash 'at' command. You can view jobs with 'atq' command, and remove scheduled jobs with 'atrm $JobID'.

    Teamspacerschoice can be run once to schedule a groundbreaker.py job. The job is a single non-recurring job (executed once). The scheduled job persists across reboots.

    Ideal usage is to execute teamspacerschoice.py with the '-c' option, which will create a cron job to run teamspacerschoice.py every Fridays at 12:00 PM--which will schedule the groundbreaker.py job for the week.

    Teamspacerschoice schedules jobs only between 10AM-4PM, except on Fridays between Noon and 4PM.
