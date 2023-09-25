from selenium import webdriver
import pandas as pd
from selenium.webdriver.support.ui import Select
import time

web_site = 'https://www.adamchoi.co.uk/results/quick'
path = 'chromedriver_linux64 (1)/chromedriver'


driver = webdriver.Chrome(path)
driver.get(web_site)

draw_button = driver.find_element('xpath', '//label[@data-btn-radio="\'Draw\'"]')
draw_button.click()

select_country = Select(driver.find_element('id', 'countrySelect'))
select_country.select_by_visible_text('Argentina')

fixture_button = driver.find_element('xpath', '//label[@data-btn-radio="\'withFixture\'"]')
fixture_button.click()

time.sleep(10)

fixture_matches = driver.find_elements('tag name', 'table')

team = []
number = []

try:
    for fixture_match in fixture_matches:
        table_matches = fixture_match.find_elements('tag name', 'tbody')
        for table_match in table_matches:
            tables_row = table_match.find_elements('tag name', 'tr')
            for row in range(len(tables_row) - 1):
                team.append(tables_row[row].find_element('xpath', './td[2]').text)
                number.append(tables_row[row].find_element('xpath', './td[3]').text)
except Exception as e:
    print(str(e))
    driver.quit()
driver.quit()


df = pd.DataFrame({'Team': team, 'Number': number})
df.to_csv('results.csv', index=False)



