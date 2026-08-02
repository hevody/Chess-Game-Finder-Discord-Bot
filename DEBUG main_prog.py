from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

### config ###
DEBUG = True
VERBOSE = True
### --- ###

### DEBUG: variable declaration ###
page_start = 1          # suppose page = x: page_start = x, page_end = x + 1
page_end = 21
###

### variable declaration ###
all_fetched_usernames = []
database_filename = ".\\databases\\" + "Top 1000 Filipino Rapid Players" + ".db"
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

  if DEBUG == True:
    for element in elements:
      print(element.text)

  driver.close()
  return usernames

if __name__ == '__main__':
  ### this section contains grabbing usernames and saving those usernames inside a .db file (in ./databases/) ###
  for page in range(page_start, page_end):
    if VERBOSE == True:
      print(f'[*] Currently on page {page}')
    fetched_usernames = grabccusernames(country, page)
    all_fetched_usernames += fetched_usernames
  if VERBOSE == True:
    print(f'Saving into {database_filename}...')
  with open(database_filename, 'w') as f:         # saves inside a .db file
    for individual_username in all_fetched_usernames:
        f.write(f"{individual_username}\n")
  if VERBOSE == True:
    print(f'Files saved into {database_filename}...')

  

### debug ###
if DEBUG == True or VERBOSE == True:
  end_time = time.perf_counter()
  elapsed_time = end_time - start_time
  print(f"Elapsed time: {elapsed_time:.1f} seconds")
### --- ###
