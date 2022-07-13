from infomap import Infomap
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import os

def read_df(filename):
    __location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

    df = pd.read_csv(os.path.join(__location__, filename),
                    sep=',',
                    header=None,
                    names=['Source', 'Target', 'Weight'])
    return df

def create_nx(df):
    G = nx.from_pandas_edgelist(df, source='Source', target='Target', edge_attr='Weight', create_using=nx.DiGraph())

    nx.draw_networkx(G, with_labels=False, font_size=6, node_size=150)
    plt.show()

    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))

    nx.write_pajek(G, os.path.join(__location__, 'input.net'))

def infomap(filename):
    im = Infomap(silent=True)

    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))

    im.read_file(os.path.join(__location__, filename))

    # Run the Infomap search algorithm to find optimal modules
    im.run()
    im.write_clu(os.path.join(__location__, 'result.clu')) #write .clu file

    print(f"Found {im.num_top_modules} modules with codelength: {im.codelength}")

    print("Result")
    print("\n#node module")
    for node in im.tree:
        if node.is_leaf:
            print(node.node_id, node.module_id)

if __name__ == "__main__":
    filename = "df.csv"
    df = read_df(filename)
    
    create_nx(df)
    
    filename = 'input.net'
    infomap(filename)