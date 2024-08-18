# %load webtableretrieval.py
import bs4
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
from datetime import datetime

def getNowTime():
    now = datetime.now()
    # dd/mm/YY H:M:S
    dt = now.strftime("%d/%m/%Y %H:%M:%S")
    return dt

def pageText(_page: int)-> dict:
    link = f'https://www.mchk.org.hk/tc_chi/list_register/list.php?page={_page}&ipp=20&type=L'
    content = requests.get(link).text
    soup = bs(content, 'html.parser')
    lstReg = colText(soup, 'reg')
    lstName = colText(soup, 'name')
    lstDate = colText(soup, 'date')
    lstQualification = colText(soup, 'qualification')
    lstQuali = [x for (i, x) in enumerate(lstQualification) if i % 2 == 0]
    lstYear = [x for (i, x) in enumerate(lstQualification) if i % 2 != 0]
    myDict = {'regno': lstReg, 'name': lstName, 'address': lstDate, 'qualification': lstQuali, 'year': lstYear}
    return myDict

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

def mergeDict(_dict1: dict, _dict2: dict) -> dict:
    for key, value in _dict2.items():
        if key in _dict1:
            _dict1[key] = _dict1[key] + value
        else:
            _dict1[key] = value
    return _dict1
    
lstOfDict = []
#dict_all = {}
def fetchAllPages(_page: int) -> dict:    
    for i in range(1, _page+1): 
        dict_1 = pageText(i)
        lstOfDict.append(dict_1)
        dt1 = getNowTime()
        print(f'Page {i} is retrieved at {dt1}.')
    dict_all = {}
    for dict1 in lstOfDict:
        mergeDict(dict_all, dict1)
    return dict_all

myDict = fetchAllPages(3)
print('*'*50)
print('All pages are fetched.')
df = pd.DataFrame(myDict)
#df
df.to_excel("doctorlist.xlsx")
print("complete.")