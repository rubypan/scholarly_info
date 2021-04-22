import pandas as pd
from scholarly import scholarly

from utils import set_scholarly_proxy
from pub_info import search_by_title, get_pub_cites_per_year
from author_info import get_author_data, get_author_cites_per_year


# External parameters
INPUT_CSV_PATH = '~/Downloads/google_scholar_input_file.csv'
SELECT_PROXY = 'tor' # select from [None, 'free_proxies', 'tor']
PUB_DATA_NOID_PATH = './pub_data_noID.csv'
PUB_DATA_PATH = './pub_data.csv'
AUTHOR_DATA_PATH = './author_data.csv'
PUB_CPY_PATH = 'pub_cites_per_year.json'
AUTHOR_CPY_PATH = 'author_cites_per_year.json'


if __name__ == '__main__':
    # Read input file
    data = pd.read_csv(INPUT_CSV_PATH)
    # Drop NaN authors
    data.dropna(subset=['Author'], inplace=True)
    # Drop duplicate titles
    data.drop_duplicates('Title', inplace=True)
    data.reset_index(inplace=True)

    # Set up proxy
    pg = set_scholarly_proxy(SELECT_PROXY)

    ########################################################
    # 1 - Search by title
    title_list = data['Title']
    # pub_data = search_by_title(title_list, save_path=PUB_DATA_NOID_PATH)
    pub_data = pd.read_csv(PUB_DATA_NOID_PATH, dtype=str)

    ########################################################
    # 2 - Get author data
    author_data = get_author_data(pub_data, save_path=AUTHOR_DATA_PATH)
    author_data = pd.read_csv(AUTHOR_DATA_PATH, dtype=str)

    ########################################################
    # 3 - Fill 'pub_id' and find pub_cites_per_year
    pub_data, pub_cites_per_year = get_pub_cites_per_year(
      pub_data,
      save_csv_path=PUB_DATA_PATH,
      save_json_path=PUB_CPY_PATH
     )
    
    ########################################################
    # 4 - Find author_cites_per_year
    author_cites_per_year = get_author_cites_per_year(
        author_data,
        save_json_path=AUTHOR_CPY_PATH
    )
