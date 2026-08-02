from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

### variable declaration
minimum_elo = 1400
maximum_elo = 1500
half_page = 0
### --- ###

### Config ###
DEBUG = True
### --- ###

def divide_et_impera(target, page_num):
  global half_page
  ### variable declaration ### 
  contains_elo_array = [] 
  eloindexes = [10, 17, 24, 31, 38, 45, 52, 59, 66, 73, 80, 87, 94, 101, 108, 115, 122, 129, 136, 143, 150, 157, 164, 171, 178, 185, 192, 199, 206, 213, 220, 227, 234, 241, 248, 255, 262, 269, 276, 283, 290, 297, 304, 311, 318, 325, 332, 339, 346]
  ### starts chrome driver ###
  if DEBUG == True:
    driver = webdriver.Chrome()
  else:
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
  ### --- ###

  driver.get(f"https://www.chess.com/leaderboard/live/rapid?country=PH&page={page_num}") 

  wait = WebDriverWait(driver, 10)

  elements = wait.until(
      EC.presence_of_all_elements_located((By.CLASS_NAME, "leaderboard-main-link"))
  )

  elements = driver.find_elements(By.CLASS_NAME, "leaderboard-main-link")

  for element in elements:
    contains_elo_array += [element.text]

  for index in eloindexes:
    print(contains_elo_array[index])
    if target == contains_elo_array[index]:
      return True
    else:
      continue
  half_page = contains_elo_array[eloindexes[-1]]
  return False  

def number_halfer(min_p, max_p):
  median = (min_p + max_p) / 2
  median = round(median)
  return median

def range_to_page(min_elo, max_elo):                            # algorithm to convert range into page
  ### variable declaration ###
  min_page = 1
  max_page = 10_000
  Found_Min_Elo = False
  ### --- ###
  
  ### min elo ###
  while True:
    page_number_MIN_ELO = number_halfer(min_page, max_page)
    Found_Min_Elo = divide_et_impera(target=min_elo, page_num=page_number_MIN_ELO)
    if not Found_Min_Elo == True:
      if half_page < min_page:
        min_page = half_page
        max_page = max_page
      elif half_page > min_page:
        min_page = min_page
        max_page = half_page
    
  ### --- ###


if __name__ == '__main__':
  range_to_page(min_elo=minimum_elo, max_elo=maximum_elo)