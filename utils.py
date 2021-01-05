import os
import pandas as pd
import numpy as np
import simplejson
from orangecontrib.bio.ontology import OBOOntology
from gene_ontology_module import *

def generate_json(file_csv, short=True):
    """
    Generates json file from csv input

    short form attributes:
        'Title', 'ID', 'min_pval', 'log_min_pval', 'interpolate'
    
    long form attributes:
        'Title', 'ID', 'min_pval', 'log_min_pval', 'interpolate', 
        'init_pval', 'min_pval_children', 'descendants'

    Inputs:
    - file_csv: N x 5 .csv file; columns are GO id, GO name/label, Count DE, Count All, and Pval
    - short: boolean, determines if json generated is in short or long form (default is True)

    Outputs:
    - localPath: str, path of output file
    - fileName: str, file name of json output, formatted as "{}.json"

    """
    data = pd.read_csv(file_csv).to_numpy()
    obi = OBOOntology('files/go.obo')
    starting_nodes, starting_node_titles, starting_node_ids = get_starting_nodes(obi, data)
    final_pvals = get_pvals_and_children_with_depth(obi, data, starting_node_ids)
    log_min_pvals = log_arr(final_pvals[:,0].tolist(), includeNone=True)

    max_log_min_pval = 0
    for value in log_min_pvals:
        if value and value > max_log_min_pval:
            max_log_min_pval = value
    # print(max_log_min_pval)

    max_log_min_pval = max(log_arr(final_pvals[:,0].tolist()))
    interpolate_vals = np.array([round(x / max_log_min_pval, 6) if x is not None else None for x in log_min_pvals])[:, np.newaxis]
    final_pvals = np.concatenate(
        [   
            final_pvals[:,:-3],
            np.array(log_min_pvals)[:, np.newaxis],
            interpolate_vals,
            final_pvals[:,-3:-1],
            final_pvals[:,-1][:,np.newaxis]
        ], 
        axis=1
    )

    final = np.concatenate((starting_nodes, final_pvals), axis=1)
    for i, n in np.ndenumerate(final[:,0]):
        final[i[0],0] = n.replace(' ', '_')
    final_dataset = pd.DataFrame(
        {
            "Title": final[:,0],
            "ID": final[:,1],
            "min_pval": final[:,2],
            "log_min_pval": final[:,3], 
            "interpolate": final[:,4],
            "init_pval": final[:,5], 
            "min_pval_children": final[:,6],
            "descendants": final[:,-1]
        }
    )
    csv_name = file_csv.split("/")[-1]
    csv_table_name = "to_plunker_" + csv_name
    final_dataset.to_csv(csv_table_name, index = False)
    plunker_inputs = pd.read_csv(csv_table_name).to_numpy()
    os.remove(csv_table_name);
    
    if short:
        json_form = ""
        json_attrs = ["Title", "ID", "min_pval", "log_min_pval", "interpolate"]
    else:
        json_form = "_long"
        json_attrs = ["Title", "ID", "min_pval", "log_min_pval", "interpolate", "init_pval",
                  "min_pval_children", "descendants"]

    json_data = [{x: plunker_inputs[i,j] for (j, x) in enumerate(json_attrs)}
                    for i in range(plunker_inputs.shape[0])]

    json_data = simplejson.dumps(json_data, ignore_nan=True)
    return json_data

if __name__ == "__main__" :
    file_csv = "files/csv_files/melanoma.csv"
    json_data = generate_json(file_csv = file_csv, short = True)
    print(json_data)