from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

### config ###
DEBUG = False
VERBOSE = True
### --- ###

### DEBUG: variable declaration ###
page_start = 5947          # suppose page = x: page_start = x, page_end = x + 1
page_end = 7634
page_end += 1 
###

### variable declaration ###
all_fetched_usernames = []
database_filename = ".\\databases\\" + "900-1000 Rapid CC Filipino usernames" + ".db"
country = "PH"
### --- ###

### debug ###
if DEBUG == True or VERBOSE == True:
  start_time = time.perf_counter()
### --- ###

def grabccusernames(country_local, page_local):
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
      print(f'[username found]: {element.text}')

  driver.close()
  return usernames

if __name__ == '__main__':
  ### this section contains grabbing usernames and saving those usernames inside a .db file (in ./databases/) ###
  for page in range(page_start, page_end):
    if VERBOSE == True:
      print(f'[*] Currently on page {page}')
    while True:             # bug fix for: urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host='localhost', port=10890): Read timed out. (read timeout=120)
      try:
        fetched_usernames = grabccusernames(country, page)
        break
      except KeyboardInterrupt:
        break
      except:
        continue
    all_fetched_usernames += fetched_usernames
    with open(f'{database_filename}_temp.array', 'w') as f:             # temporary save of the array into the database in case of timeout
      f.write(str(all_fetched_usernames))       

  if VERBOSE == True:
    print(f'Saving into {database_filename}...')
  with open(database_filename, 'w') as f:         # saves inside a .db file
    for individual_username in all_fetched_usernames:
        f.write(f"{individual_username}\n")
  if VERBOSE == True:
    print(f'Usernames saved into {database_filename}...')

  

### debug ###
if DEBUG == True or VERBOSE == True:
  end_time = time.perf_counter()
  elapsed_time = end_time - start_time
  print(f"Elapsed time: {elapsed_time:.1f} seconds")
### --- ###
