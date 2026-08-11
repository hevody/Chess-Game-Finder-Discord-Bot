import random
import os
import json
import requests
import re
import chess
import chess.pgn
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import threading
import logging
### --- ### 

"""
revision 1
"""
# make a caching database so that usernames that are not found will not be searched again once there is a rate-limit [requests.exceptions.ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))] 

logging.basicConfig(
    filename='app.log', 
    encoding='utf-8', 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

### config ###
DEBUG = False
VERBOSE = False
THREADING_DEBUG = True
database_filename = ""    # add the filename
country = "PH"
TimeControl = 600
session = requests.Session()
retries = Retry(total=3,
                backoff_factor=1,
                status_forcelist=[500, 502, 503, 504],
                )
session.mount("https://", HTTPAdapter(max_retries=retries))
session.mount("http://", HTTPAdapter(max_retries=retries))
gameMode = 'rapid'
### --- ###



### temporary variables ###
given_fen_user = '8/8/5k2/6p1/4K1Bp/7P/8/8 b - - 1 52'
low_elo = 1500
high_elo = 1530
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

def grabCCusernames_REQUESTS(page_local: int) -> list:  # will return a list of usernames from that page
  time.sleep(0.3)
  while True:
    try:
      response = session.get(f'https://www.chess.com/callback/leaderboard/live/{gameMode}?country={country}&gameType=live&page={page_local}&totalPage=10000', headers=HEADERS, timeout=30)
    except KeyboardInterrupt:
      exit()
    except:
      continue
  
    if response.status_code == 200:
      leaderboard_json = response.json()
      break
    else:
      continue
  
  username_list = []
  for player_index in range(len(leaderboard_json['leaders'])):
    username_list += [(leaderboard_json['leaders'][player_index]['user']['username'])]
    
  if VERBOSE == True:
    print(f'Found usernames on page {page_local}: {username_list}')

  return username_list

def open_leaderboard_page_retrieve_elo_REQUESTS(page: int) -> list: # returns elo list, much faster with API calls
  time.sleep(0.3)
  while True:
    try:
        response = session.get(f'https://www.chess.com/callback/leaderboard/live/{gameMode}?country={country}&gameType=live&page={page}&totalPage=10000', headers=HEADERS, timeout=30)
    except KeyboardInterrupt:
        exit()
    except:
        continue

    if response.status_code == 200:
      leaderboard_json = response.json()
      break
    else:
      continue

  elo_list = []
  for player_index in range(len(leaderboard_json['leaders'])):
    elo_list += [int(leaderboard_json['leaders'][player_index]['score'])]

  unique_elo_list = list(dict.fromkeys(elo_list))

  if VERBOSE == True:
    print(f'Found elo on the page {page}: {unique_elo_list}')

  return unique_elo_list

def find_true_elo_page(general_page: int, is_low_elo: bool, is_high_elo: bool) -> int:
  if is_low_elo == True:
    elo_to_find = low_elo - 1
  if is_high_elo == True:
    elo_to_find = high_elo + 1

  pagination = general_page
  while True:
    list_of_elo_in_page = open_leaderboard_page_retrieve_elo_REQUESTS(pagination)
    if elo_to_find in list_of_elo_in_page:
      return pagination
    elif is_low_elo == True:
      pagination += 1
    elif is_high_elo == True:
      pagination -= 1

def ELO_PAGE_binary_search(TARGET_elo_given: int, low_elo_range: bool, high_elo_range: bool) -> int:           # returns the specific page (index)
  ### variable declaration ###
  left = 1              # the pages (index)
  right = 10_000        # the pages (index)
  ### --- ###

  while True:
    midpoint = left + (right - left) // 2
    current_item = open_leaderboard_page_retrieve_elo_REQUESTS(midpoint)

    if str(TARGET_elo_given) in current_item:                      
      return midpoint                       
    if len(current_item) == 1 or high_elo_range == True:           
      current_item = int(current_item[0])
    elif low_elo_range == True:
      current_item = int(current_item[-1])

    if current_item == TARGET_elo_given:
      return midpoint
    if TARGET_elo_given > current_item:
      right = midpoint - 1
    else:
      left = midpoint + 1

def validate_game_pgn_to_fen(index_g_u: int, given_fen: str, username: str) -> bool: # will return if the game was found or not
  try:
    with lock:
      candidate_pgn_var = monthly_list[index_g_u]['pgn']
  except KeyboardInterrupt:
    exit()
  except:
    return False

  if username == 'hevocity':
     print(candidate_pgn_var)

  
  with open(f'temp_candidate_{username}.pgn', 'w', encoding='utf-8') as f:
    f.write(candidate_pgn_var)

  candidate_pgn_var = open(f'temp_candidate_{username}.pgn', encoding='utf-8', errors='replace')

  possible_game = chess.pgn.read_game(candidate_pgn_var)

  this_game_time_control = possible_game.headers['TimeControl']

  if not this_game_time_control == str(TimeControl):
    candidate_pgn_var.close()
    os.remove(f'temp_candidate_{username}.pgn')
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
      os.remove(f'temp_candidate_{username}.pgn')
      return True
  candidate_pgn_var.close()
  os.remove(f'temp_candidate_{username}.pgn')
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

  if stop_event.is_set():
     return None
  ### strip given_fen ###
  given_fen_match = fen_plain_patern.search(given_fen_unstripped)      
  given_fen = given_fen_match.group()

  # challenge: username and given fen to game link
  game_archive = get_game_archive(f'https://api.chess.com/pub/player/{cc_username}/games/archives') # dict, mut

  if cc_username == 'hevocity':
     print(game_archive)

  if game_archive == []:
    return (False, '[This user does not exist]')
  game_archive.reverse()  

  game_archive_depth_of_month = []    # list, mut
  for game_archive_month_index in range(depth_of_month):
    game_archive_depth_of_month += [game_archive[game_archive_month_index]]

  for month_link in game_archive_depth_of_month:
    monthly_list = cache_monthly_json(m_link=month_link)    # dict, mut, LOCKED

    with lock:
       monthly_list = monthly_list

    if cc_username == 'hevocity':
       print(monthly_list)

    if monthly_list == []:
       continue
    for game_index in range(len(monthly_list)):
      if DEBUG == True:
        print(game_index)
      game_found = validate_game_pgn_to_fen(game_index, given_fen=given_fen, username=cc_username)
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

    ### performs a binary search ========================================
    
    ### low elo ###
    if VERBOSE == True:
      print(f'[*] Searching for the General Chess.com Page of {low_elo}')
    low_elo_general_page = ELO_PAGE_binary_search(low_elo, True, False)
    
    if DEBUG == True or VERBOSE == True:
      print(f'[*] Found the General Chess.com Page for {low_elo}: {low_elo_general_page}')
    
    ### find true page low elo ###      # there will be 2 cases, ex. 1400 and 1399 co-exist in the page; 1400 and 1399 are on the separate page
    if VERBOSE == True:
      print(f'[*] Searching for the Real Chess.com Page of {low_elo}')         
    low_elo_true_page = find_true_elo_page(low_elo_general_page, True, False)
  
    ### high elo ###
    if VERBOSE == True:
        print(f'[*] Searching for the General Chess.com Page of {high_elo}')
    high_elo_general_page = ELO_PAGE_binary_search(high_elo, False, True)
    if DEBUG == True or VERBOSE == True:
      print(f'[*] Found the General Chess.com Page for {high_elo}: {high_elo_general_page}')
  
    ### find true page high elo ###
    if VERBOSE == True:
        print(f'[*] Searching for the Real Chess.com Page of {high_elo}')    
    high_elo_true_page = find_true_elo_page(high_elo_general_page, False, True)
  
    if VERBOSE == True:
      print(f'[FOUND] Real Chess.com page {low_elo}: {low_elo_true_page}')
      print(f'[FOUND] Real Chess.com page of {high_elo}: {high_elo_true_page}')    

    pages_that_contain_range_usernames = [x for x in range(high_elo_true_page, low_elo_true_page+1)]
  
    if mode == 'GrabRandomly':
      random.shuffle(pages_that_contain_range_usernames)

    for page in pages_that_contain_range_usernames:
      if VERBOSE == True:
        chance_calculate = (pages_that_contain_range_usernames.index(page) / len(pages_that_contain_range_usernames)) * 100
        print(f'Chance of finding the game: {chance_calculate:.1f}%') 
      usernames_in_page = grabCCusernames_REQUESTS(page_local=page)
      for username in usernames_in_page:
         if username == 'hevocity':
            print('start the debug!')
            input()
         if username in cache_usernames:
            continue
         with open('.\\cache\\cache_usernames.db', 'a') as f:
            f.write(username + '\n')
         if DEBUG == True:
            print(f'Currently searching in user: {username}')
         found, message = matchfen_to_link(cc_username=username, given_fen_unstripped=given_fen_user, depth_of_month=1)
         if found == False:
            print(message)
         if found == True:
            return message 
         

stop_event = threading.Event()
lock = threading.Lock()

def beta_test():
  #main(mode='GrabRandomly')
  usernames_list = load_username_database()
  print(usernames_list.index('hevocity'))
  input()
  with ThreadPoolExecutor(max_workers=5) as executor:
   future_to_url =  {executor.submit(matchfen_to_link, username, given_fen_user, 1): username for username in usernames_list}
   for future in concurrent.futures.as_completed(future_to_url):
      try:
         result = future.result()
      except Exception as e:
         print(f"Thread crashed with error: {e}")
      url = future_to_url[future]
      if THREADING_DEBUG == True:
        logging.info(future.result())
        logging.info(url)
        logging.info(usernames_list.index(url))

        print(future.result())  # return of function   
        print(url)              # username
        print(usernames_list.index(url))    # index
      if future.result()[0] == True:
        if THREADING_DEBUG == True:
          logging.info(url)
          logging.info(future.result()[1])
          print(url)
          print(future.result()[1])
        stop_event.set()
        executor.shutdown(wait=True, cancel_futures=True)
        return(future.result()[1])
  return 'Game Not Found'  

# I need to have designated temp files for the thread pool  

if __name__ == '__main__':
  print(beta_test())
  print('This code ran!!!!!')


### debug ###
if DEBUG == True or VERBOSE == True:
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.1f} seconds")