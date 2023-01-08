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

# Date and time imports.
import time
from datetime import datetime


chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = r'C:\Program Files\Google\Chrome Beta\Application\chrome.exe'


PATH = "C:\Program Files (x86)\chromedriver.exe" #Directory of the Chromedriver
serv = Service(PATH)
driver = webdriver.Chrome(service=serv, options=chrome_options)

WEBSITE = "https://ronniecoleman.net/"
driver.get(WEBSITE)
driver.maximize_window()
web_title = driver.title
print(WEBSITE)
print(web_title)

time.sleep(2)

# Want to hover over the "Shop by Category" button, and then get all the categories.

menu = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[4]/div[1]/header/div[3]/div/div[1]/ul/li[1]/a')
# ActionChains(driver).move_to_element(menu).click(hidden_submenu).perform()

actions = ActionChains(driver)
actions.move_to_element(menu)
actions.perform()
time.sleep(2)
print("\n")
categories = driver.find_elements(By.XPATH, '/html/body/div[1]/div[2]/div[4]/div[1]/header/div[3]/div/div[1]/ul/li[1]/ul/div/div[1]/div/div/div[1]/div/div/ul')
print(type(categories))
# The categories show up as one big string.
print(len(categories))

categories_text = [category.text.split(sep="\n") for category in categories][0]
print(categories_text)

driver.refresh()
time.sleep(2)

categories_supplements_dict = {category: {} for category in categories_text[:]}
print(categories_supplements_dict)


price_not_found_text = "PriceNotFound"
num_sold_not_found_text = "NumSoldNotFound"
timeframe_not_found_text = "TimeframeNotFound"


for category in categories_text:    
    actions = ActionChains(driver)
    menu = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[4]/div[1]/header/div[3]/div/div[1]/ul/li[1]/a')
    actions.move_to_element(menu)
    actions.perform()
    time.sleep(2)
    
    hidden_submenu = driver.find_element(By.LINK_TEXT, category)
    actions.click(hidden_submenu)
    actions.perform()
    time.sleep(2)
    
    # This next loop will click through all the products on the page.
    # TODO: Need to add some checks for a next page button. 24 items fit on a page. if len(products) > 24 then check for a next page button?
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
    
    for supplement_name in page_link_text:
        supplement_button = driver.find_element(By.LINK_TEXT, supplement_name)
        supplement_button.click()
        print(supplement_name)
        # Driver is on the page item here.
        categories_supplements_dict[category][supplement_name] = {}

        # Find the price of the product.
        # Sold out products do not have a price displayed. Thus sold out products will cause a TimeoutException.
        try:
            product_price = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'ProductPrice'))
                )
            print(product_price.text)
        except TimeoutException:
            categories_supplements_dict[category][supplement_name]['supp_price'] = price_not_found_text
        else:
            categories_supplements_dict[category][supplement_name]['supp_price'] = product_price.text      

        
        # Obtain the number of supplements sold in the last 24 hours.
        try:
            num_sold = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'TotalSold'))
                )
            print(num_sold.text)    
        except TimeoutException:
            categories_supplements_dict[category][supplement_name]['supp_sold'] = num_sold_not_found_text 
        else:
            categories_supplements_dict[category][supplement_name]['supp_sold'] = num_sold.text        
        
        # Make sure it's a 24 hour time frame.
        try:
            sold_timeframe = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'InHours'))
                )
            print(sold_timeframe.text)
        except TimeoutException:
            categories_supplements_dict[category][supplement_name]['timeframe'] = timeframe_not_found_text   
        else:
            categories_supplements_dict[category][supplement_name]['timeframe'] = sold_timeframe.text      

        
        print(categories_supplements_dict)
        print("\n")
        
        print(categories_supplements_dict[category].keys())
        

        
        time.sleep(5)
        driver.back()  
    
    driver.back()
    
    


print(categories_supplements_dict['Stacks & Bundles'].keys())   
print(len(categories_supplements_dict['Stacks & Bundles'].keys()))




























