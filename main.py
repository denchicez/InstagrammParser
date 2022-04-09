HOST = 'https://www.instagram.com'
import re
import time

import requests as rq
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class InstagrammParser:
    def __init__(self, log: bool = False):
        self.HOST = 'https://www.instagram.com'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 105.0.0.11.118 (iPhone11,8; iOS 12_3_1; en_US; en-US; scale=2.00; 828x1792; 165586599)'
        }
        self.log = log

    def initBySelenium(self, login: str, password: str, pathToChromeDriver: str = "C:\Files\chromedriver.exe"):
        selector_log = '#loginForm > div > div:nth-child(1) > div > label > input'
        selector_pas = '#loginForm > div > div:nth-child(2) > div > label > input'
        buttonAdd = "body > div.RnEpo.Yx5HN._4Yzd2 > div > div > button.aOOlW.bIiDR"
        button = '#loginForm > div > div:nth-child(3)'

        options = Options()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--incognito')
        options.add_argument('--headless')

        browser = webdriver.Chrome(pathToChromeDriver, options=options)
        browser.set_page_load_timeout(10)
        wait = WebDriverWait(browser, 5)
        try:
            browser.get(self.HOST)
            if (self.log):
                print("Start parse")
        except TimeoutException as e:
            print("Can't connect to inst : " + str(e))
            browser.quit()
            exit()
        try:
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector_log)))
            browser.find_element_by_css_selector(selector_log).send_keys(login)
            if (self.log):
                print("Insert login")
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector_pas)))
            browser.find_element_by_css_selector(selector_pas).send_keys(password)
            if (self.log):
                print("Insert password")
            try:
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, buttonAdd))).click()
                if (self.log):
                    print("Complete agree inst with cookie")
            except Exception:
                pass
            time.sleep(1)
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, button))).click()
            if (self.log):
                print("Click button")
        except Exception as e:
            print("Can't login : ", str(e))
            browser.quit()
            exit()
        time.sleep(5)
        cookies = browser.get_cookies()
        self.cookies = {}
        for cookie in cookies:
            self.cookies.update({cookie['name']: cookie["value"]})
            browser.quit()

    def initByCookies(self, cookies: dict):
        self.cookies = cookies

    def __getUserId(self, userName):
        if (self.log):
            print("URL : ", HOST + f"/{userName}/?__a=1")
        resp = rq.get(HOST + f"/{userName}/?__a=1", headers=self.headers, cookies=self.cookies)
        return re.findall(r',"id":"([^"]*)"', resp.text)[0]

    def get_followers(self, username):
        followers = []
        userid = self.__getUserId(username)
        lastCounter = 0
        while (True):
            url = f"https://i.instagram.com/api/v1/friendships/{userid}/following/?count=50&max_id={lastCounter}"
            if (self.log):
                print("URL : ", url)
            resp = rq.get(url, headers=self.headers, cookies=self.cookies)
            users = resp.json()
            users = users['users']
            if (len(users) == 0):
                break
            for user in users:
                followers.append(user['username'])
            lastCounter += 50
        return followers

    def get_subscribers(self, username):
        followers = []
        userid = self.__getUserId(username)
        lastCounter = 0
        while (True):
            url = f"https://i.instagram.com/api/v1/friendships/{userid}/followers/?count=50&max_id={lastCounter}"
            if (self.log):
                print("URL : ", url)
            resp = rq.get(url, headers=self.headers, cookies=self.cookies)
            users = resp.json()
            users = users['users']
            if (len(users) == 0):
                break
            for user in users:
                followers.append(user['username'])
            lastCounter += 50
        return followers


def main():
    Parser = InstagrammParser()
    Parser.initBySelenium(login="login", password="password")
    subs = Parser.get_subscribers("denchicez")
    fols = Parser.get_followers("denchicez")


if __name__ == '__main__':
    main()
