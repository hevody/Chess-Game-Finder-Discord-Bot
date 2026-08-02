from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

### config ###
DEBUG = True
VERBOSE = True
### --- ###

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
  wait = WebDriverWait(driver, 10)
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
    print(current_item)
     
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
         

if __name__ == '__main__':
  # result = ELO_PAGE_binary_search(1400, True, False)
  # result = ELO_PAGE_binary_search(1500, False, True)
  #result = ELO_PAGE_binary_search(1399, True, False)  # between 1399 - 1400 for minimum
  result = ELO_PAGE_binary_search(1501, False, True) # between 1500 - 1501 
  print(result)