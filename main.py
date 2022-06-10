from wiki_api_bl import map_input
from wiki_api_bl import writeData
from wiki_api_bl import read_file
from wiki_api_bl import merge_map_input

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

    if len(titles) == 1:
        data, arc = map_input(titles[0], iteration, stopwords)      #One search
    else:
        data, arc = merge_map_input(titles, iteration, stopwords)   #Multiple searches

    writeData(data, arc, filename)
    tps_end = time.time()
    print("tps =", tps_end - tps_start)