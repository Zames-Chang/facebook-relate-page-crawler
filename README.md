# facebook-relate-page-crawler
## 目標
main.py 給關鍵字透過 selenium 爬取　facebook 搜尋的結果　
main2.py 透過給關鍵字爬取粉絲專頁的相關粉絲專頁頁面

# 環境安裝
```
$ pip install selenium
$ pip install beautifulsoup4
$ pip install pandas
$ pip install openpyxl
```


請使用 txt 打開 config.json 填入你的facebook 帳號跟密碼
```jsonld=
{
    "account": "youtaccount@xxx.com",
    "password": "yourpassword",
    "time": 120 // 單位為分鐘，代表最久跑多久後要停下來
}
```

然後在 windows powershell 操作以下指令
```
$ python main.py [粉專關鍵字]
```

接著就開始自動爬取，程式有三種情況會停下來
1. 三個相關粉專都重複了
2. 沒有相關粉專
3. 超過你設定的時間

最後結果會輸出在桌面的專案資料夾(facebook-crawler)裡面的 output 
