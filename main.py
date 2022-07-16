from wiki_api_bl import read_file
from wiki_api_bl import map_input_bl
from wiki_api_iw import map_input_iw
from wiki_api_bl import merge_map_input
from wiki_api_bl import writeData
from wiki_api_bl import sort_map_input

import multiprocessing as mp
from functools import partial
import time

#__inputs__
titles = read_file("map_input_IT.txt")
iteration = 1

if len(titles) == 1:
    filename = "links_" + titles[0] + ".txt"
else:
    filename = "links.txt"

#__main__

if __name__=="__main__":
    tps_start = time.time()

    stopwords = read_file("stopwords.txt")
    infoboxes = read_file("infoboxes.txt")
    titles = sort_map_input(titles, stopwords, infoboxes)
    print(titles)
    
    if len(titles) == 1:
        data_bl, arc_bl, label_bl = map_input_bl(titles[0], iteration, stopwords, infoboxes)      #One search in links
        data_iw, arc_iw, label_iw = map_input_iw(titles[0], iteration, stopwords, infoboxes)      #One search out links

        data = [data_bl] + [data_iw]
        arc = [arc_bl] + [arc_iw]
        label = [label_bl] + [label_iw]
        
    else:
        p = mp.Pool()
        result_bl = p.map(partial(map_input_bl, iteration=iteration, stopwords=stopwords, infoboxes=infoboxes), titles)
        p.close()
        
        q = mp.Pool()
        result_iw = q.map(partial(map_input_iw, iteration=iteration, stopwords=stopwords, infoboxes=infoboxes), titles)
        q.close()
 
        result = result_bl + result_iw
        data, arc, label = zip(*result)
        data, arc, label = merge_map_input(data, arc, label)

    writeData(data, arc, label, filename)

    tps_end = time.time()
    print("tps =", tps_end - tps_start)