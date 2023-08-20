import pandas as pd
from bs4 import BeautifulSoup
import concurrent.futures
import time
import requests


def make_request(i, month, year):
    url = 'http://mahaepos.gov.in/SRC_Trans_Details.jsp'
    data = {'src_no': i, 'month': month, 'year': year}
    response = requests.post(url, data=data)
    soup = BeautifulSoup(response.text, 'html.parser')
    target_heading = f"Transaction Details for RC : {i}"
    tables = soup.find_all('table')
    if len(tables)>2:
        lastTable = tables[-1]
        heading = lastTable.find('td')
        if heading.text.strip() == target_heading:
            target_table = lastTable
            trElements = target_table.findChildren('tr')
            tdElements = trElements[-1].findChildren('td')
            if tdElements[2].text != '251832900166':
                return i, f'{tdElements[2].text}'
            else:
                return i, 'Taken'
        else:
            return i, 'Pending'
    else :
        return i, 'Pending'


cardBase = pd.read_excel(r'dataset/Daily sales/data/remaningcards.xlsx')

def thfunction():
    a = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=512) as executor:
        futures = [executor.submit(make_request,i,8,2023) for i in cardBase['SRC No']]

        for future in concurrent.futures.as_completed(futures):
            print(future.result())
        print(time.time()-a)

if __name__  == '__main__':
    thfunction()