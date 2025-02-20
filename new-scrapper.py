import csv
import requests
from bs4 import BeautifulSoup
import pandas as pd


base_url = 'https://www.bon-bast.com/'

# defining the User-Agent header to use in the GET request below
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/107.0.0.0 Safari/537.36'
}
page = requests.get(base_url, headers=headers)

# # parsing the target web page with Beautiful Soup
soup = BeautifulSoup(page.text, 'html.parser')

currencies_table1 = soup.find_all('table', class_='table table-condensed')[0]
currencies_table2 = soup.find_all('table', class_='table table-condensed')[1]


def scrape_page(soup, currencies_table, fileName):

        # Defining of the dataframe
    df = pd.DataFrame(columns=['Code', 'Currency', 'Sell', 'Buy'])

        # Collecting data
    for row in currencies_table.find_all('tr'):    
            # Find all data for each column
            columns = row.find_all('td')
            if(columns != []):
                code = columns[0].text.strip()
                currency = columns[1].text.strip()
                sell = columns[2].text.strip()
                buy = columns[3].text.strip()
            
            df = df._append({'Code': code,'Currency': currency, 'Sell': sell, 'Buy': buy },ignore_index=True)
    # Removing first row and convert it to a csv file
    df = df.iloc[1:]
    df.to_json(f'{fileName}.json', orient='gi')
    df.to_csv(f'{fileName}.csv', encoding='utf-8', index=False)

scrape_page(soup, currencies_table1, 'table1')
scrape_page(soup, currencies_table2, 'table2')
