#librairy for web scraping
from bs4 import BeautifulSoup
import urllib.request
import os

def write(infoboxes):
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))

    filename = "infoboxes.txt"
    f = open(os.path.join(__location__, filename), "w", encoding="utf-8")

    for i in range(len(infoboxes)-1):
        f.write(infoboxes[i][9:] + "\n")
    f.write(infoboxes[-1][9:])

    f.close()

def get_infoboxes():
    page_html = urllib.request.urlopen("https://en.wikipedia.org/wiki/Wikipedia:List_of_infoboxes")
    page_soup = BeautifulSoup(page_html, 'lxml')

    div_tag = page_soup.find('div', {'id': 'mw-content-text'})
    ul_tags = div_tag.find_all('ul')

    infoboxes_scrap = []

    for ul_tag in ul_tags:
        li_tags = ul_tag.find_all('li')
        for li_tag in li_tags:
            try:
                infoboxes_scrap.append(li_tag.a.get('title'))
            except:
                pass

    infoboxes = []
    for i in infoboxes_scrap:
        try:
            if i[:17] == "Template:Infobox ":
                infoboxes.append(i)
        except:
            pass

    return infoboxes

infoboxes = get_infoboxes()
write(infoboxes)