import numpy as np
import requests
import re

class Pagelinks_iw:
    def __init__(self, title, stopwords, infoboxes):
        self.URL = "https://en.wikipedia.org/w/api.php"
        self.PARAMS = {
            "action": "query",
            "prop": "links",
            "format": "json",
            "plnamespace": "0",
            "pllimit": "500",       #no redirect for direct links
            "titles": title
        }
        self.PAGES = []
        self.links = []
        self.DATA = []
        self.stopwords = stopwords
        self.infoboxes = infoboxes
        self.infobox = []

    def main(Pagelinks_iw):
        Pagelinks_iw.readData()
        Pagelinks_iw.getLinks()
        Pagelinks_iw.getData()
        #time.sleep(t) -> no need here

    def readData(Pagelinks_iw):
        S = requests.Session()
        R = S.get(url= Pagelinks_iw.URL, params= Pagelinks_iw.PARAMS)
        Pagelinks_iw.DATA = R.json()
        Pagelinks_iw.PAGES = Pagelinks_iw.DATA["query"]["pages"]

    def getLinks(Pagelinks_iw):
        for k, v in Pagelinks_iw.PAGES.items():
            for l in v["links"]:
                try:
                    if Pagelinks_iw.check(l["ns"], l["title"]) == True:         
                        Pagelinks_iw.links.append(l["title"].replace(" ", "_"))
                        print(l["title"])

                        main = Page_infobox(l["title"])
                        main.main()
                        infobox = main.infobox
                        Pagelinks_iw.infobox.append(infobox)

                except:
                    print("nop")
                    
    def getData(Pagelinks_iw):
        while Pagelinks_iw.DATA.get("continue",False): #try to find "continue" if doesn't find return other param (here False-> break while loop)
            pl = Pagelinks_iw.DATA["continue"]["plcontinue"]
            Pagelinks_iw.PARAMS["plcontinue"] = pl
            Pagelinks_iw.readData()
            Pagelinks_iw.getLinks()

    def check(Pagelinks_iw, ns, title):
        check_art = bool(ns == 0) #True
        check_stpwrd = bool([x for x in Pagelinks_iw.stopwords if re.search(x.lower(), title.lower())]) #False
        check_dic = bool(title in Pagelinks_iw.links) #False

        main = Page_infobox(title)
        main.main()
        infobox = main.infobox
        check_infobox = bool([x for x in Pagelinks_iw.infoboxes if re.match(x[8:].lower(), infobox[8:].lower())])   #False

        check = check_art and not check_stpwrd and not check_dic and not check_infobox
        return check #should return True

class Page_infobox:
    def __init__(self, title):
        self.URL = "https://en.wikipedia.org/w/api.php"
        self.PARAMS = {
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "rvprop": "content",
            "titles": title
        }
        self.PAGES = []
        self.DATA = []
        self.infobox = ""

    def main(Page_infobox):
        Page_infobox.readData()
        Page_infobox.getData()

    def readData(Page_infobox):
        S = requests.Session()
        R = S.get(url= Page_infobox.URL, params= Page_infobox.PARAMS)
        Page_infobox.DATA = R.json()
        pages = Page_infobox.DATA["query"]["pages"]
        pageId = list(pages.items())[0][0]
        Page_infobox.PAGES = Page_infobox.DATA["query"]["pages"][pageId]["revisions"][0]["*"]

    def getData(Page_infobox):
        content = Page_infobox.PAGES
        try:
            index = content.index("{{Infobox")
            content2 = content[index:]
            index2 = content2.index("|")                            #{{Infobox __template_name__\n| sometimes not \n so need to check to only keep Infobox __template_name__
            if content2[index2-1:index2] == "\n":
                Page_infobox.infobox = content2[2:index2-1]
            else:
                Page_infobox.infobox = content2[2:index2]
        except:
            pass

def map_input_iw(iwtitle, iteration, stopwords, infoboxes):
    arc = []
    data = []
    data.append(iwtitle)
    label = []

    main = Page_infobox(iwtitle)
    main.main()
    infobox = main.infobox
    label.append(infobox)

    n = 0
    start = 0
    size = np.size(data)
    
    while n < iteration:
        for i in range(start, size):
            try:
                iwtitle = data[i].replace(" ", "_")
                new_links = Pagelinks_iw(iwtitle, stopwords, infoboxes)
                new_links.main()
                new_data = new_links.links
                test = new_links.infobox
                
                for lk in new_data:
                    if not lk.replace(" ", "_") in data:
                        data.append(lk.replace("\"", "\'"))
                        indice = new_data.index(lk)
                        label.append(test[indice])
                        print("yep")
                    if data.index(lk) != i: 
                        arc.append([i, data.index(lk), 1])

            except:
                print("erreur")

        start = size
        size = np.size(data) - size
        n += 1

    return data, np.array(arc).astype(np.float32), label                   #need to convert to np.array for edit weight (float to be flexible with weight val)
