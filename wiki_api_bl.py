import numpy as np
import requests
import re
import os

class Pagelinks_bl:
    def __init__(self, title, stopwords):
        self.URL = "https://en.wikipedia.org/w/api.php"
        self.PARAMS = {
            "action": "query",
            "format": "json",
            "list": "backlinks",
            "bllimit": "250",       #bllimit 250 due to blredirect (instead of 500)
            "blredirect": "",
            "bltitle": title
        }
        self.PAGES = []
        self.links = []
        self.DATA = []
        self.stopwords = stopwords

    def main(Pagelinks_bl):
        Pagelinks_bl.readData()
        Pagelinks_bl.getLinks()
        Pagelinks_bl.getData()
        #time.sleep(t) -> no need here

    def readData(Pagelinks_bl):
        S = requests.Session()
        R = S.get(url= Pagelinks_bl.URL, params= Pagelinks_bl.PARAMS)
        Pagelinks_bl.DATA = R.json()
        Pagelinks_bl.PAGES = Pagelinks_bl.DATA["query"]["backlinks"]

    def getLinks(Pagelinks_bl):
        for b in Pagelinks_bl.PAGES:
            try:
                b["redirect"]
                try:
                    c = b["redirlinks"]
                    for d in c:
                        if Pagelinks_bl.check(d["ns"], d["title"].replace(" ", "_")) == True:
                            Pagelinks_bl.links.append(d["title"].replace(" ", "_"))
                            print(b["title"])
                except:
                    pass
            except:
                if Pagelinks_bl.check(b["ns"], b["title"].replace(" ", "_")) == True:
                    Pagelinks_bl.links.append(b["title"].replace(" ", "_"))
                    print(b["title"])
                else:
                    print("nop")

    def getData(Pagelinks_bl):
        while Pagelinks_bl.DATA.get("continue",False): #try to find "continue" if doesn't find return other param (here False-> break while loop)
            pl = Pagelinks_bl.DATA["continue"]["blcontinue"]
            Pagelinks_bl.PARAMS["blcontinue"] = pl
            Pagelinks_bl.readData()
            Pagelinks_bl.getLinks()

    def check(Pagelinks_bl, ns, title):
        check_art = bool(ns == 0) #True
        check_stpwrd = bool([x for x in Pagelinks_bl.stopwords if re.search(x.replace(" ","_").lower(), title.lower())]) #False
        check_dic = bool(title in Pagelinks_bl.links) #False

        check = check_art and not check_stpwrd and not check_dic
        return check #should return True

#Read file function: input:filename (1 colonne, no punct) / output array (n,1)
def read_file(filename):
    __location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

    f = open(os.path.join(__location__, filename), "r", encoding="utf-8")
    file = f.read().splitlines()

    return file

def map_input(bltitle, iteration, stopwords):
    arc = []
    data = []
    data.append(bltitle)

    n = 0
    start = 0
    size = np.size(data)

    while n < iteration:
        for i in range(start, size):
            try:
                bltitle = data[i].replace(" ", "_")
                new_links = Pagelinks_bl(bltitle, stopwords)
                new_links.main()
                new_data = new_links.links

                for lk in new_data:
                    if not lk.replace(" ", "_") in data:
                        data.append(lk.replace("\"", "\'"))
                    if data.index(lk) != i: 
                        arc.append([data.index(lk), i, 1])   

            except:
                print("erreur")

        start = size
        size = np.size(data) - size
        n += 1

    return data, np.array(arc).astype(np.float32)                   #need to convert to np.array for edit weight (float to be flexible with weight val)

def merge_map_input(bltitles, iteration, stopwords):

    data0, arc0 = map_input(bltitles[0], iteration, stopwords)

    for bltitle in bltitles[1:]:
        change = []
        data1, arc1 = map_input(bltitle, iteration, stopwords)

        for title in data1:
            if title in data0:
                change.append(data0.index(title))
            else:
                change.append(len(data0))
                data0.append(title)

        for arc in arc1:
            arc[0] = change[arc[0].astype(np.int32)]                    #array index must be int not float
            arc[1] = change[arc[1].astype(np.int32)]

            if (arc[:2] == arc0[:,:2]).all(1).any() == True:                    #if already exist arc statement : just look source target not weight
                indice = np.where((arc[:2] == arc0[:,:2]).all(1))[0][0]             #Get index in arc0 where connection already exist to change it
                arc0[indice][2] += 0.5                                              #Define what weight to add
            else:
                arc0 = np.append(arc0, [arc], axis=0)                           #else not already exist then append it

    arc0 = arc0[arc0[:,0].argsort()]                                            #sort arc0 output through first column
    return data0, arc0

def writeData(data, arc, filename):
    __location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

    f = open(os.path.join(__location__, filename), "w", encoding="utf-8")
    f.write("*Vertices " + str(len(data)) + "\n")
    f.write("# node_id name " + str(len(data)) + "\n")

    for i in data:
        f.write(str(data.index(i)) + " \"{}\"".format(i) + "\n")

    f.write("*Arcs " + str(len(arc)) + "\n")
    f.write("# source target weight" + "\n")

    for i in range(len(arc)-1):
        f.write(str(arc[i][0].astype(np.int32)) + " " + str(arc[i][1].astype(np.int32)) + " " + str(arc[i][2]) + "\n")      #need to convert arc[0] and [1] to int 'cause nodes
    f.write(str(arc[-1][0].astype(np.int32)) + " " + str(arc[-1][1].astype(np.int32)) + " " + str(arc[-1][2]))

    f.close()