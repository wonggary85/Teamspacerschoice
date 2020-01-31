#!/usr/bin/env python3
import os
import getopt
import sys
import keychainz
import selenium
import subprocess
import time
from getpass import getpass
from random import randint
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException, StaleElementReferenceException, ElementClickInterceptedException, WebDriverException

##################

"""
macos install chromedriver with `brew cask install chromedriver` and update with `brew cask upgrade chromedriver`
Windows install from https://chromedriver.chromium.org/
"""


def init_browser(url):
    chrome_options = Options()
    load_dotenv()
    if os.getenv('headless') == 'True':
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument('--enable-file-cookies')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36")
    chrome_options.add_argument(f"--app={url}")
    #chrome_options.add_argument("--kiosk")
    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities['platform'] = 'WINDOWS'
    capabilities['version'] = '10'
    if sys.platform == 'darwin':
        driver_path = "/usr/local/bin/chromedriver"
    elif os.path.exists('chromedriver.exe'):
        # Check if the driver happens to be in the same directory (primarily here for windows users)
        driver_path = os.path.abspath('chromedriver.exe')
    else:
        if os.getenv('driver_path'):
             driver_path = os.getenv('driver_path')
        else:
            # User input driver path and save to .env
            driver_path = input("Absolute path to chromedriver.exe: ").strip(' "\'\t\r\n')
            with open('.env', 'a+') as file:
                file.write(f'\n\ndriver_path={driver_path}')
    browser = webdriver.Chrome(options=chrome_options, desired_capabilities=capabilities, executable_path=driver_path)
    browser.set_window_size(1000,1000)
    return browser


def random_answer(inputFile):
    # Randomly pick an answer
    lines = []
    with open(inputFile, 'r') as file:
        for line in file:
            if 'lt:' not in line:
                lines.append(line.strip('\n'))
    pick = lines[randint(0,len(lines)-1)]
    return pick


def incl_priority(inputFile):
    lines = []
    with open(inputFile, 'r') as file:
        for line in file:
            if 'lt:' in line:
                lines.append(line.split(':', 1)[1].strip('\n'))
    return lines


def check_weekly(url, browser, user, passwd):
    browser.get(url)
    if WebDriverWait(browser, 10).until(EC.title_contains("Login Page")):
        WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.NAME, 'pf.username')))
        browser.find_element_by_name('pf.username').send_keys(user)
        browser.find_element_by_id('login-button').click()
        WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.ID, 'passwordInput')))
        browser.find_element_by_id('passwordInput').send_keys(passwd)
        browser.find_element_by_id('login-button').click()
        iframe = browser.find_element_by_tag_name('iframe')
        browser.switch_to.frame(iframe)
        try:
            WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.NAME, 'device')))
            phone = Select(browser.find_element_by_name('device'))
            phone.select_by_value('phone1')
            if 'getSMS' in dir():
                passcode = browser.find_element_by_id('passcode')
                passcode.click()
                browser.find_element_by_id('message').click()
                time.sleep(4)
                textcode = getSMS()
                browser.find_element_by_name('passcode').send_keys(textcode)
                passcode.click()
            else:
                browser.find_element_by_class_name('positive.auth-button').click()
        except (TimeoutException, NoSuchElementException):
            # Continue to next section to provide upto 30s for authentication
            pass 
        try:
            if WebDriverWait(browser, 30).until(EC.title_contains(('Team Dashboard'))) or browser.title == 'My Check-Ins':
                # Waiting up to 30s for 2FA before checking the title
                pass
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
            # Trying to reload the URL
            browser.get(url)
            pass
    if browser.title == 'Team Dashboard':
        while True:
            try:
                WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.ID, 'myhome')))
                browser.find_element_by_id('myhome').click()
                if browser.find_element_by_id('myperformance').is_displayed():
                    break
            except (StaleElementReferenceException, ElementNotInteractableException):
                if browser.title == 'Team Dashboard':
                    # Trying again since the page title is correct
                    pass
            except TimeoutException:
                print(f"myhome not found. Re-check your URL: {url}")
        while True:
            try:
                WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.ID, 'myperformance')))
                browser.find_element_by_id('myperformance').click()
                if browser.title == 'My Check-Ins':
                    break
            except TimeoutException:
                # Trying again
                pass
    if browser.title == 'My Check-Ins':
        try:
            WebDriverWait(browser, 10).until(EC.title_contains("My Check-Ins"))
        except NoSuchElementException:
            print("Unable to reach check-ins. Check your URL.\nQuitting.")
            exit()
    try:
        WebDriverWait(browser, 15).until(EC.element_to_be_clickable((By.ID, 'checkinLauncher')))
    except (NoSuchElementException, TimeoutException):
        print("No Login or Check-in found. Was it already completed?\nQuitting.")
        exit()
    button = browser.find_element_by_class_name('button').click()
    return browser


def next_page():
    WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, 'nextButton.pageButton')))
    browser.find_element_by_class_name('nextButton.pageButton').click()

 
def submit_weekly(love, loathe, priority, help, browser):
    """Steps through the check-in and randomly sets engagement/value ratings within an average-excellent range.
    Randomly set engagement/value between 3-5.
    Responsible for stepping through the check-in.
    Calls function submit_textbox to handle the text inputs for each category.
    """

    WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "cirating.engagementrating")))
    for strperf in ["cirating.engagementrating", "cirating.valuerating"]:
        while True:
            try:
                WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, strperf)))
                browser.find_elements_by_class_name(strperf)[randint(2,4)].click()
                break
            except NoSuchElementException:
                if (browser.find_element_by_class_name('cirating.engagementrating').is_displayed() or browser.find_element_by_class_name('cirating.valuerating').is_displayed()):
                    # May not have been ready, trying again
                    pass
    next_page()

    # Submit loved responses
    inputLove = ['class_name', 'input.strText']
    submit_textbox(love, inputLove)

    # Submit loathed responses
    inputLoathe = ['class_name', 'input.weakText']
    submit_textbox(loathe, inputLoathe)
    next_page()

    # Existing priorities
    # Currently not carrying over previous priorities to avoid having duplicate entries if a randomly selected response is the same
    try:
        if browser.find_element_by_id('prev-goals-page').is_displayed():
            browser.find_element_by_class_name('nextButton.pageButton').click()
    except NoSuchElementException:
        # You probably didn't put in priorities last week since this was not found
        pass

    # Submit priorities
    if browser.find_elements_by_class_name('icon-trash-bin.goaloption.removegoal'):
        remove_goals()
    inputPri = ['id', 'dlt-goalinput']
    submit_textbox(priority, inputPri)
    next_page()

    # Submit help responses
    inputHelp = ['class_name', 'input.needinput']
    submit_textbox(help, inputHelp)
    if os.getenv('nosubmit') == 'True':
        print("Not submitting")
        pass
    else:
        browser.find_element_by_class_name('button.pageButton.finishButton').click()
        print("Submitting")


def submit_textbox(responseList, selection):
    """Handles each category of text input.
    responseList is self explainatory.
    Selection is a list composed of the type of element we are searching for, and the string we are searching for.
    The text box is cleared before input, in case any output is saved from a previously unsubmitted check-in that failed for whatever reason.
    """

    if selection[0] == 'class_name':
        textbox = browser.find_element_by_class_name(selection[1])
        WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, selection[1])))
    elif selection[0] == 'id':
        textbox = browser.find_element_by_id(selection[1])
        WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.ID, selection[1])))
    textbox.clear()
    for line in responseList:
        textbox.send_keys(line.strip('\n'))
        if selection[1] == 'dlt-goalinput':
            browser.find_element_by_id('dlt-addgoalbtn').click()
        elif len(responseList) > 1:
            ActionChains(browser).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER).perform()


def remove_goals():
    """Removes existing goals entered for the week.
    Ideally there should be nothing to remove since it is a clean slate for the week.
    If for whatever reason the check-in was aborted, it will remove existing entries to avoid duplicates.
    The bulk of the function resides within a while loop, which was needed in cases where an extremely large number of priorities was entered would always trigger an exception (in real world usage, this should never occur).
    """
    savedpris = browser.find_elements_by_class_name('icon-trash-bin.goaloption.removegoal')
    while True:
        for priority in savedpris:
            try:
                WebDriverWait(browser, 3).until(EC.element_to_be_clickable((By.CLASS_NAME, 'icon-trash-bin.goaloption.removegoal')))
                priority.click()
                element = WebDriverWait(browser, 3).until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-small.button.msg-ok-btn')))
                #browser.find_element_by_class_name('btn-small.button.msg-ok-btn').click()
                element.click()
            except (StaleElementReferenceException, TimeoutException, ElementNotInteractableException):
                pass
            except ElementClickInterceptedException:
                try:
                    if browser.find_element_by_class_name('btn-small.button.msg-ok-btn').is_displayed():
                        element.click()
                    elif browser.find_element_by_class_name('icon-trash-bin.goaloption.removegoal').is_displayed():
                        pass
                except NoSuchElementException:
                    pass
        savedpris = browser.find_elements_by_class_name('icon-trash-bin.goaloption.removegoal')
        if len(savedpris) == 0:
            break
        else:
            pass


def reset_single_include(file):
    with open(file, 'w+') as infile:
        for category in ['love', 'loathe', 'priority', 'help']:
            infile.write(f"{category}:\n")
    print(f"Cleared {file} entries.")

def check_quit():
    while True:
        close_browser = input("Close all windows (Y|N)? ")
        if close_browser.lower() in ('y', 'yes'):
            try:
                browser.close()
                break
            except WebDriverException:
                break


def get_single_include(file):
    love = []
    loathe = []
    priority = []
    help = []
    if os.path.exists(file):
        if sys.platform == 'win32':
            cmd = f"CertUtil -hashfile {file} MD5 | find /i /v \"MD5\" | find /i /v \"certutil\""  # Windows find tool requires search string to be enclosed in double quotes
        else:
            cmd = "md5sum %s | awk '{print $1}'" % file
        if '8810610524679e08dbaa38c96ac4a3af' not in subprocess.getoutput(cmd):
            with open(file, 'r') as singleinclude:
                for line in singleinclude:
                    category = line.split(':', 1)
                    try:
                        if len(category[1]) > 1:
                            if category[0] == 'love':
                                love.append(category[1])
                            elif category[0] == 'loathe':
                                loathe.append(category[1])
                            elif category[0] == 'priority':
                                priority.append(category[1])
                            elif category[0] == 'help':
                                help.append(category[1])
                    except IndexError:
                        pass
            singleinclude = True
            uberlist = [love, loathe, priority, help]
            return uberlist, singleinclude
    else:
        reset_single_include(file)


def check_file_hash(file):
    if os.path.exists(file):
        if sys.platform == 'win32':
            cmd = f"CertUtil -hashfile {file} MD5 | find /i /v \"MD5\" | find /i /v \"certutil\""  # Windows find tool requires search string to be enclosed in double quotes
        else:
            cmd = "md5sum %s | awk '{print $1}'" % file
        if '8810610524679e08dbaa38c96ac4a3af' not in subprocess.getoutput(cmd):
            return True
        else:
            return False
    else:
        reset_single_include(file)
        return False


def printHelp():
    print("-k | --keychain:\tStores your password (Keychain on macOS or Windows Credential Locker on Windows)")
    print("-l | --love:\tSpecify a single use string")
    print("-d | --dislike:\tSpecify a single use string")
    print("-p | --priority:\tSpecify a single use string")
    print("-n | --need:\tSpecify a single use string")


def main(argv):
    """
    -Helper TeamSpacersChoice Scheduler creates a job (persists across reboots)
    -When Scheduler is run on Fridays, it will randomly pick a workday to run Groundbreaker teamspacerschoice and create a cronjob
    -Login
    -Check if weekly checkin was done (in case it was manually done)
    -If not manually specified, teamspacerschoice will randomly pick from random pre-prepared responses you created
    """

    global browser
    user = os.getlogin()
    love = []
    loathe = []
    priority = []
    help = []
    included = []
    singleuse = 'singleuse.txt'
    singleinclude = 'include.txt'

    load_dotenv()
    if os.getenv('url'):
        url = os.getenv('url')
    else:
        url = input("URL: ")

    if check_file_hash(singleuse):
        uberlist, singleuse = get_single_include(singleuse)
        love += uberlist[0]
        loathe += uberlist[1]
        priority += uberlist[2]
        help += uberlist[3]
    else:
        singleuse = False

    if os.path.exists('love.txt') and os.path.exists('loathe.txt') and os.path.exists('priority.txt') and os.path.exists('help.txt'):
        if singleuse == False:
            if os.path.getsize('love.txt') > 0:
                love.append(random_answer('love.txt'))
            if os.path.getsize('loathe.txt') > 0:
                loathe.append(random_answer('loathe.txt'))
            if os.path.getsize('priority.txt') > 0:
                priority.append(random_answer('priority.txt'))
            if os.path.getsize('help.txt') > 0:
                help.append(random_answer('help.txt'))
            if check_file_hash(singleinclude):
                uberlist, singleinclude = get_single_include(singleinclude)
                love += uberlist[0]
                loathe += uberlist[1]
                priority += uberlist[2]
                help += uberlist[3]
            else:
                singleinclude = False
    else:
        for file in ['love.txt', 'loathe.txt', 'priority.txt', 'help.txt']:
            if not os.path.exists(file):
                print(f"File {file} does not exist. Creating {file}.")
                tmp = open(file, 'w+')
                tmp.close()
        print("Populate responses, separated by newline.\nExiting.")
        exit()

    try:
        opts,args = getopt.getopt(sys.argv[1:], 'khl:d:p:n:',['love=', 'dislike=', 'priority=', 'need='])
    except Exception as err_msg:
        print(err_msg)
        exit()
    for opt,arg in opts:
        if opt in ('-k', '--keychain'):
            passwd = keychainz.set_creds(__file__)
        elif opt in ('-h', '--help'):
            printHelp()
            pass
        elif singleuse == False:
            if opt in ('-l', '--love'):
                love = []
                love.append(arg.strip(' "\'\t\r\n'))
            elif opt in ('-d', '--dislike'):
                loathe = []
                loathe.append(arg.strip(' "\'\t\r\n'))
            elif opt in ('-p', '--priority'):
                priority = []
                priority.append(arg)
            elif opt in ('-n', '--need'):
                help = []
                help.append(arg)
    
    included = incl_priority('priority.txt')
    if len(included) > 0:
        priority += included

    if keychainz.get_creds(__file__):
        passwd = keychainz.get_creds(__file__)
    else:
        try:
            passwd = getpass(prompt="\nPassword: ")
        except KeyboardInterrupt:
            exit()

    browser = init_browser(url)
    browser = check_weekly(url, browser, user, passwd)
    submit_weekly(love, loathe, priority, help, browser)
    if singleuse == True:
        print("Clearing singleuse.txt.")
        reset_single_include('singleuse.txt')
    if singleinclude == True:
        print("Clearing include.txt.")
        reset_single_include('include.txt')
    check_quit()
    exit()


if __name__=="__main__":
    load_dotenv()
    try:
        if os.getenv('sms') == 'gvoice':
            from SMS.sms_gv import getSMS
        elif os.getenv('sms') == 'twilio':
            from SMS.sms_twilio import getSMS
    except ModuleNotFoundError:
        print(f"Unable to import module: {ModuleNotFoundError}.\nContiuning without SMS capabilities.")
        pass
    main(sys.argv[1:])
