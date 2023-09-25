from selenium import webdriver
import pandas as pd

web_site = 'https://www.adamchoi.co.uk/fixtures'
path = 'chromedriver_linux64 (1)/chromedriver'

driver = webdriver.Chrome(path)
driver.get(web_site)

all_matches_button = driver.find_element('xpath', '//label[@data-btn-radio="\'date\'"]')
all_matches_button.click()

matches = driver.find_elements('tag name', 'table')
Home = []
All = []
Home_team = []
KO = []
Away_team = []
All2 = []
Away = []
for match in matches:
    match_row = match.find_elements('tag name', 'tbody')
    for row in match_row:
        match_rows = row.find_elements('tag name', 'tr')
        for col in match_rows:
            try:
                Home.append(col.find_element('xpath', './td[1]').text)
                All.append(col.find_element('xpath', './td[2]').text)
                Home_team.append(col.find_element('xpath', './td[3]').text)
                KO.append(col.find_element('xpath', './td[4]').text)
                Away_team.append(col.find_element('xpath', './td[5]').text)
                All2.append(col.find_element('xpath', './td[6]').text)
                Away.append(col.find_element('xpath', './td[7]').text)
            except Exception as e:
                All.append('')
                Home_team.append('')
                KO.append('')
                Away_team.append('')
                All2.append('')
                Away.append('')

driver.quit()

df = pd.DataFrame(
    {'Home': Home, 'All': All, 'Home Team': Home_team, 'KO': KO, 'Away_team': Away_team, 'All2': All2, 'Away': Away})
df.to_csv('Score.csv', index=False)
print(df)
