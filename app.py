from flask import Flask, jsonify, render_template , send_from_directory , Markup
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from dateutil import relativedelta
import os
import json
import time
# import concurrent.futures
import numpy as np
from dateutil import relativedelta 
import asyncio
import aiohttp


app = Flask(__name__)


class SalesData:
    def __init__(self, month, year):
        self.month = month
        self.year = year
        self.headers = []
        self.df = None
        self.dailysales = None

    def fetch_data(self):
        response = requests.post('https://mahaepos.gov.in/FPS_Trans_Details.jsp',
                                 data={'dist_code': 2518, 'fps_id': 251832900166, 'month': self.month, 'year': self.year}, verify=False)
        
        response_html = response.text 
        soup = BeautifulSoup(response_html, 'html.parser')
        table = soup.find('table')
        if table: 
            self.extract_headers(response)
            self.extract_dataframe()
        else : 
            date = datetime.now() - relativedelta.relativedelta(months =1 )
            self.month = date.month
            self.year = date.year 
            self.fetch_data()
            
    def extract_headers(self, response):
        self.data = pd.read_html(response.text)
        for col_name in self.data[0].columns:
            self.headers.append(col_name[2])
        self.data[0].columns = self.headers

    def extract_dataframe(self):
        self.df = self.data[0]
        collist = [col for col in self.df.columns if self.df[col].dtype == 'float64' and self.df[col].iloc[-1] > 0]
        self.df.set_index('Date', inplace=True)
        self.df.drop(index='Total', inplace=True)
        self.df.index = self.df.index.map(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%S'))
        self.dailysales = self.df.resample('D')[collist].sum()
        self.dailysales = self.dailysales.merge(self.df.resample('D')[collist[0]].count().rename('Sale Count'),
                                                on='Date')
        self.dailysales.index = self.dailysales.index.map(str).map(lambda x: x[0:10])
        self.dailysales.loc[-1] = self.dailysales.sum()
        self.dailysales.rename(index={-1: 'Total'}, inplace=True)

    def generate_report(self):
        # Generate report or perform further operations on self.dailysales
        pass

    def getDate(self):
        return self.month, self.year
        
        
class RemainingCards:
    def __init__(self):
        self.pathlist = []
        self.sheetname = 'remaining_cards'
        self.remaining_cards = pd.DataFrame()
        self.cardBase = pd.read_excel(r'dataset/Daily sales/data/remaningcards.xlsx')
        self.probability = None

    def fetch_remaining_cards_data(self):
        for dir, subdir, files in os.walk(r'dataset/Daily sales/ds_excel'):
            for file in files:
                self.pathlist.append(os.path.join(dir, file))

        for location in self.pathlist:
            remdf = pd.read_excel(location, sheet_name=self.sheetname)
            self.remaining_cards = pd.concat([remdf, self.remaining_cards],
                                             ignore_index=True)

    def calculate_probability(self):
        datestring = datetime.strptime('2022-08-01', '%Y-%m-%d')
        total_months = 12 * relativedelta.relativedelta(datetime.now(), datestring).years + relativedelta.relativedelta(datetime.now(), datestring).months

        self.probability = self.remaining_cards.groupby('SRC No').count()['Units']
        self.probability = round(self.probability / total_months, 4)
        self.probability = 100 - (self.probability * 100)
        self.probability[self.probability < 0] = 0
        self.probability.name = 'Probability'
        # print(self.probability)

    def merge_sales_data(self, sales_data):
        self.fetch_remaining_cards_data()
        self.calculate_probability()
        yetTOcome = self.cardBase[self.cardBase['SRC No'].isin(sales_data.df['SRC No'].astype('float'))==False].sort_values(by = 'REF').fillna(0)
        yetTOcome.iloc[:,:4] = yetTOcome.iloc[:, :4].astype('int64')
        yetTOcome.reset_index(drop=True)
        yetTOcome = yetTOcome.merge(self.probability, on = 'SRC No',how = 'left')
        yetTOcome['Probability'] = yetTOcome['Probability'].replace(to_replace=np.nan ,value =100)
        return yetTOcome[['SRC No', 'REF', 'Units', 'Probability', 'Mobile Number','Name']]


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
        # Using asyncio to do the task concurrently without increasing the vCPU and optimizing the code 
        async with aiohttp.ClientSession() as session:
            for src_no in src_numbers:
                task = self.fetch_data(session, src_no, month, year)
                tasks.append(task)
            html_responses = await asyncio.gather(*tasks)

            results = [self.scrape_data(html, src_no) for html, src_no in
                       zip(html_responses, src_numbers)]

        self.statusDataFrame = pd.DataFrame(results,
                                            columns=['SRC No', 'Status'])
        
        cardStatus = self.statusDataFrame.merge(self.yetTOcome,
                                                on='SRC No', how='left')
        # print(cardStatus)
        cardStatus['REF'] = cardStatus['REF'].replace(to_replace=0,
                                                       value=np.nan)
        
        cardStatus =  cardStatus.sort_values(by=['REF','SRC No'])
        cardStatus['REF'] =  cardStatus['REF'].fillna(0).astype('int')
        cardStatus.reset_index(drop=True , inplace=True)
        return cardStatus

class SaveData:
    def __init__(self, sales_data, availability):
        self.dailysales = sales_data.dailysales.astype('int')
        self.availability = availability
    
    
    def saveFiles(self):
    
        year = self.dailysales.index[0][:4]
        monthstring = datetime.strptime(self.dailysales.index[0] , '%Y-%m-%d').strftime('_%m_%Y.xlsx')
        savepath = r'dataset/Daily sales/ds_excel/'
        directory = os.path.exists(savepath+year)
        if not directory:
            os.mkdir(savepath+year)

        filepath = savepath+year+'/Dailysales'+ monthstring

        with pd.ExcelWriter(filepath,engine='openpyxl') as writer:
            self.dailysales.to_excel(writer, sheet_name='dailysales')
            self.availability.to_excel(writer, sheet_name='remaining_cards' , index = False)

def getStockreport():
    # month = int(input('Enter the month: '))
    # year = int(input("Enter the year: "))
    month = datetime.now().month
    year = datetime.now().year

    sales_data = SalesData(month, year)
    sales_data.fetch_data()

    return sales_data

def main():
    # month = int(input('Enter the month: '))
    # year = int(input("Enter the year: "))
    month = datetime.now().month
    year = datetime.now().year

    sales_data = SalesData(month, year)
    sales_data.fetch_data()
#     sales_data.generate_report()


    dataToFetch = RemainingCards()
    dataToFetch = dataToFetch.merge_sales_data(sales_data)
    month , year = sales_data.getDate()
    status_class = CardStatus(dataToFetch)
    Availability = asyncio.run(status_class.fetch_status(month, year))
    
    # ExcelData= SaveData(sales_data , Availability)
    # ExcelData.saveFiles()

    return Availability
    
# ____________________________READ___________________________________    
#Note : We need to change the path while we change the system 
# In total there are three different paths that we should take care of 
# 1. >> GOTO Class Remaining_Cards> __init__ >> self.CardBase 
# 2. >> GOTO Class Remaining_Cards> fetch_remaining_cards_data >> os.walk
# 3. >> GOTO Class SaveData >> saveFiles >> savepath
# ____________________________________________________________________

@app.route('/availability', methods=['GET'])
def get_availability():
    Availability = main()
    # Sort the DataFrame by the "Date" column
    # sorted_availability = Availability.sort_values('REF')

    # Convert the sorted DataFrame to an HTML table
    Availability['Mobile Number'] = Availability['Mobile Number'].apply(lambda x: Markup(f'<a href="tel:{x}">{x}</a>'))
    availability_table = Availability.to_html(index=True, classes='data-table' , escape= False)

    # Render the template and pass the availability table HTML
    return render_template('availability.html', availability_table=availability_table)


@app.route('/sales', methods=['GET'])
def get_sales_data():
    sales_data = getStockreport()
    sales_data_json = sales_data.dailysales.astype('int').reset_index().to_json(orient='records')
    columns = sales_data.dailysales.reset_index().columns
    # print(columns)
    sales_data_list = json.loads(sales_data_json)
    # print(sales_data.dailysales.astype('int').reset_index())


    return render_template('sales_table.html', data=sales_data_list , columns= columns)


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/styles.css')
def serve_css():
    return send_from_directory(app.static_folder, 'styles.css', mimetype='text/css')


# Trigger the main function when running the script

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))