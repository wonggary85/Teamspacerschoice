#!/usr/bin/env python
import getpass
import os
import getopt
import sys
import random
import keyring
import selenium
import subprocess
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

"""
macos install chromedriver with `brew cask install chromedriver`
windows you're on your own
"""

##################

def initBrowser():
    chrome_options = Options()
    #if headless:
        #chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument('--enable-file-cookies')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36")
    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities['platform'] = 'WINDOWS'
    capabilities['version'] = '10'
    if sys.platform == 'darwin':
        driver_path = "/usr/local/bin/chromedriver"
    else:
        driver_path = input("Path to chromedriver.exe: ").strip(' "\'\t\r\n')
    browser = webdriver.Chrome(options=chrome_options, desired_capabilities=capabilities, executable_path=driver_path)
    return browser

def insertCreds(url,user,passwd):
    urlCreds = user + ":" + passwd + "@"
    url = url[:8] + urlCreds + url[8:]
    return url

def randomAnswer(inputFile):
    lines = []
    with open(inputFile, 'r') as file:
        for line in file:
            lines.append(line)
    pick = lines[random.randint(0,len(lines)-1)]
    return pick    

def keychainz():
    keyring.set_password("groundbreaker", os.getlogin(), getpass.getpass(prompt="Password: "))
    print("Saved in keyring!\nRestart script.\n")
    exit()

def check_Weekly(url, browser, user, passwd):
    page = False
    #browser = initBrowser()
    browser.get(url)
    if WebDriverWait(browser, 10).until(EC.title_contains("Login Page")):
        WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.NAME, 'pf.username')))
        browser.find_element_by_name('pf.username').send_keys(user)
        browser.find_element_by_id('login-button').click()
        WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.ID, 'passwordInput')))
        browser.find_element_by_id('passwordInput').send_keys(passwd)
        passwd = ""
        browser.find_element_by_id('login-button').click()
        WebDriverWait(browser, 30).until(EC.title_contains("Team Dashboard"))
        browser.get(url)
    elif WebDriverWait(browser, 10).until(EC.title_contains("My Check-Ins")):
        pass
    else:
        print("No Login or Check-in found.")
        exit()
    WebDriverWait(browser, 15).until(EC.element_to_be_clickable((By.ID, 'checkinLauncher')))
    button = browser.find_element_by_class_name('button').click()
    return browser
 
def submit_Weekly(love, loathe, priority, help, browser):
    """
    Randomly set Strength/Performance between 3-5.
    Input text for love/loathe is selected randomly in their respective text files, one response occupies one line.
    """
    strength = random.randint(2,4)
    performance = random.randint(2,4)
    button = WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "cirating.engagementrating")))
    browser.find_elements_by_class_name("cirating.engagementrating")[strength].click()
    browser.find_elements_by_class_name("cirating.valuerating")[performance].click()
    browser.find_element_by_class_name('nextButton.pageButton').click()

    # Loved responses
    WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "input.strText")))
    browser.find_element_by_class_name("input.strText").clear()
    inputLove = browser.find_element_by_class_name("input.strText")
    #inputLove.send_keys(love)
    submit_text(love, inputLove)

    # Loathed responses
    browser.find_element_by_class_name("input.weakText").clear()
    inputLoathe = browser.find_element_by_class_name("input.weakText")
    #inputLoathe.send_keys(loathe)
    submit_text(loathe, inputLoathe)
    browser.find_element_by_class_name('nextButton.pageButton').click()

    # Priorities
    
    browser.find_element_by_class_name('nextButton.pageButton').click()
    
    # Help responses

    browser.find_element_by_class_name('button.pageButton.finishButton').click()
    print("Submitting")

def submit_text(responseList, textbox):
    for line in response:
        textbox.send_keys(line.strip('\n')
        if len(response) > 1:
            ActionChains(browser).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER).perform()

def resetSingleUse():
    with open('singleuse.txt', 'w') as singleuse:
        for category in ['love', 'loathe', 'priority', 'help']:
            singleuse.write("%s:\n" % category)
 
def check_quit():
    while True:
        close_browser = input("Close all windows (Y|N)? ")
        if close_browser.lower() in ('y', 'yes'):
            browser.close()
            return

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
                print("File %s does not exist. Creating %s." % (file, file))
                tmp = open(file, 'w+')
                tmp.close()
        print("Populate responses, separated by newline.\nExiting.")
        exit() 

    if os.path.exists('singleuse.txt'):
        if not subprocess.getoutput("md5sum singleuse.txt | awk '{print $1}'") == '8810610524679e08dbaa38c96ac4a3af':
            with open('singleuse.txt', 'r') as singleuse:
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

    try:
        opts,args = getopt.getopt(sys.argv[1:], 'khl:d:p:n:',['love=', 'dislike=', 'priority=', 'need='])
    except Exception as err_msg:
        print(err_msg)
        exit()
    for opt,arg in opts:
        if opt in ('-k', '--keychain'):
            keychainz()
        elif opt in ('-h', '--help'):
            #printHelp()
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

    if keyring.get_password("groundbreaker", user):
        passwd = keyring.get_password("groundbreaker", user)
    else:
        try:
            passwd = getpass.getpass(prompt="\nPassword: ")
        except KeyboardInterrupt:
            exit()

    browser = initBrowser()
    browser = check_Weekly(url, browser, user, passwd)
    submit_Weekly(love, loathe, priority, help, browser)
    if singleuse == True:
        resetSingleUse()
    check_quit()
    exit()

if __name__=="__main__":
    main(sys.argv[1:])
    load_dotenv()
