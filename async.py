import asyncio
import aiohttp
from bs4 import BeautifulSoup
import time
import pandas as pd
import concurrent.futures


async def fetch_data(session, src_no, month, year):
    url = 'http://mahaepos.gov.in/SRC_Trans_Details.jsp'
    data = {'src_no': src_no, 'month': month, 'year': year}
    async with session.post(url, data=data) as response:
        return await response.text()


def scrape_data(html, src_no):
    soup = BeautifulSoup(html, 'html.parser')
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


async def main():
    global cardBase
    src_numbers = cardBase['SRC No']
    # Replace with your list of src_no values
    month = '08'
    year = '2023'

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data(session, src_no, month, year)
                 for src_no in src_numbers]
        html_responses = await asyncio.gather(*tasks)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(scrape_data, html_responses, src_numbers))

    for src_no, status in results:
        print(f"SRC No: {src_no}, Status: {status}")

cardBase = pd.read_excel(r'dataset\Daily sales\data\remaningcards.xlsx')
a = time.time()
if __name__ == '__main__':
    asyncio.run(main())
    print(time.time()-a)







import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
import concurrent.futures

class CardStatus:
    def __init__(self, yetTOcome):
        self.yetTOcome = yetTOcome
        self.statusDataFrame = None

    async def fetch_data(self, session, src_no, month, year):
        url = 'http://mahaepos.gov.in/SRC_Trans_Details.jsp'
        data = {'src_no': src_no, 'month': month, 'year': year}
        async with session.post(url, data=data) as response:
            return await response.text()

    def scrape_data(self, html, src_no):
        soup = BeautifulSoup(html, 'html.parser')
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

    async def fetch_status(self, month, year):
        src_numbers = self.yetTOcome['SRC No']
        tasks = []
        async with aiohttp.ClientSession() as session:
            for src_no in src_numbers:
                task = self.fetch_data(session, src_no, month, year)
                tasks.append(task)
            html_responses = await asyncio.gather(*tasks)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(self.scrape_data, html_responses, src_numbers))

        self.statusDataFrame = pd.DataFrame(results, columns=['SRC No', 'Status'])
        cardStatus = self.statusDataFrame.merge(self.yetTOcome , on = 'SRC No' , how='left')
        # print(cardStatus)
        cardStatus['REF'] = cardStatus['REF'].replace(to_replace=0 , value=np.nan)
        cardStatus =  cardStatus.sort_values(by=['REF','SRC No'])
        cardStatus['REF'] =  cardStatus['REF'].fillna(0).astype('int')
        cardStatus.reset_index(drop=True , inplace=True)
        return cardStatus

def main():
    yetTOcome = None  # Replace with your data
    month = '08'
    year = '2023'

    status_class = CardStatus(yetTOcome)
    asyncio.run(status_class.fetch_status(month, year))