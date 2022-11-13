#步驟1 import所有需要的library
from bs4 import BeautifulSoup as BS
from urllib.request import Request, urlopen
import pandas as pd
import time
import csv
import requests
from selenium import webdriver
import sys
import io


#步驟2 使用chromedriver開啟網頁
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
driver = webdriver.Chrome('chromedriver.exe')
driver.get("https://udn.com/search/word/2/五倍券")

#步驟3 將搜尋結果展開至我們要的大小
date = "2021-07-18"
#i = 0 #滾輪下拉次數
time.sleep(10) #等待網頁開好
driver.execute_script("window.scrollBy(0,5000)") #經過測試，第一次移動5000是最剛好可以讓網頁繼續讀取的距離
time.sleep(10) #下拉第一次後，保留時間讓網頁跑出動態結果
while driver.page_source.find(date) == -1 : #持續下拉網頁，直到翻到指定日期的新聞
    #print("進入")
    driver.execute_script("window.scrollBy(0,4800)") #經過測試，每次移動4800是最剛好可以讓網頁繼續讀取的距離
    time.sleep(10) #每一次下拉後，保留時間讓網頁跑出動態結果
    #print("休息好了")
    #i += 1
    #print("下拉第" + str(i) + "次")

#步驟4 開始蒐集每一篇新聞的網址
BSParse = BS(driver.page_source,'html.parser')
div_context = BSParse.find_all("a", class_="story-list__image--holder")

href = []
href_check = ""
for i in range(len(div_context)):
	href_check = div_context[i].get('href')
	if (href_check.find("https://udn.com/news/story/")) != -1: #因為聯合新聞網除了一般常見的新聞頁面外，會有一些特殊類別的新聞界面，這裡只收錄一般常見的頁面
		href.append(href_check)
print(len(href))


#步驟5 將每一篇新聞的內容逐個爬下
time = []
author = []
title = []
content = []
author_check = 0
hdr = {'User-Agent': 'Mozilla/5.0'}
for i in range(len(href)):
	site = href[i]
	req = Request(site, headers = hdr)
	page = urlopen(req)
	soup = BS(page, "html.parser") #BS將page進行解讀，利用html.parser的方式，如果沒加上的話，會形成亂碼
	newest = soup.find("section", {"class":"article-content__wrapper"})

	#確定頁面依然存在，不是已刪除的新聞，這裡淘汰的是404not found的網頁
	if (str(newest) == "None"):
		print("第" + str(i) + "篇新聞pass(404 not found)")
		print("\n\n")
		time.append("pass") #將list寫入csv時，每個list需一樣，所以在需pass的網址的其他欄位寫上pass
		author.append("pass")
		title.append("pass")
		content.append("pass")
		continue

	#要拿到的東西{時間, 記者, 標題, 內容, 網址}
	newest_time = newest.find("time", {"class":"article-content__time"}) #時間
	if (str(newest_time) == "None"): #藉由時間的抓取結果來double check這是不是我們要的網頁規格
		print("第" + str(i) + "篇新聞pass(不符合規格)")
		print("\n\n")
		time.append("pass") #將list寫入csv時，每個list需一樣，所以在需pass的網址的其他欄位寫上pass
		author.append("pass")
		title.append("pass")
		content.append("pass")
		continue
	print("第" + str(i) + "篇新聞:")
	print("時間 : " + newest_time.text)

	newest_author = newest.find("span", {"class":"article-content__author"}) #記者
	newest_author = newest_author.find("a") #僅取出記者名字
	if (str(newest_author) == "None"): #因為有的報導是轉貼其他網站的，如果是這種情況的話，就不取出名字
		newest_author = newest.find("span", {"class":"article-content__author"})
		newest_author = newest_author.text.strip().replace('\n', '')
		author_check = 1
	newest_title = newest.find("h1", {"class":"article-content__title"}) #標題
	newest_content = newest.find("section", {"class":"article-content__editor"}) #內文

	#開始把抓到的內容加入儲存陣列裡面
	time.append(newest_time.text)
	if author_check:
		author.append(newest_author)
	else :
		author.append(newest_author.text)
	title.append(newest_title.text)
	content.append(newest_content.text)
	
	
	if author_check:
		print("記者 : " + newest_author)
	else :
		print("記者 : " + newest_author.text)
	print("標題 : " + newest_title.text)
	print("\n\n")
	
	author_check = 0

df = pd.DataFrame({'time':time, 'author':author, 'title':title, 'content': content, "href":href}, columns = ["time", "author", "title", "content", "href"])
df.to_csv("News_crawlers.csv", encoding = "utf_8_sig") #python會有中文編碼的問題，因此存進csv檔時須加上encoding參數