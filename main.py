from wiki_api_bl import read_file
from wiki_api_bl import map_input
from wiki_api_bl import merge_map_input
from wiki_api_bl import writeData

import multiprocessing as mp
from functools import partial
import time

#__inputs__
titles = read_file("map_input_IT.txt")
iteration = 1

if len(titles) == 1:
    filename = "bllinks_" + titles[0] + ".txt"
else:
    filename = "bllinks.txt"

#__main__

if __name__=="__main__":
    tps_start = time.time()

    stopwords = read_file("stopwords.txt")
    infoboxes = read_file("infoboxes.txt")

    if len(titles) == 1:
        data, arc, label = map_input(titles[0], iteration, stopwords, infoboxes)      #One search
    else:
        print(titles)
        p = mp.Pool()
        result = p.map(partial(map_input, iteration=iteration, stopwords=stopwords, infoboxes=infoboxes), titles)
        data, arc, label = zip(*result) #unzip result give tuples of array (n array for n titles)
        #data, arc, label = merge_map_input(titles, iteration, stopwords, infoboxes)   #Multiple searches
        data, arc, label = merge_map_input(data, arc, label)
        
    print(data)
    writeData(data, arc, label, filename)

    tps_end = time.time()
    print("tps =", tps_end - tps_start)