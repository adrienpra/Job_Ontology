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
filename = "links.txt"

#__main__

if __name__=="__main__":
    tps_start = time.time()

    #get inputs
    stopwords = read_file("stopwords.txt")
    infoboxes = read_file("infoboxes.txt")
    titles = sort_map_input(titles, stopwords, infoboxes)
    print(titles)
    
    #process inputs: wiki-api scrap
    p = mp.Pool()
    result_bl = p.map(partial(map_input_bl, iteration=iteration, stopwords=stopwords, infoboxes=infoboxes), titles)
    p.close()
    
    q = mp.Pool()
    result_iw = q.map(partial(map_input_iw, iteration=iteration, stopwords=stopwords, infoboxes=infoboxes), titles)
    q.close()
    
    #merge result
    result = result_bl + result_iw
    data, arc, label = zip(*result)
    data, arc, label = merge_map_input(data, arc, label)

    #write result
    writeData(data, arc, label, filename)

    tps_end = time.time()
    print("tps =", tps_end - tps_start)