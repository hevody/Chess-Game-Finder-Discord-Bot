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
import re
import chess
import chess.pgn
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
### --- ### 

"""
revision 1
"""
# make a caching database so that usernames that are not found will not be searched again once there is a rate-limit [requests.exceptions.ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))] 


### config ###
DEBUG = True
VERBOSE = True
database_filename = "pageOneToThree"
country = "PH"
LOAD_DATABASE = True
TimeControl = 600
session = requests.Session()
retries = Retry(total=3,
                backoff_factor=1,
                status_forcelist=[500, 502, 503, 504],
                )
session.mount("https://", HTTPAdapter(max_retries=retries))
session.mount("http://", HTTPAdapter(max_retries=retries))
### --- ###



### temporary variables ###
high_elo_true_page = 1
low_elo_true_page = 2
given_fen_user = '8/7R/4k3/3p1b2/8/4P2P/2r3P1/6K1 w - - 1 31'
### --- ###

### constant variable declaration ###
all_fetched_usernames = []
database_dir_filename = ".\\databases\\" + f"{database_filename}" + ".db"
USER_AGENT = 'Mozlla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json, text/plain, */*",
    "Connection": "keep-alive"
}
fen_plain_patern = re.compile(r'[a-zA-Z0-9]*/[a-zA-Z0-9]*/[a-zA-Z0-9]*/[a-zA-Z0-9]*/[a-zA-Z0-9]*/[a-zA-Z0-9]*/[a-zA-Z0-9]*/[a-zA-Z0-9]*')
with open('.\\cache\\cache_usernames.db') as f:
   cache_usernames = f.read().split()
### --- ###

### debug ###
if DEBUG == True or VERBOSE == True:
    start_time = time.perf_counter()
### --- ###

### function variable ###
monthly_list = []

def validate_game_pgn_to_fen(index_g_u: int, given_fen: str) -> bool: # will return if the game was found or not
  try:
    candidate_pgn_var = monthly_list[index_g_u]['pgn']
  except KeyboardInterrupt:
    exit()
  except:
    return False

  
  with open('candidate.pgn', 'w', encoding='utf-8') as f:
    f.write(candidate_pgn_var)

  candidate_pgn_var = open('candidate.pgn', encoding='utf-8', errors='replace')

  possible_game = chess.pgn.read_game(candidate_pgn_var)

  this_game_time_control = possible_game.headers['TimeControl']

  if not this_game_time_control == str(TimeControl):
    candidate_pgn_var.close()
    os.remove('candidate.pgn')
    return False

  board = possible_game.board()
  for move in possible_game.mainline_moves():
    board.push(move)
    candidate_fen_unstripped = board.fen()
    candidate_fen_match = fen_plain_patern.search(candidate_fen_unstripped)
    candidate_fen = candidate_fen_match.group()
    if given_fen == candidate_fen:
      if DEBUG == True:
        print('[Match Found!]')
      candidate_pgn_var.close()
      os.remove('candidate.pgn')
      return True
  candidate_pgn_var.close()
  os.remove('candidate.pgn')
  return False
  
def get_game_archive(g_a_url) -> list:
  time.sleep(0.3)
  if DEBUG == True:
      print('[INSIDE] retrieve_game_archive_from_chesscom')
  while True:
    try:
        response = session.get(g_a_url, headers=HEADERS, timeout=30)
    except KeyboardInterrupt:
       exit()
    except:
        continue

    if response.status_code == 200:
      response_json = response.json()
      return response_json['archives']
    elif response.json()['code'] == 0:
      return []
    else:
      continue

def cache_monthly_json(m_link: str) -> list:
  time.sleep(0.3)
  while True:
    try:
        response = session.get(m_link, headers=HEADERS, timeout=30)
    except KeyboardInterrupt:
       exit()
    except:
       continue

    if response.status_code == 200:
      try:
        if response.json()['code'] == 0:
            return []
      except: pass
      response_json = response.json()
      return response_json['games']
    else:
      continue

def matchfen_to_link(cc_username: str, given_fen_unstripped: str, depth_of_month: int) -> tuple[bool, str]:
  global monthly_list
  ### strip given_fen ###
  given_fen_match = fen_plain_patern.search(given_fen_unstripped)
  given_fen = given_fen_match.group()

  # challenge: username and given fen to game link
  game_archive = get_game_archive(f'https://api.chess.com/pub/player/{cc_username}/games/archives')
  if game_archive == []:
    return (False, '[This user does not exist]')
  game_archive.reverse()  

  game_archive_depth_of_month = []
  for game_archive_month_index in range(depth_of_month):
    game_archive_depth_of_month += [game_archive[game_archive_month_index]]

  for month_link in game_archive_depth_of_month:
    monthly_list = cache_monthly_json(m_link=month_link)
    if monthly_list == []:
       continue
    for game_index in range(len(monthly_list)):
      if DEBUG == True:
        print(game_index)
      game_found = validate_game_pgn_to_fen(game_index, given_fen=given_fen)
      if game_found:
        game_link = monthly_list[game_index]['url']
        return (True, game_link)
  return (False, "[GAME NOT FOUND]")

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

    #input_item_number = int(input('choose: ')) - 1
    input_item_number = 1                   # TEMPORARY WILL REMOVE
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

def main(mode: str) -> str:     # will return a link
    if mode == 'LoadDatabase':
        usernames_list = load_username_database()
        for username in usernames_list:
            if username in cache_usernames:
               continue
            with open('.\\cache\\cache_usernames.db', 'a') as f:
               f.write(username + '\n')
            if DEBUG == True:
              print(f'Currently searching in user: {username}')
            if VERBOSE == True:
               chance_calculate = (usernames_list.index(username) / len(usernames_list)) * 100
               print(f'Chance of finding the game: {chance_calculate:.1f}%') 
            found, message = matchfen_to_link(cc_username=username, given_fen_unstripped=given_fen_user, depth_of_month=1)
            if found == False:
               print(message)
            if found == True:
               return message

    #grab_usernames_randomly()
    #grab_usernames_sequentially()

if __name__ == '__main__':
    print(main('LoadDatabase'))

### debug ###
if DEBUG == True or VERBOSE == True:
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.1f} seconds")