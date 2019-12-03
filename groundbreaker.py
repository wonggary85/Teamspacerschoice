#!/usr/bin/env python
import getpass
import os
import getopt
import sys
import keychainz
import selenium
import subprocess
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
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import WebDriverException

"""
macos install chromedriver with `brew cask install chromedriver`
windows you're on your own
"""

##################

def initBrowser():
    chrome_options = Options()
    load_dotenv()
    if os.getenv('headless') == True:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument('--enable-file-cookies')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36")
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
            file = open('.env', 'a+')
            file.write(f'\n\ndriver_path={driver_path}')
            file.close()
    browser = webdriver.Chrome(options=chrome_options, desired_capabilities=capabilities, executable_path=driver_path)
    return browser

def randomAnswer(inputFile):
    # Randomly pick an answer
    lines = []
    with open(inputFile, 'r') as file:
        for line in file:
            lines.append(line.strip('\n'))
    pick = lines[randint(0,len(lines)-1)]
    return pick

def check_Weekly(url, browser, user, passwd):
    page = False
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
        phone = Select(browser.find_element_by_name('device'))
        phone.select_by_value('phone1')
        browser.find_element_by_class_name('positive.auth-button').click()
        WebDriverWait(browser, 30).until(EC.title_contains("Team Dashboard"))
        browser.get(url)
    try:
        WebDriverWait(browser, 10).until(EC.title_contains("My Check-Ins"))
    except NoSuchElementException:
        print("No Login or Check-in found.")
        exit()
    WebDriverWait(browser, 15).until(EC.element_to_be_clickable((By.ID, 'checkinLauncher')))
    button = browser.find_element_by_class_name('button').click()
    return browser

def nextPage():
    WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, 'nextButton.pageButton')))
    browser.find_element_by_class_name('nextButton.pageButton').click()
 
def submit_Weekly(love, loathe, priority, help, browser):
    """
    Randomly set Strength/Performance between 3-5.
    Input text for love/loathe is selected randomly in their respective text files, one response occupies one line.
    """

    WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "cirating.engagementrating")))
    for strperf in ["cirating.engagementrating", "cirating.valuerating"]:
        try:
            browser.find_elements_by_class_name(strperf)[randint(2,4)].click()
        except NoSuchElementException:
            print("Engagement/Value selection not found.")
            exit()
    nextPage()

    # Submit loved responses
    inputLove = ['class_name', 'input.strText']
    submit_textbox(love, inputLove)

    # Submit loathed responses
    inputLoathe = ['class_name', 'input.weakText']
    submit_textbox(loathe, inputLoathe)
    nextPage()

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
    nextPage()

    # Submit help responses
    inputHelp = ['class_name', 'input.needinput']
    submit_textbox(help, inputHelp)
    nosubmit = os.getenv('nosubmit')
    if nosubmit == True:
        print("Not submitting")
        pass
    else:
        #browser.find_element_by_class_name('button.pageButton.finishButton').click()
        print("Submitting")

def submit_textbox(responseList, selection):
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
            continue

def resetSingleUse():
    with open('singleuse.txt', 'w') as singleuse:
        for category in ['love', 'loathe', 'priority', 'help']:
            singleuse.write(f"{category}:\n")

def check_quit():
    while True:
        close_browser = input("Close all windows (Y|N)? ")
        if close_browser.lower() in ('y', 'yes'):
            try:
                browser.close()
                break
            except WebDriverException:
                break

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
    singleuse = False
    love = []
    loathe = []
    priority = []
    help = []

    load_dotenv()
    if os.getenv('url'):
        url = os.getenv('url')
    else:
        url = input("URL: ")

    if os.path.exists('love.txt') and os.path.exists('loathe.txt') and os.path.exists('priority.txt') and os.path.exists('help.txt'):
        if os.path.getsize('love.txt') > 0:
            love.append(randomAnswer('love.txt'))
        if os.path.getsize('loathe.txt') > 0:
            loathe.append(randomAnswer('loathe.txt'))
        if os.path.getsize('priority.txt') > 0:
            priority.append(randomAnswer('priority.txt'))
        if os.path.getsize('help.txt') > 0:
            help.append(randomAnswer('help.txt'))
    else:
        for file in ['love.txt', 'loathe.txt', 'priority.txt', 'help.txt']:
            if not os.path.exists(file):
                print(f"File {file} does not exist. Creating {file}.")
                tmp = open(file, 'w+')
                tmp.close()
        print("Populate responses, separated by newline.\nExiting.")
        exit() 

    if os.path.exists('singleuse.txt'):
        if not subprocess.getoutput("md5sum singleuse.txt | awk '{print $1}'") == '8810610524679e08dbaa38c96ac4a3af':
            with open('singleuse.txt', 'r') as singleuse:
                love = []
                loathe = []
                priority = []
                help = []
                for line in singleuse:
                    category = line.split(':')
                    if len(category[1]) > 2:
                        if category[0] == 'love':
                            love.append(category[1])
                        elif category[0] == 'loathe':
                            loathe.append(category[1])
                        elif category[0] == 'priority':
                            priority.append(category[1])
                        elif category[0] == 'help':
                            help.append(category[1])
            singleuse = True
    else:
        resetSingleUse()

    if os.path.exists('love.txt') and os.path.exists('loathe.txt') and os.path.exists('priority.txt') and os.path.exists('help.txt'):
        if singleuse == False:
            love = set()
            loathe = set()
            priority = set()
            help = set()
            if os.path.getsize('love.txt') > 0:
                love.add(randomAnswer('love.txt'))
            if os.path.getsize('loathe.txt') > 0:
                loathe.add(randomAnswer('loathe.txt'))
            if os.path.getsize('priority.txt') > 0:
                priority.add(randomAnswer('priority.txt'))
            if os.path.getsize('help.txt') > 0:
                help.add(randomAnswer('help.txt'))
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
            passwd = keychainz.setCreds(__file__)
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

    if keychainz.getCreds(__file__):
        passwd = keychainz.getCreds(__file__)
    else:
        try:
            passwd = getpass.getpass(prompt="\nPassword: ")
        except KeyboardInterrupt:
            exit()

    browser = initBrowser()
    browser = check_Weekly(url, browser, user, passwd)
    submit_Weekly(love, loathe, priority, help, browser)
    if singleuse == True:
        print("Clearing singleuse.txt.")
        resetSingleUse()
    check_quit()
    exit()

if __name__=="__main__":
    main(sys.argv[1:])
