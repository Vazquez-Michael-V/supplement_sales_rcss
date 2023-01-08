#Selenium imports for website navigation.
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains

#Pandas and numpy for data tables.
import pandas as pd
import numpy as np

# Matplotlib for plotting.
import matplotlib.pyplot as plt

# Date and time imports.
import time
from datetime import datetime

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = r'C:\Program Files\Google\Chrome Beta\Application\chrome.exe'

PATH = "C:\Program Files (x86)\chromedriver.exe" #Directory of the Chromedriver
serv = Service(PATH)
driver = webdriver.Chrome(service=serv, options=chrome_options)

# WEBSITE = "https://ronniecoleman.net/collections/pre-workout-1"
WEBSITE = "https://ronniecoleman.net/collections/protein-mass-gainer-1"

driver.get(WEBSITE)
driver.maximize_window()
web_title = driver.title
print(WEBSITE)
print(web_title)

time.sleep(2)

products = driver.find_elements(By.CLASS_NAME, 'container')

page_link_text = []
# print(products)
for product in products:
    # print(product.text)
    try:
        page_products = product.find_element(By.CLASS_NAME, 'grid-uniform').find_elements(By.TAG_NAME, 'h4')
        print(len(page_products))   
        for e in page_products:
            print(e.get_attribute('innerText'))
            page_link_text.append(e.get_attribute('innerText'))      
        
    except:
        pass

print(page_link_text)
print(len(page_link_text))
for t in page_link_text:
    print(type(t))


supplements_dict = {supp_name: {'supp_price': None, 'supp_sold': None, 'timeframe': None} for supp_name in page_link_text}
print(supplements_dict)
price_not_found_text = "PriceNotFound"
num_sold_not_found_text = "NumSoldNotFound"
timeframe_not_found_text = "TimeframeNotFound"
for supplement_name in page_link_text:
    supplement_button = driver.find_element(By.LINK_TEXT, supplement_name)
    supplement_button.click()
    
    # Find the price of the product.
    # Sold out products do not have a price displayed. Thus sold out products will cause a TimeoutException.
    try:
        product_price = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'ProductPrice'))
            )
        print(product_price.text)
    except TimeoutException:
        supplements_dict[supplement_name]['supp_price'] = price_not_found_text     
    else:
        supplements_dict[supplement_name]['supp_price'] = product_price.text
    
    
    # Obtain the number of supplements sold in the last 24 hours.
    try:
        num_sold = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'TotalSold'))
            )
        print(num_sold.text)    
    except TimeoutException:
        supplements_dict[supplement_name]['supp_sold'] = num_sold_not_found_text    
    else:
        supplements_dict[supplement_name]['supp_sold'] = num_sold.text    
        
        
    # Make sure it's a 24 hour time frame.
    try:
        sold_timeframe = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'InHours'))
            )
        print(sold_timeframe.text)
    except TimeoutException:
        supplements_dict[supplement_name]['timeframe'] = timeframe_not_found_text    
    else:
        supplements_dict[supplement_name]['timeframe'] = sold_timeframe.text
        
    time.sleep(5)
    driver.back()

print(supplements_dict)


# Put supplements_dict into a DataFrame.
temp_dfs_list = []
m = 0
for key in supplements_dict.keys():
    item_row = []
    item_row.append(key)
    item_row.append(supplements_dict[key]['supp_price'])
    item_row.append(supplements_dict[key]['supp_sold'])
    item_row.append(supplements_dict[key]['timeframe'])
    
    df_temp = pd.DataFrame(data={m: item_row})
    df_temp.reset_index(inplace=True, drop=True)
    print(type(df_temp))
    df_temp = df_temp.T
    temp_dfs_list.append(df_temp)
    m+=1
    print(df_temp)

df_suppies = pd.concat(temp_dfs_list)
# Reset the index just to be safe.
df_suppies.reset_index(drop=True, inplace=True)



# This rename mapping depends on the order of the append lines in the for loop over supplements_dict.keys().
df_suppies.rename(columns={0: 'supplement_name',
                           1: 'supplement_cost',
                           2: 'num_sold',
                           3: 'timeframe_sold'
                           }, inplace=True)

df_suppies['supp_cost_amount'] = df_suppies['supplement_cost'].copy()
cost_amount_rename = {' USD': '', r'\$':'', ' ':''}
df_suppies.replace({'supp_cost_amount': cost_amount_rename}, regex=True, inplace=True)
df_suppies['supp_cost_amount'] = pd.to_numeric(df_suppies['supp_cost_amount'], errors='coerce')

print(df_suppies.shape)
print(df_suppies)
print(df_suppies.info())


df_barh_supp_cost = df_suppies[['supp_cost_amount', 'supplement_name']].copy()
df_barh_supp_cost.sort_values(by=['supplement_name'], ascending=False, inplace=True)
df_barh_supp_cost.set_index('supplement_name', inplace=True)
print(df_barh_supp_cost.info())

# ax = df_barh_supp_cost.plot(kind='barh', legend=False, xlabel="Supplement Name", title='Supplements by Cost')

fig, ax = plt.subplots(figsize=(9,4))
df_barh_supp_cost.plot(ax=ax, 
        kind='barh', legend=False, xlabel="Supplement Name", title='Proteins by Cost')
ax.xaxis.set_major_formatter('${x:1.2f}')
plt.show()
fig.savefig('proteins_by_cost.png', dpi=300, bbox_inches='tight')









