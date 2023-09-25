from selenium import webdriver
import pandas as pd
from selenium.webdriver.support.ui import Select
import time


web_site = 'https://www.adamchoi.co.uk/btts/detailed'
path = 'chromedriver_linux64 (1)/chromedriver'


driver = webdriver.Chrome(path)
driver.get(web_site)

all_matches_button = driver.find_element('xpath', '//label[@analytics-event="All matches"]')
all_matches_button.click()

dropdown = Select(driver.find_element('id', 'country'))
dropdown2 = Select(driver.find_element('id', 'league'))
dropdown3 = Select(driver.find_element('id', 'season'))
dropdown.select_by_visible_text('Italy')
dropdown2.select_by_visible_text('Serie B')
dropdown3.select_by_visible_text('20/21')

time.sleep(20)

matches = driver.find_elements('tag name', 'tr')

date = []
home_team = []
scroe = []
away_team = []

for match in matches:
    date.append(match.find_element('xpath', './td[1]').text)
    home_team.append(match.find_element('xpath', './td[2]').text)
    scroe.append(match.find_element('xpath', './td[3]').text)
    away_team.append(match.find_element('xpath', './td[4]').text)

driver.quit()

df = pd.DataFrame({'date': date, 'home_team': home_team, 'scroe': scroe, 'away_team': away_team})
df.to_csv('btts_detail.csv', index=False)
print(df)
