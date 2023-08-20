import aiohttp
import asyncio
from bs4 import BeautifulSoup
import concurrent.futures
import time

loops = 5000
a = time.time()
async def performTask(index):
    varA = f'Start task execution of {index}...'

    await asyncio.sleep(5)

    return f'Finising the execution of {index} index',varA

async def runMultiple():
    results = await asyncio.gather(*[performTask(index) for index in range(loops)])

    for result in results:
        # print(result)
        pass


def threadTask(index):
    varT= f'Executing thread {index} '
    time.sleep(5)
    return f'Done executing {index}',varT


asyncio.run(runMultiple())
atime = time.time()-a
print('Onto another')


b = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=3000) as executor:
    futures = [executor.submit(threadTask, index) for index in range(loops)]

    done, _ = concurrent.futures.wait(futures, return_when=concurrent.futures.ALL_COMPLETED)


ttime = time.time()-b
print(ttime)
print(atime)

print(atime < ttime)












# def make_request(i, month, year):
#     url = 'http://mahaepos.gov.in/SRC_Trans_Details.jsp'
#     data = {'src_no': i, 'month': month, 'year': year}
#     response = requests.post(url, data=data)
#     soup = BeautifulSoup(response.text, 'html.parser')
#     target_heading = f"Transaction Details for RC : {i}"
#     tables = soup.find_all('table')
#     if len(tables)>2:
#         lastTable = tables[-1]
#         heading = lastTable.find('td')
#         if heading.text.strip() == target_heading:
#             target_table = lastTable
#             trElements = target_table.findChildren('tr')
#             tdElements = trElements[-1].findChildren('td')
#             if tdElements[2].text != '251832900166':
#                 return i, f'{tdElements[2].text}'
#             else:
#                 return i, 'Taken'
#         else:
#             return i, 'Pending'
#     else :
#         return i, 'Pending'