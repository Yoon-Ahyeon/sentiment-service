from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import re
import time
import json
 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

options = webdriver.ChromeOptions() # 크롬 옵션 객체 생성
options.add_argument("window-size=1920x1080") # 화면크기(전체화면)
options.add_argument("disable-gpu")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument('--no-sandbox') 
# options.add_argument('headless') # headless 모드 설정 -> 해당 옵션 적용 시 PDF 다운 불가


url = input("Enter the product URL (NaverStore): ")

driver = webdriver.Chrome(options=options)
driver.implicitly_wait(3)

driver.get(url)
print("Navigating to the website...")
time.sleep(5) 

# 페이지가 로드될 때까지 대기
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#content')))
print("Page loaded successfully.")

driver.find_element(By.CSS_SELECTOR,'#content > div > div._3CTsMZymJs > div._27jmWaPaKy > ul > li:nth-child(2) > a').click()
print("Clicked on the Reviews tab.")
time.sleep(3)

# 최신순 버튼 클릭
driver.find_element(By.CSS_SELECTOR,'#REVIEW > div > div._2LvIMaBiIO > div._2LAwVxx1Sd > div._1txuie7UTH > ul > li:nth-child(2) > a').click()
print("Sorted reviews by latest.")
time.sleep(3)

write_dt_lst = []
item_nm_lst = []
content_lst = []
ranking_lst = []
date_cut = (datetime.now() - timedelta(days = 365)).strftime('%Y%m%d')

page_num = 1

while True :
    print(f"Collecting data from page {page_num}...")

    html_source = driver.page_source
    soup = BeautifulSoup(html_source, 'html.parser')
    time.sleep(0.5)

    reviews = soup.findAll('li', {'class': 'BnwL_cs1av'})

    for review in range(len(reviews)):
        
        write_dt_raw = reviews[review].findAll('span' ,{'class' : '_2L3vDiadT9'})[0].get_text()
        write_dt = datetime.strptime(write_dt_raw, '%y.%m.%d.').strftime('%Y%m%d')
        
        item_nm_info_raw = reviews[review].findAll('div', {'class' : '_2FXNMst_ak'})[0].get_text()
        item_nm_info_for_del = reviews[review].findAll('div', {'class' : '_2FXNMst_ak'})[0].find('dl', {'class' : 'XbGQRlzveO'}).get_text()
        item_nm_info= re.sub(item_nm_info_for_del, '', item_nm_info_raw)

        str_start_idx = re.sub(item_nm_info_for_del, '', item_nm_info_raw).find('필수 옵션: ')
        item_nm = item_nm_info[str_start_idx + 6:].strip()
        
        review_content_raw = reviews[review].findAll('div', {'class' : '_1kMfD5ErZ6'})[0].find('span', {'class' : '_2L3vDiadT9'}).get_text()
        review_content = re.sub(' +', ' ',re.sub('\n',' ',review_content_raw ))

        rank_num = reviews[review].findAll('em' ,{'class' : '_15NU42F3kT'})[0].get_text()
        
        write_dt_lst.append(write_dt)
        item_nm_lst.append(item_nm)
        content_lst.append(review_content)
        ranking_lst.append(rank_num)
        
    # page 이동
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, 'a.fAUKm1ewwo._2Ar8-aEUTq._nlog_click')

        if "disable" in next_button.get_attribute("class"):
            print("Reached the last page. Exiting loop.")
            break

        next_button.click()
        print(f"Moving to page {page_num + 1}")
        time.sleep(3)
        page_num += 1

    except NoSuchElementException:
        print("No next button found. Assuming last page and exiting loop.")
        break
    except Exception as e:
        print(f"An error occurred: {e}")
        break
    
print("done!")

print("Data collection complete, saving to JSON file.")

result_data = []
for write_dt, item_nm, content, ranking in zip(write_dt_lst, item_nm_lst, content_lst, ranking_lst):
    result_data.append({
        'RD_WRITE_DT': write_dt,
        'RD_ITEM_NM': item_nm,
        'RD_CONTENT': content,
        'RD_RANK': ranking
    })


with open('sentiment-service/NLP/data/navershopping_review.json', 'w', encoding='utf-8') as f:
    json.dump(result_data, f, ensure_ascii=False, indent=4)
