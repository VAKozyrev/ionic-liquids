from tqdm import tqdm
import requests
import pandas as pd

#Create a generator of batches by 10id (limit of KEGG for one request)
def ids_batches(ids_list, batch_size=10):
    return [ids_list[i:i+batch_size] for i in range(0, len(ids_list), batch_size)]

if __name__ == '__main__':

    #Get list of all compounds from KEGG
    response = requests.get('https://rest.kegg.jp/list/cpd')
    df_compounds = pd.DataFrame([line.split('\t') for line in response.text.splitlines()], columns=['kegg_id', 'name'])
    df_compounds.to_csv('../data/compounds-list.tsv', sep='\t', index=False)

    #Request db entry and mol file for each compound
    with open('../data/compounds.kegg', 'w') as file:
        for batch in tqdm(ids_batches(df_compounds.kegg_id.tolist()), unit='batch', desc='Retrieving compound entries from KEGG'):
            response = requests.get(f'https://rest.kegg.jp/get/{'+'.join(batch)}')
            file.write(response.text)

    with open('../data/compounds.mol', 'w') as file:
        for batch in tqdm(ids_batches(df_compounds.kegg_id.tolist()), unit='batch', desc='Retrieving compound MolFiles from KEGG'):
            response = requests.get(f'https://rest.kegg.jp/get/{'+'.join(batch)}/mol')
            file.write(response.text)