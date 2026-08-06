from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

### new dependencies ### 
import random
import os
import json
import requests
### --- ### 

"""
revision 1
"""

### config ###
DEBUG = True
VERBOSE = True
database_filename = "pageOneToThree"
country = "PH"
LOAD_DATABASE = True
### --- ###

### temporary variables ###
high_elo_true_page = 1
low_elo_true_page = 2
### --- ###

### constant variable declaration ###
all_fetched_usernames = []
database_dir_filename = ".\\databases\\" + f"{database_filename}" + ".db"
USER_AGENT = 'Mozlla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'
HEADERS = {
  'User-Agent': USER_AGENT
}
### --- ###

### debug ###
if DEBUG == True or VERBOSE == True:
    start_time = time.perf_counter()
### --- ###

def perform_get_request(url: str) -> str:
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        return response.text

def load_username_database() -> list:       # will return a list with username that is randomized
    # what database would you like to use?
    # there will be 2 sources, either on pastebin, raw github, or locally
    print('What database would you like to use?')          # iterate
    databases = [x for x in os.listdir('.\\databases')]
    databases.remove('username_database_raw_links.json')
    with open('.\\databases\\username_database_raw_links.json') as f:
        json_database = f.read()
    json_database = json.loads(json_database)
    json_database_key = [x for x in json_database]

    databases += json_database_key

    item_number = 0
    for database in databases:
        item_number += 1
        print(f'[{item_number}] {database}')

    input_item_number = int(input('choose: ')) - 1
    if databases[input_item_number] in json_database: 
        usernames_chronological_text = perform_get_request(json_database[databases[input_item_number]])
        usernames_list = usernames_chronological_text.split()
        random.shuffle(usernames_list)
        return usernames_list

    with open(f'.\\databases\\{databases[input_item_number]}') as f:
        local_database_username_list = f.read().split()

    random.shuffle(local_database_username_list)
    return local_database_username_list

def grabccusernames(country_local: str, page_local: int) -> list:
    ### variable declaration ###
    usernames = []
    ### --- ###

    if DEBUG == True:
        driver = webdriver.Chrome()     

    else: 
        options = Options()
        options.add_argument("--headless=new")

        driver = webdriver.Chrome(options=options)

    driver.get(f"https://www.chess.com/leaderboard/live/rapid?country={country_local}&page={page_local}")

    wait = WebDriverWait(driver, 10)
    elements = wait.until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "cc-user-block-username"))
    )

    elements = driver.find_elements(By.CLASS_NAME, "cc-user-block-username")

    for element in elements:
        usernames += [element.text]

    if DEBUG == True or VERBOSE == True:
        for element in elements:
            print(f'[username found] {element.text}')

    driver.close()
    return usernames



if __name__ == '__main__':
    if LOAD_DATABASE == True:
        print(load_username_database())
    #grab_usernames_randomly()
    #grab_usernames_sequentially()

### debug ###
if DEBUG == True or VERBOSE == True:
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.1f} seconds")