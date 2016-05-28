#!/usr/bin/python
# -!- encoding:utf8 -!-

import requests

PAGES=10
BASE_URL="http://data.grandlyon.com/localisation/?P="
RESULTS=[]


for i in range(PAGES):
    print "> retrieving page %s" % i
    page = requests.get("%s%s" % (BASE_URL, i)).content
    print "> parsing page..."
    result_items = page.split('class="result_item"')
    for item in result_items:
        if 'class="result_item_title">' in item:
            RESULTS.append(item.split('class="result_item_title">')[1].split("</a>")[0].split('>')[1])
    print "> done !"

for res in RESULTS:
    print "---------------------------\n%s" % res




