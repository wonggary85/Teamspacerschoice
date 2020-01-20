## Setup

* Install python3 and python3-pip

* (Optional) Setup virtualenv

* Install python modules with `pip install -r requirements.txt`

* Install [chromedriver](https://chromedriver.chromium.org/)
  * macOS `brew cask install chromedriver`
  * Windows https://chromedriver.chromium.org/downloads

* Execute `groundbreaker.py` once to create corresponding files to populate responses
  * Populate the files with responses

* Execute teamspacerschoice or groundbreaker once
  * Execute `teamspacerschoice.py` once to randomly schedule `groundbreaker.py` for the week
  * Alternatively, execute `groundbreaker.py` to immediately run

* (Optional) Recommended to run `teamspacerschoice.py -c` to create cronjob for teamspacerschoice

* (Optional) Recommended to run `groundbreaker.py -k` to save password in Keychain/Windows Credential Locker


## About

This is composed of two scripts, Groundbreaker.py and Teamspacerschoice.py. Groundbreaker can be used without Teamspacerschoice.

Use Groundbreaker to immediately run a single check-in. Use Teamspacerschoice to schedule a single non-recurring check-in.

The scripts only have any value to my colleagues, but can be used as reference and adapted to other things.


## Groundbreaker.py 

This script will fetch a list of pre-recorded responses in love.txt, loathe.txt, priority.txt, and help.txt, and randomly select a single response to use.

Login credentials can be stored with option '-k' or '--keychain'. The credentials is saved to the native 'Keychain Access' app in macOS or 'Windows Credential Locker' on Windows.

The script can also automatically retireve and use single use responses recorded in singleuse.txt or with CLI arguments. Single use responses take precedence over pre-recorded responses.

The first run will create the necessary files needed to populate responses.

You can add priorities that you want to include long term (such as a project) by prepending a 'lt:' before the string.

## Teamspacerschoice.py

Currently this is incompatible with Windows due to `at` and `python-crontab`.

This uses the bash `at` command. You can view jobs with `atq` command, and remove scheduled jobs with `atrm $JobID`.

Teamspacerschoice can be run once to schedule a groundbreaker.py job for the work week (Fri-Thurs). The job is a single non-recurring job (executed once). The scheduled job persists across reboots.

Ideal usage is to execute teamspacerschoice.py with the '-c' option, which will create a cron job to run teamspacerschoice.py every Fridays at 12:00 PM--which will schedule the groundbreaker.py job for the week.

Teamspacerschoice schedules jobs only between 10AM-4PM, except on Fridays between Noon and 4PM.

## Keychainz.py

Handles passwords used with Keyring/Windows Credential Locker. Not designed to be used by itself.

## gbformatter.py

Use to easily add multiple entries to singleuse.txt. 

## .env

A '.env' file can be setup with variables for the URL and chromedriver absolute path.

> url=https://example.com

> driver_path=/absolute/path/to/chromedriver

> nosubmit=True

