#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Web scraper able to bypass Cloudflare using a pool of proxies
#don't use it to do harmfull/illegal things, the coder is not responsable for them,this code is only for educational purporse

import sys
import cfscrape
import requests,re,threading,time
import ctypes
import re
from msvcrt import getch
from collections import deque
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from nt import access
init() 
from threading import *
screen_lock = Semaphore(value=1)
import json
import os


Tk().withdraw() #remove the window
source_lst = deque() 
proxies = deque() #working proxies
proxies_timed = deque() #dead proxy
hits = 0 
first = 1
i=0

#global variable to stop the threads
global killall
killall=0

start_time = time.time()

headers = {
            'User-agent': "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
            'origin' : 'http://example.com/'         
          }   

#global variable that check if using proxies or not
use_prox=0

#list keys
keys = {'timed out' : ('Request limiting policy has been breached','An error has occurred.'),
        'banned':('403','<title>Access denied','<title>Could not find host ','<title>Attention Required!'),
        'success':('http://example.com/'),
        'unsuccess':('403','<title>Access denied','<title>Could not find host ','<title>Attention Required!')
        }

#the source file is a file with the following format: "data1:data2\n"
print('Select Source file')
time.sleep(1)
source_file = askopenfilename()
with open(source_file,'r', encoding="utf8") as source: 
    source_lst = re.findall('(.*):(.*)',source.read().rstrip())
    
#to do: let the user select the type of the proxy  
choose=0
proxy_type =['https://','socks4://','socks5://']

#proxy scrape is a free proxy pool
print("Do you want use auto downloaded proxies from proxyscrape or to use yours?")
use_auto_proxies = int(input('To auto download digit [0] or to use yours [1]: '))
if(use_auto_proxies==0):
    type=int(input('http [0], https [1], other[2]: '))
    
if type==0:
    urlproxies="https://proxyscrape.com/proxies/HTTP_Working_Proxies.txt"
if type==1:
    urlproxies="https://proxyscrape.com/proxies/HTTP_SSL_Proxies_10000ms_Timeout_Proxies.txt"
if type==2:        
    urlproxies="https://proxyscrape.com/proxies/HTTP_Elite_Proxies.txt"
    
if use_auto_proxies==1:
    print('\nSelect a proxy file')
    time.sleep(1)
    proxy_file = askopenfilename() 
    with open(proxy_file,'r+') as proxyfile:
        for line in proxyfile.readlines():
            proxies.append(line.rstrip()) 

if use_auto_proxies==0:    
    r = requests.get(urlproxies)
    with open("tempf.tmp", 'wb') as f:  
        f.write(r.content)     
    with open("tempf.tmp",'r') as proxyfile:
        for line in proxyfile.readlines():
            proxies.append(line.rstrip()) 
    if os.path.exists("tempf.tmp"):    
        os.remove("tempf.tmp")  
    print("proxy were updated!")    
        
         


#FUNCTION THAT UPDATE THE NUMBER OF PAGE REQUESTED PER MINUTE
####################################
######   CPM UPDATE             ####
####################################
def cpm():
    global old_len,cpm,end

    while  not end:
        new_len = len(source_lst)
        cpm = (old_len - new_len) * 10
        old_len = new_len
        time.sleep(6)
    return


####################################
######   UPDATE THE STATUS BAR   ###
####################################
def update():
    global cpm,end, source_lst,proxies,hits
    while not end:
        raw_time = time.time() - start_time
        elapsed_time = time.strftime('%H:%M:%S',time.gmtime(raw_time))
        ctypes.windll.kernel32.SetConsoleTitleW(f'source left |{len(source_lst)}| cpm|{cpm}| hits |{hits}|  proxies left |{len(proxies)}|  elapsed time |{elapsed_time}| bots |{len(processes)-1}')
        if (raw_time % 600) == 0:
            with open('remaining_source.txt','w+') as file:
                for source in source_lst:
                    file.write(source[0]+':'+ source[1] + '\n')
    return


####################################
######  REQUEST    #################
####################################
def get_resp(): 
        global source_lst,proxies,url,proxy_type,proxy_type_in,hits,first,i,killall

        headers = {
                'User-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
                'origin' : 'http://example.com/',
                'referer': 'http://example.com/',    
                   }
       
#get a new source from the source list
#create the scraper object
        scraper = cfscrape.create_scraper()
        
        while source_lst and killall==0: #for all the source list
            
            apend = 0
            success = 0
            try:
                source= source_lst.pop() #extract a source string
            except:
                return 
            try:
                proxy = proxies.popleft() #get a new proxy
                prox= {'https': proxy_type[choose] + proxy}
            except IndexError:
                return
            check = 0

#get the page     
       
            try:
                if(use_prox == 1):
                    login=scraper.get("http://example.com/", proxies=prox,timeout = 15)
                else:
                    login=scraper.get("http://example.com/",timeout = 15)
                success = 1
     

            #if the proxy used is working and we had bypassed the proxies's blacklist of cloudflare go ahead:
                if (success) :
                      
                        payload = {
                                   '_token' : token
                                   } 
                                   
                        if(use_prox == 1):
                            testo_post=scraper.post("http://example.com/", data=payload,headers = headers, proxies=prox,timeout = 15)   #you can use also the get method             
                        else:
                            testo_post=scraper.post("http://example.com/", data=payload,headers = headers, timeout = 15)
                    

					#SUCCESS KEY IS FOUND
                        if any(successKey in testo_post.text for successKey in keys['success']) and (testo_post.status_code==200):
                         #Function to use if success key is found and we had bypass cloudflare  
                            pass 
                             
                             
                    #FAILURE KEYWORD               
                        elif any(unsuccessKey in testo_post.text for unsuccessKey in keys['unsuccess']) and (testo_post.status_code==200):
                         #Function to use if success key is notfound and we had bypass cloudflare  
                            pass   
                       

                     #BANNED KEYWORD          
                        elif  any(bannedKey in login.text for bannedKey in keys['banned']) or any(bannedKey in testo_post.text for bannedKey in keys['banned']):
                         #Function to use if banned key is found and we had bypass cloudflare  
                            pass 
 
                    
                else:
                    with open('uncaptured_errors.txt','a+') as file:
                        file.write(':'.join(source) + '--> ' + login.text+"\n")                               
                
            except :                    
                    source_lst.append(source)
                    pass    

        return



####################################
###########     MAIN     ###########
####################################
threads=5
threads = input('How many threads ( Default is 5) ?: ')

processes = [] 
end = 0
old_len = len(source_lst) 
process = threading.Thread(target = update) 
process.start()
process = threading.Thread(target = cpm)
process.start()


for t in range(int(threads)): 
    process = threading.Thread(target = get_resp) 
    process.start()
    processes.append(process)

while True:
    
    try: 
        running = 0
        for p in processes: 
            if  p.isAlive():
                running = 1 
            else:
                processes.remove(p) 
        if not running: 
            end = 1
            break
 

        if(len(proxies)) <= 20 :		
		#auto update proxies from the proxy pool
            if(use_auto_proxies==1):    
                screen_lock.acquire()
                with open(proxy_file,'r+') as proxyfile:
                    for line in proxyfile.readlines():
                        proxies.append(line.rstrip()) 
                screen_lock.release()
    
            else:    
                r = requests.get(urlproxies)
                with open("tempf.tmp", 'wb') as f:  
                    f.write(r.content)     
                screen_lock.acquire()
                with open("tempf.tmp",'r') as proxyfile:
                    for line in proxyfile.readlines():
                        proxies.append(line.rstrip()) 
                screen_lock.release() 
                if os.path.exists("tempf.tmp"):    
                    os.remove("tempf.tmp")
                    print("Proxies were updated!")
 
    except KeyboardInterrupt:
        print('Exiting and saving the remaining data...')
        killall=1
        while True:
            running = 0
            for p in processes: 
                if  p.isAlive():
                    running = 1 
                else:
                    processes.remove(p) 
                if not running: 
                    end = 1
                   
                    screen_lock.acquire()    
                    if ( len(source_lst)>=1):
                        with open('remaining_source.txt','w+', encoding="utf8") as file: 
                            for source in source_lst:
                                file.write(source[0]+':'+ source[1] + '\n')
                                screen_lock.release()  
                    break
