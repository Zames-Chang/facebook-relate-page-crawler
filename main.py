# -*- coding: UTF-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys 
import io
from bs4 import BeautifulSoup
from google import google
import re
import pandas as pd
import sys
import requests
import time 
from selenium.webdriver.chrome.options import Options
from random import randint
import json

def get_facebook_fanspage_list(keyword):
    with open("config.json", "r") as f:
        config = json.loads(f.read())
        account = config['account']
        password = config['password']
        scorll_time = config['scroll-time']
    chrome_options = Options()
    chrome_options.add_experimental_option('prefs',{'profile.default_content_setting_values.notifications':1})
    browser = webdriver.Chrome(chrome_options = chrome_options)
    browser.get("https://www.facebook.com")
    elem_user = browser.find_element_by_id("email")
    elem_user.clear
    elem_user.send_keys(account)  
    elem_pwd = browser.find_element_by_name("pass")
    elem_pwd.clear
    elem_pwd.send_keys(password)
    elem_pwd.send_keys(Keys.RETURN)
    time.sleep(10)
    browser.execute_script(f"window.location.href = 'https://www.facebook.com/search/pages/?q={keyword}&epa=SERP_TAB'")
    for _ in range(scorll_time):
        js="var q=document.documentElement.scrollTop=10000"  
        browser.execute_script(js)
        time.sleep(5)
    time.sleep(10)
    html = browser.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    soup = BeautifulSoup(html, "html.parser")
    result = soup.find('div', {"id" : "browse_result_area"}).findAll('a')
    return_list = []
    for r in result:
        if(r.get_text() != "" and re.match("^https://www.facebook.com/", r['href'])):
            return_list.append([r.get_text(), r['href']])
    browser.close()
    return return_list

def parser(fans_page):
    name = fans_page[0]
    url = fans_page[1]
    url_about = url.strip("?ref=br_rs") + "about"
    html = requests.get(url_about).text
    soup = BeautifulSoup(html, "html.parser")
    try:
        phone = soup.find("div", string=re.compile("^通話[\s|0-9]+")).get_text().strip(" ").strip("通話")
    except:
        phone = None
    try:
        email_pattern = "^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"
        email = soup.find("div", string=re.compile(email_pattern)).get_text()
    except:
        email = None
    try:
        address = soup.find("div", string=re.compile("規劃路線")).previous_sibling.get_text()
    except:
        address = None
    data = {
        "名稱": name,
        "網址": url,
        "電話": phone,
        "電子郵件": email,
        "地址": address
    }
    return data
    #df = pd.DataFrame(data=data)
    #df.to_excel(f"./output/{fans_page}.xlsx", index=False)

def main(keyword):
    fans_pages = get_facebook_fanspage_list(keyword)
    fans_pages = fans_pages[:-1]
    data = {
        "名稱": [],
        "網址": [],
        "電話": [],
        "電子郵件": [],
        "地址": []
    }
    check_table = {}
    df = pd.DataFrame(data=data)
    for fans_page in fans_pages:
        print(f"prcoessing {fans_page[0]}")
        fans_page_information = parser(fans_page)
        time.sleep(randint(1,3))
        if(not fans_page_information["網址"] in check_table):
            check_table[fans_page_information["網址"]] = True
            df = df.append(fans_page_information, ignore_index=True)
    df.to_excel(f"./output/{keyword}.xlsx", index=False)

if __name__ == "__main__":
    if(len(sys.argv) != 2):
        raise ValueError("錯誤的使用方法: 請使用 python main.py [想搜尋的粉專名稱]")
    main(sys.argv[1])
    print("下載成功!請到output資料夾中確認結果")
    