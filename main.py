# coding: utf-8
# array where i_th element is the number of ayahs in the i_th surah of the Quran
AYAH_COUNT = [7,286,200,176,120,165,206,75,129,109,123,111,43,52,99,128,111,110,98,135,112,78,118,64,77,227,93,88,69,60,34,30,73,54,45,83,182,88,75,85,54,53,89,59,37,35,38,29,18,45,60,49,62,55,78,96,29,22,24,13,14,11,11,18,12,12,30,52,52,44,28,28,20,56,40,31,50,40,46,42,29,19,36,25,22,17,19,26,30,20,15,21,11,8,8,19,5,8,8,11,11,8,3,9,5,4,7,3,6,3,5,4,5,6]
# to parse html nicely with unicode
from bs4 import BeautifulSoup
# basically all processing of Arabic text will be done with copious amounts of regular expressions
import re
# to call webpage and retrieve html
import requests
# quick and dirty hack to deal with unicode
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
# start a timer to display time elapsed
import time
global start
start = time.time()
# load ayah tags from text file
ayah_tags = [i.strip("\n") for i in open("ayah_tags.txt","r").readlines()]
# function to strip Arabic text of tafsir from html
def get_arabic_text(url):
	# get html
	html = requests.get(url).content
	# use beautiful soup to make unicode nice
	soup = unicode(BeautifulSoup(html,features="html5lib"))
	# pick out lines that have the tag "TextResultArabic" (tag used to label lines with the Arabic text of tafsir)
	out = [i.encode("utf-8") for i in soup.split("\n") if "TextResultArabic" in i]
	# get text in angle brackets and remove angle brackets
	out = [re.sub("<[^>]*","",i).replace("<","").replace(">","") for i in out]
	# return processed text	
	return out
# function to count pages of text in a given url
def count_pages(url):
	# get html and make soup
	html = requests.get(url).content
	soup = unicode(BeautifulSoup(html,features="html5lib"))
	out = []
	# find all instances of javascript page number labels 	
	for i in re.findall("Javascript:InnerLink_onchange\([0-9|,]*\)",soup):
		# remove extra text and gather page labels in array as ints
		i = re.sub("Javascript:InnerLink_onchange","",i)
		for j in [int(k) for k in i.strip("(").strip(")").split(",")]:
			out.append(j)
	# return maximum of array	
	if len(out)==0: return 1
	else: return max(out)
# function that checks whether or not url has any tafsir text
def url_has_tafsir(url):
	# get html and make soup	
	html = requests.get(url).content
	soup = unicode(BeautifulSoup(html,features="html5lib"))
	# check for text "tafsir for this ayah does not exist"
	return u"تفسير هذه الآية غير موجود" not in soup
# returns all of the text under the tafsir of given ayah by looping through all urls under that ayah
def get_tafsir_ayah(tafsir_id,surah_no,ayah_no):
	url = "https://www.altafsir.com/Tafasir.asp?tMadhNo=0&tTafsirNo="+str(tafsir_id)+"&tSoraNo="+str(surah_no)+"&tAyahNo="+str(ayah_no)+"&tDisplay=yes&Page=1&LanguageId=1"
	if url_has_tafsir(url)==False:
		return None
	else:
		duplicate_flag = False
		number_of_pages = count_pages(url)
		out = ""
		for i in range(1,number_of_pages+1):
			print "attempt no. "+str(attempts)+" "+"surah "+str(surah_no)+", ayah "+str(ayah_no)+" "+"getting page "+str(i)+"/"+str(number_of_pages)+" "+str(time.time()-start)
			new_url = "https://www.altafsir.com/Tafasir.asp?tMadhNo=0&tTafsirNo="+str(tafsir_id)+"&tSoraNo="+str(surah_no)+"&tAyahNo="+str(ayah_no)+"&tDisplay=yes&Page="+str(i)+"&LanguageId=1"
			out += "".join([i+"\n" for i in get_arabic_text(new_url) if "}" in i])
		return out
# get ayahs that are referenced under the tafsir of given ayah
def get_referenced_ayahs(tafsir_id,surah_no,ayah_no):
	# get tafsir of given ayah
	temp = get_tafsir_ayah(tafsir_id,surah_no,ayah_no)
	ayah_matches = []
	# loop through all ayah tags and look for them in tafsir text
	for a in ayah_tags:
		a = a.split("|")
		current_surah_no = int(a[1])
		current_ayah_no = int(a[2])
		# if match is found, append to array		
		if temp.find(a[0])!=-1: ayah_matches.append((current_surah_no,current_ayah_no)); print "match!"
	# return array	
	return ayah_matches
# code below is to batch collect referenced ayahs for an entire surah
"""
tafsir_id = sys.argv[1]
i = int(sys.argv[2])
start2 = time.time()
flag = True
while flag:
	try:
		g = open(tafsir_id+"_"+str(i)+".txt","w")
		for j in range(AYAH_COUNT[int(i)]):
			print (i+1,j+1,time.time()-start2)
			links = get_referenced_ayahs(1,i+1,j+1)
			g.write(str(i)+" "+str(j)+" "+str(links))
			g.write("\n")
		g.close()
		flag = False
	except:
		continue
"""
print get_referenced_ayahs(4,2,190)
