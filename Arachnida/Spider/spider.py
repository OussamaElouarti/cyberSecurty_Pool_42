#!/usr/bin/env python3

import sys
import urllib.request
from urllib.parse import urlparse
import os
from bs4 import BeautifulSoup as BSHTML
import ssl
import requests

class target:
    ip=""
    images=[]
    level=5
    rec=False
    path = "data"
    links=[]


def checkOptions():
    t = target()
    i = 1
    while(i<len(sys.argv)):
        if '-' == sys.argv[i][0]:
            if sys.argv[i][1] == 'r':t.rec=True;i+=1
            elif sys.argv[i][1] == 'l':t.level = int(sys.argv[i+1]);i+=2
            elif sys.argv[i][1] == 'p':t.path = sys.argv[i+1];i+=2
            else:print(sys.argv[i]+" is a Bad option");exit()
        else:
            if len(t.ip) != 0:print("bad format\nUsage ./spider [-rlp] URL");exit()
            else:
                result = urlparse(sys.argv[i])
                if result.scheme  and result.netloc:t.ip = sys.argv[i]
                else:print("Invalid target");exit()
            i+=1
    return t


def debug(t):
    print("ip "+t.ip)
    print(*t.images)
    print(t.level)
    print(t.path)
    print(t.rec)


def GetImages(ip):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    l=[]
    req = urllib.request.Request(ip, None, headers={"User-Agent": "Mozilla/5.0"})
    try:
        fp = urllib.request.urlopen(req, context=ctx)
    except urllib.error.HTTPError as err:
        # print(f'A HTTPError was thrown: {err.code} {err.reason}')
        return(l)
    mybytes = fp.read()
    page = mybytes.decode("utf8")
    fp.close()
    soup = BSHTML(page,features="html.parser")
    images = soup.findAll('img')
    for image in images:
        src = image.get("src")
        if src:
            if src.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')) == False:continue
            # resolve any relative urls to absolute urls using base URL
            src = requests.compat.urljoin(ip, src)

            l+=[src]
    return(l)


def getLinks(ip):
    l=[]
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(ip, None, headers={"User-Agent": "Mozilla/5.0"})
    try:
        fp = urllib.request.urlopen(req, context=ctx)
    except urllib.error.HTTPError as err:
        # print(f'A HTTPError was thrown: {err.code} {err.reason}')
        return(l)
    mybytes = fp.read()
    page = mybytes.decode("utf8")
    fp.close()
    soup = BSHTML(page,features="html.parser")
    links = soup.findAll('a')
    for link in links:
        href = link.get("href")
        href = requests.compat.urljoin(ip, href)
        l+=[href]
    return(l)


def parseImage(images, path):
    parent_dir = "/Users/oel-ouar/Desktop/Arachnida/Spider/"
    path = os.path.join(parent_dir,path)
    isExist = os.path.exists(path)
    if isExist == False:os.mkdir(path)
    for i in images:
        with open(path+i[i.rfind('/'):], 'wb') as handle:
            response = requests.get(i, stream=True)
            if not response.ok:
                print(response)
            for block in response.iter_content(1024):
                if not block:
                    break
                handle.write(block)

def recu(ip, depth, path):
    images = GetImages(ip)
    links = getLinks(ip)
    parseImage(images, path)
    if depth < 0:return
    if links:
        for i in range(len(links)):
            recu(links[i],depth-1,path)


def main():
    if len(sys.argv) ==1 or len(sys.argv) > 7:
        print('Usage ./spider [-rlp] URL');exit()
    else:
        Mytarget = checkOptions()
        if Mytarget.rec == True:
            print("--Starting--")
            images = GetImages(Mytarget.ip)
            links = getLinks(Mytarget.ip)
            parseImage(Mytarget.images, Mytarget.path)
            for link in links:
                recu(link,Mytarget.level, Mytarget.path)
        else:
            print("--Starting--")
            Mytarget.images = GetImages(Mytarget.ip)
            if len(Mytarget.images) == 0:print("No images in this website");exit()
            parseImage(Mytarget.images, Mytarget.path)
        print("--DONE--")


if __name__ == "__main__":
    main()