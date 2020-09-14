from ontobio.ontol_factory import OntologyFactory
import obonet, math
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup


ofactory = OntologyFactory()
ont = ofactory.create('go.json')
graph = obonet.read_obo('go.obo')
soup  = BeautifulSoup(open('templates/cellLocation.html', 'r').read(), 'html.parser')

def get_starting_nodes(data):
    node_titles = []
    titles = soup.find_all("g", title=True)
    for title in titles:
        temp = str(title)
        a = temp.find("title")
        b = temp.find(">")
        name = temp[a+7:b-1]
        if name[len(name)-3:] == 'ies':
            name = name[:-3]
            name = name + 'y'
        if name[-1] == 's':
            if name[-2] != 'u':
                name = name[:-1]
        if name[-1] == 'i':
            name = name[:-1]
            name = name + 'us'
        if name[-1] == 'a':
            name = name[:-1]
            name = name + 'on'
        if name.lower() not in node_titles:
            node_titles.append(name.lower())

    name_to_id = {data['name'].lower(): id_ for id_, data in graph.nodes(data=True) if 'name' in data}
    node_ids = []
    for name in node_titles:
        try:
            node_ids.append(name_to_id[name])
        except:
            node_ids.append(None)

    node_titles_np = np.array(node_titles)[np.newaxis]
    node_ids_np = np.array(node_ids)[np.newaxis]

    nodes = np.concatenate((node_titles_np.T, node_ids_np.T),axis=1)

    return nodes, node_titles, node_ids

def bfs(source):
    explored = []
    queue = [source]
    while queue:
        node = queue.pop(0)
        # what if the starting node is None? then ont.children(source) returns nothing
        if node not in explored:
            explored.append(node)
            children = ont.children(node)
            queue.extend(children)
    return explored

def bfs_with_depth(source):
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
                children = ont.children(node)
                queue.extend(children)
            level_size -= 1
        level += 1
    res = np.concatenate(((np.array(explored, dtype='object')[np.newaxis]).T, (np.array(depths)[np.newaxis]).T),
                         axis=1)
    return res

def min_pval(nodes, data):
    pvals = []
    for node in nodes:
        for i in range(len(data[:,0])):
            if node == data[i,0]:
                pvals.append(data[i,4])
    if not pvals:
        return None
    else: 
        return min(pvals)


def get_pvals(starting_node_ids):
    pvals = []
    for node in starting_node_ids:
        pvals.append(min_pval(bfs(node)))
    return pvals


def get_pvals_and_children_with_depth(data, starting_node_ids):
    pvals = np.empty([len(starting_node_ids), 4], dtype='object')
    for i in range(len(starting_node_ids)):
        node = starting_node_ids[i]
        res = bfs_with_depth(node)
        
        pvals[i,0] = min_pval(res[:,0], data)
        for j in range(len(data[:,0])):
            if node == data[j,0]:
                pvals[i,1] = data[j,4]
                break
                
        d = get_graph(node)
        d = goid_to_label_and_pval(d, data)
        d_str = "\n".join(("{}: {}".format(*j) for j in d.items()))
        pvals[i,3] = d_str
        
        non_represented_res = [x for x in res[:,0] if x not in starting_node_ids]
        pvals[i,2] = min_pval(non_represented_res, data)
        
    return pvals

def get_graph(node):
    res = bfs_with_depth(node)
    graph = {}
    for i in range(np.amax(res[:,1]) + 1):
        graph['level ' + str(i)] = [x for ind, x in np.ndenumerate(res[:,0]) 
                                    if res[ind[0],1] == i] 
    return graph

def goid_to_label_and_pval(d, data):
    for k, v in d.items():
        new_v = []
        for x in v:
            lbl = ont.label(x)
            pval = '--'
            for i in range(data.shape[0]):
                if x == data[i,0]:
                    pval = round(data[i,4],6)
            if lbl:
                x = lbl + ", pval = " + str(pval)
            else:
                x = None
            new_v.append(x)
        d.update([(k, new_v)])
    return d

def log_arr(arr, base=10, includeNone=False):
    res = [-math.log(x, base) if x is not None else None for x in arr]
    if includeNone:
        return res #keeps None values
    else: 
        return [x for x in res if x is not None] # removes None values