from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

### config ###
DEBUG = True
### --- ###

### DEBUG: variable declaration ###
page_start = 1          # suppose page = x: page_start = x, page_end = x + 1
page_end = 20
###

### variable declaration ###
all_fetched_usernames = []
### --- ###

### debug ###
if DEBUG == True:
  start_time = time.perf_counter()
### --- ###

def grabccusernames(page_local):
  ### variable declaration ###
  usernames = []
  ### --- ###

  if DEBUG == True:
    driver = webdriver.Chrome()     

  else: 
    options = Options()
    options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=options)

  driver.get(f"https://www.chess.com/leaderboard/live/rapid?country=PH&page={page_local}")

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
  for page in range(page_start, page_end):
    fetched_usernames = grabccusernames(page)
    all_fetched_usernames += fetched_usernames
  print(all_fetched_usernames)

### debug ###
if DEBUG == True:
  end_time = time.perf_counter()
  elapsed_time = end_time - start_time
  print(f"Elapsed time: {elapsed_time:.1f} seconds")
### --- ###
