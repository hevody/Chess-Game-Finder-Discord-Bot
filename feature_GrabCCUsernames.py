from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import random

"""
revision 1
"""

### config ###
DEBUG = True
VERBOSE = True
database_filename = "pageOneToThree"
country = "PH"
LOAD_DATABASE = True
username_database = "Top 1000 Filipino Rapid Players.db"
### --- ###

### temporary variables ###
high_elo_true_page = 1
low_elo_true_page = 2
### --- ###

### constant variable declaration ###
all_fetched_usernames = []
database_dir_filename = ".\\databases\\" + f"{database_filename}" + ".db"
### --- ###

### debug ###
if DEBUG == True or VERBOSE == True:
    start_time = time.perf_counter()
### --- ###

def load_username_database() -> list:       # will return a random list
    # what database would you like to use?
    # there will be 2 sources, either on pastebin, raw github, or locally
    print('What database would you like to use?')          # iterate


    # input()
    print()

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
    if load_username_database == True:
        load_username_database()
    #grab_usernames_randomly()
    #grab_usernames_sequentially()

### debug ###
if DEBUG == True or VERBOSE == True:
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.1f} seconds")