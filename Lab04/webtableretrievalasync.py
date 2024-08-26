import nest_asyncio
import asyncio
import aiohttp
from tqdm.notebook import tqdm
from datetime import datetime
import bs4
from bs4 import BeautifulSoup as bs
import pandas as pd
from datetime import datetime
import math

nest_asyncio.apply()

def getNowTime():
    now = datetime.now()
    # dd/mm/YY H:M:S
    dt = now.strftime("%d/%m/%Y %H:%M:%S")
    return dt

# dictionary with {page: content} structure
dictContent = {}

# column text according to headers
def colText(_soup: bs, _headers: str)->list:
    lst = []
    all_text = _soup.findAll("td", attrs={'headers': _headers})    
    for txt in all_text:
        num = txt.get("rowspan")
        if num == None: # no rowspan
            lst.append(txt.text)
            continue        
        if num == "1":
            lst.append(txt.text)
            continue
        if num != "1":
            for j in range(int(num)):
                lst.append(txt.text)
    return lst

def pageContent(_content: str)-> dict:
    if _content == "":
        print("Empty content!")
        return {}
    soup = bs(_content, 'html.parser')
    lstReg = colText(soup, 'reg')
    lstName = colText(soup, 'name')
    lstDate = colText(soup, 'date')
    lstQualification = colText(soup, 'qualification')
    lstQuali = [x for (i, x) in enumerate(lstQualification) if i % 2 == 0]
    lstYear = [x for (i, x) in enumerate(lstQualification) if i % 2 != 0]
    myDict = {'regno': lstReg, 'name': lstName, 'address': lstDate, 'qualification': lstQuali, 'year': lstYear}
    return myDict

async def fetch_page2(_page: int):
    # By default, the limit is set to 100. 
    # If you're making a large number of requests, 
    # you may need to increase this limit e.g. 900 in this scenario
    # async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=2000)) as session:
    async with aiohttp.ClientSession() as session:
        link = f'https://www.mchk.org.hk/tc_chi/list_register/list.php?page={_page}&ipp=20&type=L'
        # set the timeout to be 60 sec to avoid: The semaphore timeout period has expired
        async with session.get(link, timeout=aiohttp.ClientTimeout(total=60)) as response:
        #async with session.get(link) as response:
            content = await response.text()
            dictContent[_page] = pageContent(content)
            print(_page, " is fetched at: ", getNowTime())

def run_fetching2(_lastpage: int):
    if _lastpage > 100: 
        # segmentation of fetching page as 100 per times
        howmanyfetch = math.ceil(_lastpage / 100)
        for i in range(0, howmanyfetch): # 0 to howmanyfetch-1
            print("segment: ", i+1, " starting...")
            initPage = 1 + i * 100
            if (i == howmanyfetch -1):                
                finalPage = _lastpage + 1
                print("final segment: ", "init page: ", initPage, "; final page: ", finalPage-1, ".")
            else:
                finalPage = initPage + 100
            tasks = [ fetch_page2(page) for page in range(initPage, finalPage)]
            asyncio.get_event_loop().run_until_complete(asyncio.gather(*tasks))            
        print(f"All {len(dictContent)} pages are fetched!")
    else:
        tasks = [ fetch_page2(page) for page in range(1, _lastpage+1)]
        asyncio.get_event_loop().run_until_complete(asyncio.gather(*tasks))
        print(f"All {len(dictContent)} pages are fetched!")

def mergeDict(_dict1: dict, _dict2: dict) -> dict:
    for key, value in _dict2.items():
        if key in _dict1:
            _dict1[key] = _dict1[key] + value
        else:
            _dict1[key] = value
    return _dict1

def main():
    run_fetching2(804)
    # merge the dictContent i.e. page->content to dict_all in acsending order 
    dict_all = {}
    for key in sorted(dictContent.keys()):
        mergeDict(dict_all, dictContent[key])
        # print(f"Key: {key}")
    df = pd.DataFrame(dict_all)
    df.to_excel("..\\output04\\doctorlistAsync2b.xlsx")
    print("output excel file complete.")

main()