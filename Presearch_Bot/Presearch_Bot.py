# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import ui
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from configuration import config
from datetime import datetime
from time import sleep
import random
import os
import pickle

#  Initialization
words = open("ExtraFiles//words.txt", "r").readlines()

#  Setting up chrome
user_data_path = '/home/username/.config/google-chrome'.format(os.getlogin())
profile_name = "Profile " + str(config["profile_number"])

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument('--user-data-dir=' + user_data_path)
options.add_argument('--profile-directory=' + profile_name)
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
driver.execute_script('return navigator.userAgent')
driver.maximize_window()


def page_loaded(driver):
	return driver.find_element(By.TAG_NAME, 'body') != None


def login():
    try:
        #Position yourself on the main page of Presearch
        driver.get("https://account.presearch.com/")
        wait = ui.WebDriverWait(driver, 10)
        wait.until(page_loaded)

        #Check if exists a file with cookies
        if os.path.exists("ExtraFiles//cookies.pkl"):

            #SeIf there are cookies, use them to log into your Presearch account
            if login_with_cookies():
                return True

        sleep(5)

        accounts_data = open("ExtraFiles//accounts.txt", "r").readlines()
        accounts = {}
        for account in accounts_data:
            account_splited = account.split(":", maxsplit=1)
            # Extract Email and Password from accounts.txt
            email = account_splited[0].strip()
            password = account_splited[1].strip()

            if email != "" and password !="":
                break
    
        #Fill Email
        email_input = driver.find_element(By.XPATH, '//input[@name="email"]')
        email_input.send_keys(email)
        
        #Fill Password
        password_input = driver.find_element(By.XPATH, '//input[@name="password"]')
        password_input.send_keys(password)

        #Check the "Remember Me" checkbox
        driver.find_element(By.XPATH, '//input[@name="remember"]').click()

        #Open the challenge to prove you're not a robot
        driver.find_element(By.XPATH, '//*[@id="login-form"]/form/div[3]/div[2]/div/iframe').click()

        print('Press Enter after proving you´re not a robot: ')
        input()
    
        #Click in Login button
        driver.find_element(By.XPATH, '//*[@id="login-form"]/form/div[3]/div[3]/button').click()

        #Position yourself on your Presearch profile page
        driver.get("https://account.presearch.com/")
        wait = ui.WebDriverWait(driver, 10)
        wait.until(page_loaded)

        #Save cookies so you don't have to log in again next time
        pickle.dump(driver.get_cookies() , open("ExtraFiles//cookies.pkl","wb"))
    
        #Return your login state
        return check_is_logged_in()

    except:
        print ("\n\nSomething went wrong!\nPlease re-run the bot to try again")
        return


def login_with_cookies():
    try:
        #Apply cookies
        cookies = pickle.load(open("ExtraFiles//cookies.pkl", "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
    
        #Position yourself on your Presearch profile page
        driver.get("https://account.presearch.com/")
        wait = ui.WebDriverWait(driver, 10)
        wait.until(page_loaded)
    
        #Return your login state
        return check_is_logged_in()
    except:
        print ("\n\nSomething went wrong!\nPlease re-run the bot to try again")
        return

def check_is_logged_in():
    #Check if you is logged in
    if driver.current_url == "https://account.presearch.com/":
        return True

def check_day_searchs():
    try:
        #Page where we have the list of daily searches.
        link = "https://account.presearch.com/tokens/usage-rewards?page=3"
        driver.get(link)
        wait = ui.WebDriverWait(driver, 10)
        wait.until(page_loaded)

        #Get a date from 25 searches, if it is equal to today's date, we have all daily searches completed
        search_date = driver.find_element(By.XPATH, '//*[@id="main"]/table/tbody/tr[5]/td[1]').text
        search_date = search_date[0 : search_date.index(' ')]
        today_date = datetime.today().strftime('%Y-%m-%d')

        if search_date == today_date:
            print("\n\nAll 25 paid daily searches had already been performed.\nCome back again tomorrow.")
            return True

    except:
        print ("\n\nSomething went wrong!\nPlease re-run the bot to try again")
        return


def loop_search():
    try:
        #Get a word and search for it
        link = "https://engine.presearch.org/search?q=" + random.choice(words).strip()
        driver.get(link)

        #Search for words randomly or in order in the file.
        if config["random"]:
            for i in range(0, config["searches_count"]):
                word = random.choice(words).strip()

                if not search(word):
                    return
                
                print("Searched for " + word)
                sleep(max(config["delay"], 2))
        else:
            for word in words:
                word = word.strip()

                if not search(word):
                    return

                print("Searched for " + word)
                sleep(max(config["delay"], 2))

        print("\n\nAll surveys have been completed!\nIf you didn't get the maximum daily reward, run the bot again.")
    except:
        print ("\n\nSomething went wrong!\nPlease re-run the bot to try again")
        return


def search(word):
    try:
        search_bar = driver.find_element(By.NAME, "q")
        search_bar.clear()
        search_bar.send_keys(word)
        search_bar.submit()

        return True
    except:
        print ("\n\nSomething went wrong!\nPlease re-run the bot to try again")
        return False
        
def get_reward_tokens():
    #Position yourself on the main page of Presearch
    link = "https://account.presearch.com/"
    driver.get(link)
    wait = ui.WebDriverWait(driver, 10)
    wait.until(page_loaded)

    reward_tokens = driver.find_element(By.XPATH, '//*[@id="main"]/div[2]/div/div[2]/div[2]/a[2]/span/span').text
    print("\nYou have collected " + reward_tokens + " Usage Reward Tokens.\n\n")


#If you is logged in do research
if login():
    #It will do the daily searches only if they are not all done yet.
    if not check_day_searchs():
        loop_search()

    get_reward_tokens()


else:
    if os.path.exists("ExtraFiles//cookies.pkl"):
        os.remove("ExtraFiles//cookies.pkl")

    print("\n\nUnable to login to your Presearch account, please re-run the bot to try to login.")

driver.close()
