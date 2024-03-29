import numpy as np
import requests
import re
import os
import pandas as pd

import networkx as nx

class Pagelinks_bl:
    def __init__(self, title, stopwords, infoboxes):
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
        self.infoboxes = infoboxes
        self.infobox = []

    def main(Pagelinks_bl):
        Pagelinks_bl.readData()
        Pagelinks_bl.getLinks()
        Pagelinks_bl.getData()

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
                            print(d["title"])

                            main = Page_infobox(d["title"])
                            main.main()
                            infobox = main.infobox
                            Pagelinks_bl.infobox.append(infobox)
                except:
                    pass
            except:
                if Pagelinks_bl.check(b["ns"], b["title"].replace(" ", "_")) == True:
                    Pagelinks_bl.links.append(b["title"].replace(" ", "_"))
                    print(b["title"])

                    main = Page_infobox(b["title"].replace(" ", "_"))
                    main.main()
                    infobox = main.infobox
                    Pagelinks_bl.infobox.append(infobox)
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

        main = Page_infobox(title)
        main.main()
        infobox = main.infobox
        check_infobox = bool([x for x in Pagelinks_bl.infoboxes if re.match(x[8:].lower(), infobox[8:].lower())])   #False

        check = check_art and not check_stpwrd and not check_dic and not check_infobox
        return check        #should return True

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

#Read file function: input:filename (1 colonne, no punct) / output array (n,1)
def read_pajek_file(filename):  #function to be done (check shape of vars)
    
    G = nx.read_pajek(filename, encoding='utf-8')
    df = nx.to_pandas_edgelist(G)

    data2 = list(df['source']) + list(df['target'])
    data = list(set(data2))

    arc= []

    for i in range(len(df)):
        arc.append([data.index(df.iloc[i][0]), data.index(df.iloc[i][1]), df.iloc[i][2]])

    label = []
    for i in range(len(data)):
        label.append('')

    data = [i.replace("%27", "'") for i in data]

    return data, np.array(arc).astype(np.float32), label

def read_file(filename):
    __location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

    f = open(os.path.join(__location__, filename), "r", encoding="utf-8")
    file = f.read().splitlines()

    return file

def sort_map_input(titles, stopwords, infoboxes):
    dic = {}

    for title in titles:
        page = Pagelinks_bl(title, stopwords, infoboxes)
        page.readData()
        dic[title] = len(page.PAGES)
    
    dic = dict(sorted(dic.items(), key=lambda x:x[1]))
    sorted_titles = list(dic.keys())

    return sorted_titles #took all links no filter

def map_input_bl(bltitle, iteration, stopwords, infoboxes):
    arc = []
    data = []
    data.append(bltitle)
    label = []

    main = Page_infobox(bltitle)
    main.main()
    infobox = main.infobox
    label.append(infobox)

    n = 0
    start = 0
    size = np.size(data)

    while n < iteration:
        for i in range(start, size):
            try:
                bltitle = data[i].replace(" ", "_")
                new_links = Pagelinks_bl(bltitle, stopwords, infoboxes)
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
                        arc.append([data.index(lk), i, 1])

            except:
                print("erreur")

        start = size
        size = np.size(data) - size
        n += 1

    return data, np.array(arc).astype(np.float32), label                   #need to convert to np.array for edit weight (float to be flexible with weight val)

def merge_map_input(data, arcs, labels):

    data = list(data)
    arcs = list(arcs)
    labels = list(labels)

    for i in range(len(data)-1):
        change = []

        for title in data[i+1]:
            if title in data[0]:
                change.append(data[0].index(title))
            else:
                change.append(len(data[0]))
                data[0].append(title)
                labels[0].append(labels[i+1][data[i+1].index(title)])

        for arc in arcs[i+1]:
            arc[0] = change[arc[0].astype(np.int32)]                    #array index must be int not float
            arc[1] = change[arc[1].astype(np.int32)]

            if (arc[:2] == arcs[0][:,:2]).all(1).any() == True:                    #if already exist arc statement : just look source target not weight
                indice = np.where((arc[:2] == arcs[0][:,:2]).all(1))[0][0]             #Get index in arc0 where connection already exist to change it
                arcs[0][indice][2] += 0.5                                              #Define what weight to add
            else:
                arcs[0] = np.append(arcs[0], [arc], axis=0)                           #else not already exist then append it

    arcs[0] = arcs[0][arcs[0][:,0].argsort()]                                            #sort arc0 output through first column
    return data[0], arcs[0], labels[0]

def weight_arc(data, arc, filename):
    
    file = read_file(filename)
    x = [[line.split()[0], line.split()[1], line.split()[2]] for line in file]
    sources, targets, weights = zip(*x) #output 3 tuples
    
    for i in range(len(sources)):
        try:
            source_idx = float(data.index(sources[i]))
            target_idx = float(data.index(targets[i]))
            weight_dft = 1.0
            
            source_idx = np.float32(source_idx)
            target_idx = np.float32(target_idx)
            weight_dft = np.float32(weight_dft)
            
            for j in range(len(arc)):
                if ([source_idx, target_idx, weight_dft] == arc[j]).all(0):
                    arc[j][2] = np.float(weights[i])
                    
            for k in range(len(arc)):
                if ([target_idx, source_idx, weight_dft] == arc[k]).all(0):
                    arc[k][2] = np.float(weights[i])                      
        except:
            pass
    return arc
    
def writeData(data, arc, labels, filename):

    #list input infomap_online write txt

    __location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

    f = open(os.path.join(__location__, filename), "w", encoding="utf-8")
    f.write("*Vertices " + str(len(data)) + "\n")
    f.write("# node_id name " + str(len(data)) + "\n")

    for i in data:
        f.write(str(data.index(i)) + " {}".format(i) + "\n")

    f.write("*Arcs " + str(len(arc)) + "\n")
    f.write("# source target weight" + "\n")

    for i in range(len(arc)-1):
        f.write(str(arc[i][0].astype(np.int32)) + " " + str(arc[i][1].astype(np.int32)) + " " + str(arc[i][2]) + "\n")      #need to convert arc[0] and [1] to int 'cause nodes
    f.write(str(arc[-1][0].astype(np.int32)) + " " + str(arc[-1][1].astype(np.int32)) + " " + str(arc[-1][2]))
    f.close()

    #list lables write txt

    f2 = open(os.path.join(__location__, "labels.txt"), "w", encoding="utf-8")
    for label in labels:
        f2.write(label + "\n")
    f2.close()
    
    #pd dataframe write csv

    source_in, target_out, weight = zip(*arc)

    source = [data[int(i)] for i in source_in]
    target = [data[int(i)] for i in target_out]

    weight = list(weight)
    weight = [str(i) for i in weight]
    weight = tuple(weight)

    Dic = {'source': source, 'target':target, 'weight':weight}
    df = pd.DataFrame(Dic)

    df.to_csv(os.path.join(__location__, 'df.csv'), header=False, index=False, encoding='utf-8')