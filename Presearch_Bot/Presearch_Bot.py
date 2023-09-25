# -*- coding: utf-8 -*-
from ast import Global
from asyncio.windows_events import NULL
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import ui
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from configuration import config
from datetime import datetime
from time import sleep
import random
import os
import pickle
import requests

#  Initialization
words = open("ExtraFiles//words.txt", "r").readlines()
proxies_list = []
driver = None


def setting_up_webdriver(proxy):
    print ("Please wait while the Webdriver is configured...")

    #  Setting up chrome
    user_data_path = '/home/username/.config/google-chrome'.format(os.getlogin())
    profile_name = "Profile " + str(config["profile_number"])

    options = webdriver.ChromeOptions()

    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    if proxy:
        options.add_argument('--proxy-server=%s' % proxy)

    options.add_argument('--user-data-dir=' + user_data_path)
    options.add_argument('--profile-directory=' + profile_name)
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.execute_script('return navigator.userAgent')
    driver.maximize_window()

    return driver


def page_loaded(driver):
	return driver.find_element(By.TAG_NAME, 'body') != None


def get_list_proxies():
    try:
        print ("Getting a list of proxies...")

        # Search the website free-proxy-list.net
        response = requests.get("https://free-proxy-list.net/")
        soup = BeautifulSoup(response.text, 'html.parser')

        for row in soup.find("table").find_all("tr")[1:]:
            cells = row.find_all("td")
            try:                
                ip = cells[0].get_text().strip()
                port = cells[1].get_text().strip()
                proxy = f"{ip}:{port}"
                proxies_list.append(proxy)
            except:
                continue
        return proxies_list

    except:
        print ("\n\nget_list_proxies() - An error occurred while trying to create a list of proxies to use for the bot.")
        return


def test_proxy(proxy_url):
    try:
        #Test the proxy by making a request to the httpbin.org site
        proxyDict = {  
              "http" : proxy_url ,
              "https" : proxy_url 
            }

        try:
            response = requests.get('https://www.google.com/', timeout = 3, proxies = proxyDict)
        except:
            print ("Proxy '%s` is not valid." % proxy_url)
            return False

        if response.status_code == 200:
            print ("Proxy '%s` is valid and will be used by the bot." % proxy_url)
            return True
        else:
            print ("Proxy '%s` is not valid." % proxy_url)

    except:
        print ("\n\ntest_proxy() - An error occurred while trying to test proxy '%s`." % proxy_url)
        return False

    return False


def get_valid_proxy():
    try:
        print ("Please wait while we search the list for a valid proxy to use...")

        for proxy in proxies_list:
            if test_proxy(proxy):
                return proxy

        return 
    except:
        print ("\n\nget_valid_proxy() - An error occurred in the function that returns a valid proxy, the bot will continue without a proxy.")
        return



def login():
    try:
        print ("Logging in to your account...")

        #Position yourself on the main page of Presearch
        driver.get("https://account.presearch.com/")
        wait = ui.WebDriverWait(driver, 10)
        wait.until(page_loaded)

        if check_is_logged_in():
            return True

        #Check if exists a file with cookies
        if os.path.exists("ExtraFiles//cookies.pkl"):

            #SeIf there are cookies, use them to log into your Presearch account
            if login_with_cookies():
                return True

        sleep(5)

        accounts_data = open("ExtraFiles//accounts.txt", "r").readlines()
        for account in accounts_data:
            account_splited = account.split(":", maxsplit=1)
            # Extract Email and Password from accounts.txt
            email = account_splited[0].strip()
            password = account_splited[1].strip()

            if email != "" and password != "":
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

        print('At this point you will have to complete the challenge to prove that you are not a robot logging in.')
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
        print ("\n\nlogin() - There was an error trying to log in to your account.")
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
        print ("\n\nlogin_with_cookies() - An error occurred while trying to apply the cookie to automatically login to your account.")
        return


def check_is_logged_in():
    #Check if you is logged in
    if driver.current_url == "https://account.presearch.com/":
        return True


def check_day_searchs():
    try:
        print("Checking if all paid searches of the day have already been performed...")

        #Page where we have the list of daily searches.
        link = "https://account.presearch.com/tokens/usage-rewards?page=3"
        driver.get(link)
        wait = ui.WebDriverWait(driver, 10)
        wait.until(page_loaded)

        #Get a date from 25 searches, if it is equal to today's date, we have all daily searches completed
        search_date = driver.find_element(By.XPATH, '//*[@id="main"]/div[2]/div/div[3]/div/div/div[2]/table/tbody/tr[5]/td[2]/div/div/div/div/span').text
        search_date = datetime.strptime(search_date, '%b %d, %Y %H:%M:%S')
        search_date = search_date.strftime('%Y-%m-%d')
        today_date = datetime.today().strftime('%Y-%m-%d')

        if search_date == today_date:
            print("\n\nAll 25 paid daily searches had already been performed.\nCome back again tomorrow.")
            return True

    except:
        print ("\n\ncheck_day_searchs() - It was not possible to validate whether all the daily searches have already been carried out.")
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

                if search(word):
                    print("Searched for: " + word)
                
                sleep(max(config["delay"], 2))
        else:
            for word in words:
                word = word.strip()

                if not search(word):
                    return

                print("Searched for: " + word)
                sleep(max(config["delay"], 2))

        print("\n\nAll searches have been completed!\nIf you didn't get the maximum daily reward, run the bot again.")
    except:
        print ("\n\nloop_search() - An error occurred while we were carrying out the searches.!\nPlease re-run the bot to try again")
        return


def search(word):
    try:
        search_bar = driver.find_element(By.NAME, "q")
        search_bar.clear()
        search_bar.send_keys(word)
        search_bar.submit()

        return True
    except:
        print ("\nsearch() - An error occurred while trying to search for the word '%s`." % word)
        return False
        
def get_reward_tokens():
    #Position yourself on the main page of Presearch
    link = "https://account.presearch.com/"
    driver.get(link)
    wait = ui.WebDriverWait(driver, 10)
    wait.until(page_loaded)

    reward_tokens = driver.find_element(By.XPATH, '//*[@id="main"]/div[2]/div/div[3]/div/div/div[2]/table/tbody/tr[5]/td[2]/div/div/div/div/span').text
    print("\nYou have collected " + reward_tokens + " Usage Reward Tokens.\n\n")


def main():
    global proxies_list
    global driver

    proxy = None

    if config["proxy"]:
        #Clear the list of proxies and fetch a new list.
        proxies_list.clear()    
        proxies_list = get_list_proxies()

        #If we have proxies in the list it is valid if any of them are valid.
        if len(proxies_list) > 0:
            proxy = get_valid_proxy()
            proxies_list.remove(proxy)

    #Applies the settings to the webdriver and starts it.
    driver = setting_up_webdriver(proxy)

    if driver:
        #If you is logged in do research
        if login():
            print("Login was successful!")

            #It will do the daily searches only if they are not all done yet.
            if not check_day_searchs():
                print("Doing the daily searches...")
                loop_search()

            get_reward_tokens()

        else:
            if os.path.exists("ExtraFiles//cookies.pkl"):
                os.remove("ExtraFiles//cookies.pkl")

            print("\n\nUnable to login to your Presearch account, please re-run the bot to try to login.")

        driver.close()


if __name__ == "__main__":
    main()