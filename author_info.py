import json
import pandas as pd
from tqdm.auto import tqdm
from scholarly import scholarly

from utils import random_sleep, str2list


def get_author_data(pub_data, save_path=None):
    '''
    Lalala

    '''
    # Create an empty author_data DataFrame
    author_columns  = ["Author ID", "Author Name", "Affiliation",
                       "Author Cited By", "h-index", "i10-index",
                       "Email Domain", "Interests"]
    author_data = pd.DataFrame(columns=author_columns)

    # Remove empty entries that have no author info
    pub_data = pub_data.dropna(subset=['Author Names'])

    # Read author names and IDs from previous step pub_data
    author_names_list = pub_data['Author Names']
    author_ids_list = pub_data['Author IDs']
    assert len(author_names_list) == len(author_ids_list)

    # Loop through the list of author names and IDs, get author info
    print("Start getting author data ...")
    for author_names, author_ids in tqdm(zip(author_names_list, author_ids_list),
                                         total=len(author_names_list)):
        # Convert string from CSV to proper lists
        author_names = str2list(author_names)
        author_ids = str2list(author_ids)
        # Make sure for each pub, we have same number of author names and ids
        assert len(author_names) == len(author_ids)

        for author_name, author_id in zip(author_names, author_ids):
            if len(author_id) == 0:
                # If author ID not available, just use the name
                author = {}
                author['name'] = author_name
            else:
                # Skip authors with ID already in author_data
                if author_id in author_data['Author ID']:
                    continue
                # If author ID is available, search that ID to get more info
                author = scholarly.search_author_id(author_id)
                random_sleep(min_sec=1, max_sec=5)
                # Fill for index and cites info
                author = scholarly.fill(author, sections=['indices'])
                random_sleep(min_sec=1, max_sec=5)

            author_data = append_author_row(author_data, author)
            if save_path:
                author_data.to_csv(save_path, index=False)
    return author_data


def append_author_row(author_data, author):
    '''
    Lalala

    '''
    # Get attribute from author dictionary
    author_name = author.get('name', '')
    author_id = author.get('scholar_id', '')
    affiliation = author.get('affiliation', '')
    cited_by = author.get('citedby', '')
    hindex = author.get('hindex', '')
    i10index = author.get('i10index', '')
    email = author.get('email_domain', '')
    interests = author.get('interests', '')

    # Create a new row with extracted info
    new_row = {# Author attributes
                "Author ID": author_id, "Author Name": author_name,
                "Affiliation": affiliation, "Author Cited By": cited_by,
                "h-index": hindex, "i10-index": i10index,
                "Email Domain": email, "Interests": interests}
    return author_data.append(new_row, ignore_index=True)


def get_author_cites_per_year(author_data, save_json_path=None):
    author_cites_per_year = {} # { author_id: {year: cites_per_year} }

    # Remove empty entries that have no author info
    author_data = author_data.dropna(subset=['Author ID'])

    # Iterate rows of the author_data
    print("Start getting author_cites_per_year ...")
    for idx, row in tqdm(author_data.iterrows(), total=len(author_data)):
        author_id = row['Author ID']

        author = scholarly.search_author_id(author_id)
        random_sleep(min_sec=1, max_sec=5)
        author = scholarly.fill(author, sections=['counts'])
        random_sleep(min_sec=1, max_sec=5)

        # Look for author_cites_per_year using author_id
        author_cites_per_year[author_id] = author['cites_per_year']
        if save_json_path:
            with open(save_json_path, 'w') as f:
                json.dump(author_cites_per_year, f)
    
    return author_cites_per_year
