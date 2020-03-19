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
    check_table = {}
    return_list = []
    with open("config.json", "r") as f:
        config = json.loads(f.read())
        account = config['account']
        password = config['password']
        scorll_time = config['time']
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
    time.sleep(10)
    html = browser.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    soup = BeautifulSoup(html, "html.parser")
    result = soup.find('div', {"id" : "browse_result_area"}).findAll('a')
    first = 0
    for r in result:
        if(r.get_text() != "" and re.match("https://www.facebook.com/", r['href'])):
            first = [r.get_text(), r['href']]
            break
    if(first):
        browser.execute_script(f"window.location.href = '{first[1]}'")
        first[1] = first[1][:first[1].find('?')]
        data = parser(first)
        return_list.append(data)
        check_table[data["網址"]] = 1
        time.sleep(10)
        count = 0
        while(1):
            count += 1
            html = browser.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
            soup = BeautifulSoup(html, "html.parser")
            related_page = soup.find('div', id=re.compile("^PageRelatedPagesSecondaryPagelet"))
            flag = 0
            for a in related_page.findAll('a'):
                name = a.get_text()
                if(re.match(r'https://www.facebook.com/.+/\?', a['href']) and name != "" ):
                    url = a['href']
                    url = url[:url.find('?')]
                    if(url not in check_table):
                        flag = 1
                        data = parser([name, url])
                        return_list.append(data)
                        check_table[url] = 1
                        browser.execute_script(f"window.location.href = '{url}'")
                        break
            time.sleep(10)
            print("flag: " + str(flag))
            if(flag == 0 or count >= scorll_time*6):
                break
    browser.close()
    return return_list

def parser(fans_page):
    name = fans_page[0]
    url = fans_page[1]
    url_about = url + "about"
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

def main(keyword):
    fans_pages = get_facebook_fanspage_list(keyword)
    data = {
        "名稱": [],
        "網址": [],
        "電話": [],
        "電子郵件": [],
        "地址": []
    }
    df = pd.DataFrame(data=data)
    for fans_page in fans_pages:
        df = df.append(fans_page, ignore_index=True)
    df.to_excel(f"./output/{keyword}.xlsx", index=False)

if __name__ == "__main__":
    if(len(sys.argv) != 2):
        raise ValueError("錯誤的使用方法: 請使用 python main.py [想搜尋的粉專名稱]")
    main(sys.argv[1])
    print("下載成功!請到output資料夾中確認結果")
    