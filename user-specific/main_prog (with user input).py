from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

### debug ###
start_time = time.perf_counter()
### --- ###

def grabccusernames():
  options = Options()
  options.add_argument("--headless=new")

  driver = webdriver.Chrome(options=options)
  driver.get("https://www.chess.com/leaderboard/live/rapid?country=PH&page=1000")

  wait = WebDriverWait(driver, 10)

  elements = wait.until(
      EC.presence_of_all_elements_located((By.CLASS_NAME, "cc-user-block-username"))
  )

  elements = driver.find_elements(By.CLASS_NAME, "cc-user-block-username")

  for element in elements:
      print(element.text)

  driver.close()

if __name__ == '__main__':
   grabccusernames()

### debug ###
end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time:.1f} seconds")
### --- ###
