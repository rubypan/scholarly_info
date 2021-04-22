import json
import pandas as pd
from tqdm.auto import tqdm
from scholarly import scholarly

from utils import random_sleep, str2list


def search_by_title(title_list, save_path=None):
    '''
    Search by title.

    [Args]
    '''
    # Create an empty pub_data DataFrame
    pub_columns = ['Title', 'Author Names', 'Author IDs', 'Year', 'Venue',
                   'URL', 'Pub Cites', 'Pub ID']
    pub_data = pd.DataFrame(columns=pub_columns)

    # Search each title on Google Scholar.
    print("Start searching by title ...")
    for title in tqdm(title_list):
        print(f'Searching for publication: "{title}"')
        # Keep trying if got Google not fetch; proceed once succeed
        while True:
            try:
                search_query = scholarly.search_pubs(title)
                break
            except:
                print("Google denied request - retry after 60-100 seconds ...")
                random_sleep(min_sec=60, max_sec=100) # sleep longer if failed
        random_sleep(min_sec=1, max_sec=5) # short sleep if succeeded

        try:
            pub = next(search_query)
        except StopIteration:
            # Entry not found; create an empty pub dict with only title
            # pub = {'bib': {'title': title}}
            bib = {'title': title}
            pub = {'bib': bib}
            pub_data = append_pub_row(pub_data, pub) # not found
            continue

        if len(pub['author_id']) == 0:
            print('No author ID found, skip current title')
        else:
            pub_data = append_pub_row(pub_data, pub)
            if save_path:
                pub_data.to_csv(save_path, index=False)
    return pub_data


def append_pub_row(pub_data, pub):
    '''
    Append a row to pub_data Data Frame.
    Notice that we do not have Pub ID available yet, need to wait for author
    information fill.

    '''
    # Get attribute from publication dict; if not exist, use empty string
    bib = pub.get('bib', {})
    title = bib.get('title', '')
    author_names = bib.get('author', '')
    author_ids = pub.get('author_id', '')
    year = bib.get('pub_year', '')
    venue = bib.get('venue', '')
    url = pub.get('pub_url', '')
    pub_cites = pub.get('num_citations', '')

    # Create a new row with extracted info
    new_row = {# Pub attributes
               "Title": title,
               "Author Names": author_names, "Author IDs": author_ids,
               "Year": year, "Venue": venue, "URL": url, "Pub Cites": pub_cites,
               "Pub ID": ''}
    return pub_data.append(new_row, ignore_index=True)


def get_pub_cites_per_year(pub_data, save_csv_path=None, save_json_path=None):
    '''

    '''
    # Remove empty entries that have no author info
    pub_data = pub_data.dropna(subset=['Author IDs'])

    pub_cites_per_year = {} # { pub_id: {year: cites_per_year} }

    # Iterate rows of the pub_data
    print("Start getting pub_cites_per_year ...")
    for idx, row in tqdm(pub_data.iterrows(), total=len(pub_data)):
        title = row['Title']
        year = row['Year']
        author_ids = row['Author IDs']
        author_ids = str2list(author_ids)

        # Re-initiate the value of pub_id
        pub_id = None

        # For each row, iterate multiple author_id until find pub_id
        for author_id in author_ids:
            # Skip empty author ID
            if len(author_id) == 0:
                continue

            # Get the author dict and fill that author's publication data
            author = scholarly.search_author_id(author_id)
            random_sleep(min_sec=1, max_sec=5)
            author = scholarly.fill(author, sections=['publications'])
            random_sleep(min_sec=1, max_sec=5)

            # In the author's pub list, try to find the one that matches our
            # specific paper by title and year
            for pub in author['publications']:
                if pub['bib']['title'] == title and pub['bib']['pub_year'] == year:
                    pub = scholarly.fill(pub, sections='counts')
                    random_sleep(min_sec=1, max_sec=5)
                    pub_id = pub.get('cites_id', None)
                    break

            if pub_id is not None: # if found pub_id
                # Update pub_id in the pub_data table
                pub_data.at[idx, 'Pub ID'] = pub_id
                if save_csv_path:
                    pub_data.to_csv(save_csv_path, index=False)
            
                # Look for pub_cites_per_year using pub_id
                pub_cites_per_year[pub_id] = pub['cites_per_year']
                if save_json_path:
                    with open(save_json_path, 'w') as f:
                        json.dump(pub_cites_per_year, f)

                # No need to check the next author_id, break to next paper
                break
    
    return pub_data, pub_cites_per_year
