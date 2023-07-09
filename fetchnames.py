import pandas as pd
import concurrent.futures 
from bs4 import BeautifulSoup
import requests


def fetch_names(number):
    url = 'http://mahaepos.gov.in/SRC_Trans_Details.jsp'
    data = {'src_no': number, 'month': 6, 'year': 2023}
    response = requests.post(url, data=data)
    soup = BeautifulSoup(response.text, 'html.parser')
    target_heading = f"Transaction Details for RC : {number}"
    tables = soup.find_all('table')
    if len(tables)>2:
        lastTable = tables[-1]
        heading = lastTable.find('td')
        if heading.text.strip() == target_heading:
            target_table = lastTable
            trElements = target_table.findChildren('tr')
            tdElements = trElements[-1].findChildren('td')
            name = tdElements[1].text.strip()
            return number,name
    else:
        try : 
            table = tables[0]
            name = table.find_all('td')[1].text
            return number,name
        except:
            return number, 'Not Found'

dataframe = pd.read_excel(r"dataset\Daily sales\data\remaningcards.xlsx")
dflist = []
with concurrent.futures.ThreadPoolExecutor(max_workers=256) as executor:
        futures = [executor.submit(fetch_names,number) for number in dataframe['SRC No']]
        
        for future in concurrent.futures.as_completed(futures):
            dflist.append(future.result())

df = pd.DataFrame(dflist, columns=['SRC No', 'Name'])
named_cards = dataframe.merge(df, how= 'left', on= 'SRC No')
named_cards.to_excel(r"dataset\Daily sales\data\remaningcards.xlsx", index=False)
        