import asyncio
from bs4 import BeautifulSoup
import time
import pandas as pd 
import aiohttp

cardBase = pd.read_excel(r'dataset/Daily sales/data/remaningcards.xlsx')



async def fetch_data(session, src_no, month, year):
    url = 'http://mahaepos.gov.in/SRC_Trans_Details.jsp'
    data = {'src_no': src_no, 'month': month, 'year': year}
    async with session.post(url, data=data) as response:
        return await response.text()

def scrape_data(html, src_no):
    soup = BeautifulSoup(html, 'lxml')  # Use lxml for more efficient parsing
    target_heading = f"Transaction Details for RC : {src_no}"
    tables = soup.find_all('table')
    if len(tables) > 2:
        lastTable = tables[-1]
        heading = lastTable.find('td')
        if heading.text.strip() == target_heading:
            target_table = lastTable
            trElements = target_table.findChildren('tr')
            tdElements = trElements[-1].findChildren('td')
            if tdElements[2].text != '251832900166':
                return src_no, f'{tdElements[2].text}'
            else:
                return src_no, 'Taken'
        else:
            return src_no, 'Pending'
    else:
        return src_no, 'Pending'

async def fetch_status():
    month, year = 8,2023
    src_numbers = cardBase['SRC No']
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data(session, src_no, month, year) for src_no in src_numbers]
        html_responses = await asyncio.gather(*tasks)

        results = [scrape_data(html, src_no) for html, src_no in zip(html_responses, src_numbers)]

    for src_no, status in results:
        print(f"SRC No: {src_no}, Status: {status}")

a = time.time()
if __name__ == '__main__':
    asyncio.run(fetch_status())
    print(time.time()-a)

def afunction():
    asyncio.run(fetch_status())