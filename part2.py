#!/usr/bin/env python
# coding: utf-8

#built-in imports
import re
import threading
from queue import Queue
from threading import Semaphore, Timer
from configparser import ConfigParser
import urllib
import html
import ast
from part1 import keyword_search
import sys

#import config file
config_object = ConfigParser()
config_object.read("config.ini")
param = config_object["parameters"]

#set parameters
workers_num = int(param["workers_num"])
requests_per_time = int(param["requests_per_time"])
time = int(param["time"])
with_wiki_references = ast.literal_eval(param["with_wiki_references"])   #whether to include reference and external links in wiki-scraper?
print_wiki_txt = ast.literal_eval(param["print_wiki_txt"]) #whether to print the scraped wiki page
link = param["url"]

#semaphore for sync printing
print_semaphore = Semaphore(1)

#producer(scheduler) architecture
class Producer:
    def __init__(self, queue):
        self.queue = queue
    def run(self):
        threading.Timer(time, self.run).start()
        # print("Reset")
        for i in range(requests_per_time):
            self.queue.put(i)
            
#consumers(workers) architecture
class Consumer:
    def __init__(self, queue, id):
        self.queue = queue
        self.__id = id
    def run(self):
        while True:
            try:
                    #check if has permission to send a request (based on requests_per_time) if yes continue, else blocked until producer initiates new permissions
                self.queue.get()
                    #scrape and search keywords
                wiki_txt, url = Scraper.url_to_text(link)
                output, final_txt = keyword_search(wiki_txt)
                    #sync printing
                print_semaphore.acquire()
                print("Worker: "+str(self.__id))
                print("Random URL: "+ str(url))
#                 print(final_txt+"\n")
                print("Text: "+wiki_txt+"\n") if (print_wiki_txt == True) else None
                print('Matches :', output)
                print("-----------------------------")
                print_semaphore.release()
                self.queue.task_done()
            except KeyboardInterrupt:
                print('Interrupted')
                sys.exit()

#scrape a random wiki page
class Scraper:
    #decode url data to html format and finaly produce a nicely formatted text
    def url_to_text(url):
        try:
            response = urllib.request.urlopen(url)
            html_decode = response.read().decode("utf-8")
            text = Scraper.html_to_text(html_decode)
            return text, response.url
        except urllib.error.HTTPError as exception:
            print(exception)
            sys.exit()
            
    #remove all html tags (# <.*> : greedy, <.*?> : non-greedy, re.DOTALL : with newlines)
    def html_to_text(html_decode):
        if html_decode is None:
            return ""
        text = html_decode
        if with_wiki_references == False:
            text = re.sub(r'<h2><span class="mw-headline" id="External_links".*', "", text, flags=re.DOTALL)   #remove refrences and external-links
            text = re.sub(r'<h2><span class="mw-headline" id="References".*', "", text, flags=re.DOTALL)   #remove refrences and external-links
        text = re.sub(r'<h2><span class="mw-headline" id="See_also".*', "", text, flags=re.DOTALL)   #remove see-also forward
        text = re.sub(r"<(script|style).*?>.*?(</\1>)", " ", text, flags=re.DOTALL)   #remove internal style
        text = re.sub(r"<!--(.*?)-->", " ", text, flags=re.DOTALL)   #remove comments
        text = re.sub(r'<title>.*?</title>', "", text)   #remove title
        text = re.sub(r'<div id="siteSub".*?</div>', " ", text)   #remove noprint tag
        text = re.sub(r'<a class="mw-jump-link".*?</a>', " ", text)   #remove unnecessary links
        text = re.sub(r'<div id="toc".*?</ul>\s</div>', "", text, flags=re.DOTALL)   #remove contents window
        text = re.sub(r"</?(p|div|br).*?>", " ", text, flags=re.DOTALL)   #remove all <p>, <div>, <br>
        text = re.sub(r"<.*?>", " ", text, flags=re.DOTALL)   #remove all tags
        text = html.unescape(text)
        text = re.sub(r"[\s^]+", " ", text)   #remove consecutive whitespaces
        text = re.sub("[^\S\n]+", " ", text, flags=re.UNICODE)   #remove tabs
        text = re.sub("(\n)", "", text)   #remove newline
        text = re.sub("\n\n+", "\n", text)   #remove consecutive newlines
        text = text.strip()   #remove leading and traling spaces
        return text
    
#create, start and join consumers(workers) and producer(scheduler) threads
def main():
    q = Queue(maxsize=requests_per_time)
        #create and start producer thread
    scheduler = Producer(q)
    scheduler_thread = threading.Thread(target=scheduler.run)
    scheduler_thread.start()
        #create and start consumers thread
    workers = [] 
    for worker_id in range(workers_num):
        worker = Consumer(q, worker_id)
        workers.append(worker)   
    worker_threads = []
    for worker in workers:
        t = threading.Thread(target=worker.run)
        t.start()
        worker_threads.append(t)
        #join all threads and terminate
    scheduler_thread.join()
    for t in worker_threads:
        t.join()      
    print("DONE!")
      
if __name__ == "__main__":
    main()

#with the non-built-in library: BeautifulSoup, scraping a wiki page could be more readable
# def wiki_scrape(url): 
#     wiki_txt = ''
#     res = requests.get(url,)
#     res.raise_for_status()
#     wiki = bs4.BeautifulSoup(res.text,"html.parser")
#     for i in wiki.select('p'):
#         wiki_txt = wiki_txt + i.getText()
#     return wiki_txt, res.url

