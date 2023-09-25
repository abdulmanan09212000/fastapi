from selenium import webdriver
import pandas as pd

web_site = 'https://www.adamchoi.co.uk/teamgoals/detailed'
path = 'chromedriver_linux64 (1)/chromedriver'

driver = webdriver.Chrome(path)
driver.get(web_site)
all_matches_button = driver.find_element('xpath', '//label[@analytics-event="All matches"]')
all_matches_button.click()


matches = driver.find_elements('tag name', 'tr')
date = []
home_team = []
score = []
away_team = []
for match in matches:
    date.append(match.find_element('xpath', './td[1]').text)
    home_team.append(match.find_element('xpath', './td[2]').text)
    score.append(match.find_element('xpath', './td[3]').text)
    away_team.append(match.find_element('xpath', './td[4]').text)
driver.quit()


df = pd.DataFrame({'Date': date, 'HomeTeam': home_team,
                  'Score': score, 'AwayTeam': away_team})
df.to_csv('football_scores.csv', index=False)
