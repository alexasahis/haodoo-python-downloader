# Your code here!
import datetime
from urllib.request import urlopen
import requests as rq
import requests
from bs4 import BeautifulSoup
import re
from urllib.request import urlopen
import os, sys

from random import randint
from time import sleep


def downloadbook(dlfilename,localpath):
	#print(dlfilename) # 把所有的 <a></a> 抓出來
	dllink="http://www.haodoo.net/?M=d&P="+dlfilename
	dlfile = requests.get(dllink, allow_redirects=True)
	savefile=open(localpath+"/"+dlfilename, 'wb')
	savefile.write(dlfile.content)
	savefile.close()
	dlfile.close()

def processbook(url,basepath):
	print(url)
	print("START")
	response = rq.get(url) # 用 requests 的 get 方法把網頁抓下來
	html_doc = response.text # text 屬性就是 html 檔案
	soup = BeautifulSoup(response.text, "lxml") # 指定 lxml 作為解析器

	bookftype=[]
	bookftype.append({"inval":"下載 updb 檔", "filetype":"updb" ,"replace":"DownloadUpdb('"})
	bookftype.append({"inval":"下載 prc 檔", "filetype":"prc","replace":"DownloadPrc('"})
	bookftype.append({"inval":"下載直式 mobi 檔", "filetype":"mobi","replace":"DownloadMobi('"})
	bookftype.append({"inval":"下載 epub 檔", "filetype":"epub","replace":"DownloadEpub('"})
	bookftype.append({"inval":"下載直式 epub 檔", "filetype":"epub","replace":"DownloadVEpub('"})
	bookftype.append({"inval":"下載 pdf 檔", "filetype":"pdf","replace":"DownloadPdf('"})

	a_list = soup.find(name='input',value="線上閱讀")

	mdpath=""


	while a_list is not None:
		#print("DEBUG 0 start new book")
		t = a_list.find_previous(name="font")
		if t is None:
			auth="NULL AUTHOR"
		#	print(t)
		else:
			if t.string is None:
				auth="NULL AUTHOR"
			else:
				auth=t.string
			tb = t.next_sibling
			if tb is None:
				tb=""
		print(auth)
		print(tb)
		authpath = basepath+auth.replace("/","#")
		if not os.path.isdir(authpath):
			os.mkdir(authpath,0o755)

		mdpath=authpath+"/"+tb.replace("/","#")
		if not os.path.isdir(mdpath):
			os.mkdir(mdpath,0o755)

		#print("DEBUG check "+mdpath+"/done.txt")
		if os.path.isfile(mdpath+"/done.txt"):
			print("Already downloaded")
		else:
			#print("DEBUG isfile FALSE")

			for b in bookftype:
				f=a_list.find_next(name='input',value=b["inval"])
				if f:
					dlfilename=f['onclick'].replace(b["replace"],"").replace("')","")+"."+b["filetype"]
					downloadbook(dlfilename,mdpath)
					print("DOWNLOAD "+b["filetype"])


			coverimg=a_list.find_next(name='img')
			while True:
				if coverimg:
					m = re.compile(r'covers\/.*')
					print("DOWNLOAD "+coverimg['src'])
					if m.match(coverimg['src']):
						dlimgurl="http://www.haodoo.net/"+coverimg['src']
						dlimgfile = requests.get(dlimgurl, allow_redirects=True)
						fimg=open(mdpath+"/"+ coverimg['src'].replace("covers/" , "") , 'wb')
						fimg.write(dlimgfile.content)
						fimg.close()
						dlimgfile.close()
						#print("DEBUG img done")

					coverimg=coverimg.find_next(name='img')
				if not coverimg:
					break


			findex=open(mdpath+"/index.html"  , 'wt')
			modifyhtml=html_doc.replace("src=\"covers/","src=\"")
			findex.write(modifyhtml)
			findex.close()
			print("DOWNLOAD BOOK Ok")
			donefile=open(mdpath+"/done.txt",'wt')
			now = datetime.datetime.now()
			donefile.write(now.strftime("%Y-%m-%d %H:%M:%S"))
			donefile.close()
			print("DONE " +mdpath)
			print("NEXT BOOK")
			stime=randint(1,10)
			print("WAIT "+str(stime)+" seconds.")
			sleep(stime)

		a_list = a_list.find_next(name='input',value="線上閱讀")

		if not a_list:
			print("NEXT PAGE")
			break

	response.close()

def processcat(cat,catnum,bpath):
	basepath = bpath+cat+"/"
	if not os.path.isdir(basepath):
		os.mkdir( basepath, 0o755 );

	url = "http://www.haodoo.net/?M=hd&P="+cat
	for i in range(1,catnum+1):
		urli=url+'-'+str(i)
		response = rq.get(urli) # 用 requests 的 get 方法把網頁抓下來
		html_doc = response.text # text 屬性就是 html 檔案

		cindex=open(basepath+"/index"+str(i)+".html"  , 'wt')
		cindex.write(html_doc)
		cindex.close()

		soup = BeautifulSoup(response.text, "lxml") # 指定 lxml 作為解析器
		a_list = soup.find_all('a')
		for ai in a_list:
			m = re.compile(r'(.*)M=book(.*)')
			m2 = re.compile(r'(.*)M=Share(.*)')
			if m.match(ai['href']) or m2.match(ai['href']):
				#print(ai) # 把所有的 <a></a> 抓出來
				#print("OK\n\n")
				u=ai['href'].replace("&amp;","&")
				u="http://www.haodoo.net/"+u
				#print(u)
				processbook(u,basepath)

		response.close()


if len(sys.argv)!= 2:
	print("Please provide save path : python3 haodoo.py /this/is/path")
else:
	cattype=[]
	cattype.append({"cat":"100", "catnum":5})
	cattype.append({"cat":"wisdom", "catnum":6})
	cattype.append({"cat":"history", "catnum":3})
	cattype.append({"cat":"martial", "catnum":10})
	cattype.append({"cat":"mystery", "catnum":5})
	cattype.append({"cat":"romance", "catnum":6})
	cattype.append({"cat":"scifi", "catnum":10})
	cattype.append({"cat":"fiction", "catnum":7})
	if not os.path.isdir(sys.argv[1]):
		print("Path not exists")
	else:
		bpath = sys.argv[1]+"/haodoo/"
		if not os.path.isdir(bpath):
			os.mkdir( bpath, 0o755 );

		for c in cattype:
			processcat(c["cat"],c["catnum"],bpath)
