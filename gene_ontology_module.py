import math
import numpy as np
from orangecontrib.bio.ontology import OBOOntology
# from bs4 import BeautifulSoup


obi = OBOOntology('files/go.obo')

def get_starting_nodes(data):
    """
    Gets the starting node titles from an html template and the corresponding ids from a csv input

    Inputs:
    - data: N x 5 numpy array; columns are GO id, GO name/label, Count DE, Count All, and Pval

    Outputs:
    - nodes: N x 2 numpy array; columns are node titles and node id
    - node_titles: size N numpy array
    - node_id: size size N numpy array
    """
    # node_titles = []

    # titles = soup.find_all("g", title=True)
    # for title in titles:
    #     temp = str(title)
    #     a = temp.find("title")
    #     b = temp.find(">")
    #     name = temp[a+7:b-1]
    #     if name[len(name)-3:] == 'ies':
    #         name = name[:-3]
    #         name = name + 'y'
    #     if name[-1] == 's':
    #         if name[-2] != 'u':
    #             name = name[:-1]
    #     if name[-1] == 'i':
    #         name = name[:-1]
    #         name = name + 'us'
    #     if name[-1] == 'a':
    #         name = name[:-1]
    #         name = name + 'on'
    #     if name.lower() not in node_titles:
    #         node_titles.append(name.lower())

    # print(node_titles)

    node_titles = [
        "cytosol", 
        "intermediate filament", 
        "actin filament", 
        "focal adhesion site", 
        "microtubule organizing center", 
        "centrosome", 
        "microtubule", 
        "microtubule end", 
        "secreted protein", 
        "lipid droplet", 
        "lysosome", 
        "peroxisome", 
        "endosome", 
        "endoplasmic reticulum", 
        "golgi apparatus", 
        "nucleoplasm", 
        "nuclear membrane", 
        "nuclear body", 
        "nuclear speckle", 
        "nucleolus", 
        "nucleoli fibrillar center", 
        "rods and ring", 
        "mitochondrion", 
        "plasma membrane"
    ]

    map_label_to_id = {term.name : term.id for term in obi.terms()}
    node_ids = []
    for name in node_titles:
        try:
            node_ids.append(map_label_to_id[name])
        except:
            node_ids.append(None)

    node_titles_np = np.array(node_titles)[np.newaxis]
    node_ids_np = np.array(node_ids)[np.newaxis]

    nodes = np.concatenate((node_titles_np.T, node_ids_np.T),axis=1)

    return nodes, node_titles, node_ids

def search_children_with_depth(source):
    level = 0
    depths = []
    explored = []
    queue = [source]
    while queue:
        level_size = len(queue)
        while level_size > 0:
            node = queue.pop(0)
            if node not in explored:
                explored.append(node)
                depths.append(level)
                children = obi.child_terms(node)
                children = [child.id for child in children]
                queue.extend(children)
            level_size -= 1
        level += 1
    explored_with_depth = np.concatenate(((np.array(explored, dtype='object')[np.newaxis]).T, (np.array(depths)[np.newaxis]).T),
                         axis=1)
    return explored_with_depth

def get_pvals_and_children_with_depth(data, starting_node_ids):
    pvals = np.empty([len(starting_node_ids), 4], dtype='object')
    for i in range(len(starting_node_ids)):
        node = starting_node_ids[i]
        children_with_depth = search_children_with_depth(node)
        
        pvals[i,0] = min_pval(children_with_depth[:,0], data)
        for j in range(len(data[:,0])):
            if node == data[j,0]:
                pvals[i,1] = data[j,4]
                break
        
        non_represented_children = [x for x in children_with_depth[:,0] if x not in starting_node_ids]
        pvals[i,2] = min_pval(non_represented_children, data)
                        
        graph = map_graph_level_with_children(data, children_with_depth)
        str_graph = "\n".join(("{}: {}".format(*j) for j in graph.items()))
        pvals[i,3] = str_graph        
    return pvals

def map_graph_level_with_children(data, children_with_depth):
    def map_id_to_label_and_pval(id):
        label = obi.term(id).name
        mask = data[:,0] == id
        pval = '--'
        if data[mask,:].shape[0] == 1: 
            pval = str(round(data[mask,:][0,4], 6))
        if label:
            return f"{label}, pval = {pval}"
        return None
    
    graph = {}
    for i in range(np.amax(children_with_depth[:,1]) + 1):
        mask = children_with_depth[:,1] == i
        children = children_with_depth[mask,:][:,0].tolist()
        graph['level ' + str(i)] = [map_id_to_label_and_pval(child) for child in children if child]
    return graph

def log_arr(arr, base=10, includeNone=False):
    """
    Takes the negative log of each element of a list of ints or floats

    Inputs:
    - arr: list, must be type int or float
    - base: int, log base (default is 10)
    - includeNone: boolean, True if want to return None values, False is default

    Outputs:
    - list that is negative log of each element of arr 
    """
    res = [-math.log(x, base) if x is not None else None for x in arr]
    if includeNone:
        return res #keeps None values
    else: 
        return [x for x in res if x is not None] # removes None values

def min_pval(nodes, data):
    """
    Returns the mininum p value from a list of nodes
    
    Inputs:
    - nodes: list of GO id strings
    - data: N x 5 numpy array; columns are GO id, GO name/label, Count DE, Count All, and Pval

    Outputs:
    - min(pvals): float that represents the minimum p value from the input nodes list
    """
    pvals = []
    for node in nodes:
        for i in range(len(data[:,0])):
            if node == data[i,0]:
                pvals.append(data[i,4])
    if not pvals:
        return None
    else: 
        return min(pvals)