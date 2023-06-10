import pandas as pd
import concurrent.futures
import numpy as np
import requests
from bs4 import BeautifulSoup

pd.set_option('display.max_rows' , None)
class CardStatus:
    def __init__(self, yetTOcome):
        self.yetTOcome = yetTOcome
        self.statusDataFrame = []
        # print(self.yetTOcome)

    @staticmethod
    def make_request(i, month, year):
        url = 'http://mahaepos.gov.in/SRC_Trans_Details.jsp'
        data = {'src_no': i, 'month': month, 'year': year}
        response = requests.post(url, data=data)
        soup = BeautifulSoup(response.text, 'html.parser')
        tableElements = soup.find_all('table')
        if len(tableElements) > 2:
            trElements = tableElements[-1].findChildren('tr')
            tdElements = trElements[-1].findChildren('td')
            if tdElements[2].text != '251832900166':
                return i, 'Ported'
            else:
                return i, 'Taken'
        else:
            return i, 'Pending'

    def fetch_status(self, month, year):
        status = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=216) as executor:
            futures = [executor.submit(self.make_request, i, month, year) for i in self.yetTOcome['SRC No']]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                status.append(result)

        self.statusDataFrame = pd.DataFrame(status, columns=['SRC No', 'Status'])
        print(self.statusDataFrame)
        cardStatus = self.statusDataFrame.merge(self.yetTOcome , on = 'SRC No' , how='left')
        # print(cardStatus)
        cardStatus['REF'] = cardStatus['REF'].replace(to_replace=0 , value=np.nan)
        cardStatus =  cardStatus.sort_values(by=['REF','SRC No'])
        cardStatus['REF'] =  cardStatus['REF'].fillna(0).astype('int')
        cardStatus.reset_index(drop=True , inplace=True)
        return cardStatus
    

yetTOcome = pd.read_excel(r'test.xlsx')
CS = CardStatus(yetTOcome).fetch_status(1,2023)

print(CS)