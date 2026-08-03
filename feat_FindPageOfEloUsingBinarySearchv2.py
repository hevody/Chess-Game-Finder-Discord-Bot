from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

### config ###
DEBUG = False
VERBOSE = True

### --- ###

### variable declaration ###
low_elo = 2100
high_elo = 2200
### --- ###

def find_true_elo_page(general_page: int, is_low_elo: bool, is_high_elo: bool) -> int:
  if is_low_elo == True:
    elo_to_find = low_elo - 1
  if is_high_elo == True:
    elo_to_find = high_elo + 1

  pagination = general_page
  while True:
    list_of_elo_in_page = open_leaderboard_page_retrieve_elo(pagination)
    if str(elo_to_find) in list_of_elo_in_page:
      return pagination
    elif is_low_elo == True:
      pagination += 1
    elif is_high_elo == True:
      pagination -= 1



def open_leaderboard_page_retrieve_elo(page: int) -> list:           # returns elo list
  ### variable declaration ###
  eloindexes = [x for x in range(3, 350, 7)]

  ### starts chrome driver ###
  if DEBUG == True:
    driver = webdriver.Chrome()
  else:
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
  ### --- ###

  driver.get(f"https://www.chess.com/leaderboard/live/rapid?country=PH&page={page}")   

  ### wait ###
  wait = WebDriverWait(driver, 30)                                   # bug fix: selenium.common.exceptions.TimeoutException, internet problem probably, before: ['1977', '1976']
  elements = wait.until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "leaderboard-main-link"))
    )
  ### --- ###

  elements = driver.find_elements(By.CLASS_NAME, "leaderboard-main-link")

  

  contains_elo_array = [x.text for x in elements]

  
  multiple_elo_list = []
  for index in eloindexes:          # buggy
    try: 
      multiple_elo_list += [contains_elo_array[index]]
    except:
      break

  unique_elo_list = list(dict.fromkeys(multiple_elo_list))

  if DEBUG == True or VERBOSE == True:
    print(f'(*) Found elo on the page {page}: {unique_elo_list}')            

  driver.close()
  return unique_elo_list
  

def ELO_PAGE_binary_search(TARGET_elo_given: int, low_elo_range: bool, high_elo_range: bool) -> int:           # returns the specific page (index)
  ### variable declaration ###
  left = 1              # the pages (index)
  right = 10_000        # the pages (index)
  ### --- ###

  while True:
    midpoint = left + (right - left) // 2
    current_item = open_leaderboard_page_retrieve_elo(midpoint)

    if str(TARGET_elo_given) in current_item:                      # bug fix
      return midpoint                       
    if len(current_item) == 1 or high_elo_range == True:           # found a bug: (*) Found elo on the page: ['2101', '2100', '2099']
      current_item = int(current_item[0])
    elif low_elo_range == True:
      current_item = int(current_item[-1])

    if current_item == TARGET_elo_given:
      return midpoint
    if TARGET_elo_given > current_item:
      right = midpoint - 1
    else:
      left = midpoint + 1

    

if __name__ == '__main__':
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
    print(f'[*] true page of low elo: {low_elo_true_page}')
    print(f'[*] true page of high elo: {high_elo_true_page}')
  