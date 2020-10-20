#!/usr/bin/env python
# coding: utf-8

#built-in imports
import re
from configparser import ConfigParser

#import config file
config_object = ConfigParser()
config_object.read("config.ini")
param = config_object["parameters"]

#set parameters
static_input = param["static_input"]
          
#search keywords in text
def keyword_search(paragraph):
    output = []
    d = {}
    with open('keywords.txt') as txt:
            #manipulate strings so it can be easily compared
        keywords = txt.read().lower()
        keywords = re.sub(r'[^\nA-Za-z0-9]+'," ",keywords)   #remove Non-alphanumeric exept new line
        keywords = re.sub(r' +'," ",keywords).splitlines()   #remove consecutive newlines 
        wordlist = paragraph.lower()
        wordlist = re.sub(r'\W'," ",wordlist)   #remove Non-alphanumeric
        wordlist = re.sub(r' +'," ",wordlist)   #remove consecutive newlines
            #fill dictionary with keywords keys and counting values
        for w in keywords:
            d[w] = wordlist.count(w)
            #also check for 'elimination of the space character' cases:
            d[w] = d[w] + wordlist.count(w.replace(" ", ""))
            #if counting value greater than 0, found a match and add the string to the output array
        for k,v in d.items():
            if v>0:
                output.append(k)
        return output, wordlist

def main():
    output, final_txt = keyword_search(static_input)  
    print(output)
      
if __name__ == "__main__":
    main()
