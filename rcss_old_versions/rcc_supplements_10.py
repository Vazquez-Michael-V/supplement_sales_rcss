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
import pytz

import json

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = r'C:\Program Files\Google\Chrome Beta\Application\chrome.exe'
chrome_options.add_argument('--incognito')


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

# Ronnie Coleman supplements customer service phones are open 9am-5pm Eastern, per the top right of the homepage on the website.
timezone_est = pytz.timezone('EST')
scrape_timestamp_start = datetime.now(tz=timezone_est).strftime('%Y-%m-%d %I:%M:%S %p')
print(f'Starting web scrape {scrape_timestamp_start}')


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

# Need to close the popup ad, if it appears on the screen.
# The pop up ad takes a few seconds to appear.
time.sleep(15)
try:
    pop_up_ad = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[10]/div/div/div/div/div/div/form/div/div[2]/div[1]/div/input'))
        )
except TimeoutException:
    print("No pop up ad found on the page.")
else:
    print("Need to close the pop up ad.")
    close_ad_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[10]/div/div/div/div/div/div/button'))
        )   
    # driver.find_element(
    #     By.XPATH, )
    close_ad_button.click()
    print("Ad should be closed.")
    time.sleep(5)

# TODO: Maybe get rid of this and use np.nan instead.
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
    # There's a class called "pagination", which holds the next page buttons.
    
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
        
        # TODO: Prices vary based on selected size, but this is not reflected in the number of sold items.
        # Thereforce, will find the minimum price and the maximum price, and create an average price column.        
        
        try:
            product_default_price = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'ProductPrice'))
                )
            print(product_default_price.text)
        except TimeoutException:
            categories_supplements_dict[category][supplement_name]['supp_default_price'] = price_not_found_text
        else:
            categories_supplements_dict[category][supplement_name]['supp_default_price'] = product_default_price.text
        
        # Select the largest option, aka get maximum price.
        try:
            product_options = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'swatch-option1'))               
                ).find_element(By.TAG_NAME, 'ul').find_elements(By.CLASS_NAME, 'swatch-view-item')  
            
            print("Product options:")
            print(len(product_options))
            
            # TODO: Working to select the different product options.
            # Website has several different options for selecting items.
            for opt in product_options:
                # print(opt.get_attribute('innerText')) 
                print(opt.get_attribute('aria-label')) # Keep the aria-label, as this seems to have more info associated with it.
                # opt_to_click = opt.find_element(By.XPATH, "//div[@class='swatch-image swatch-selector swatch-allow-animation']")

                # opt_to_click.click()
                # print(f"Clicking {opt.get_attribute('aria-label')}")
                # time.sleep(5)
                
            # Finding the price should be the same code. Just need to select the largest option first.
            product_max_price = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'ProductPrice'))
                )
            print(product_max_price.text)
            
        except TimeoutException:
            categories_supplements_dict[category][supplement_name]['supp_max_price'] = price_not_found_text
        else:
            categories_supplements_dict[category][supplement_name]['supp_max_price'] = product_max_price.text
        
        
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
        
        # Obtain number of current views.
        try:
            print("Finding number of current views...")
            current_views = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'visitor_counter_visitors'))
                )
            print(current_views.text)
        except TimeoutException:
            print("Could not find current number of views.")
            categories_supplements_dict[category][supplement_name]['current_views'] = np.nan
        else:
            categories_supplements_dict[category][supplement_name]['current_views'] = current_views.text
        
        
        # Obtain product rating and number of reviews.
        try:
            print("Finding reviews info...")
            reviews_info_id = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'goToReview'))
                )
            reviews_info_class = reviews_info_id.find_element(By.CLASS_NAME, 'loox-rating')
            print(reviews_info_class.get_attribute('data-rating'))
            print(reviews_info_class.get_attribute('data-raters'))
            print(reviews_info_class.get_attribute('aria-label'))
        except TimeoutException:
            print("Could not find reviews info.")
            categories_supplements_dict[category][supplement_name]['product_rating'] = np.nan
            categories_supplements_dict[category][supplement_name]['product_num_reviews'] = np.nan
        else:
            categories_supplements_dict[category][supplement_name]['product_rating'] = reviews_info_class.get_attribute('data-rating')
            categories_supplements_dict[category][supplement_name]['product_num_reviews'] = reviews_info_class.get_attribute('data-raters')

        
        # Make sure it's a 24 hour time frame.
        # Also add the time website was scraped.
        try:
            sold_timeframe = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'InHours'))
                )
            print(sold_timeframe.text)
        except TimeoutException:
            categories_supplements_dict[category][supplement_name]['timeframe'] = timeframe_not_found_text   
        else:
            categories_supplements_dict[category][supplement_name]['timeframe'] = sold_timeframe.text    
        finally:
            categories_supplements_dict[category][supplement_name]['scrape_timestamp'] = datetime.now(tz=timezone_est)\
                .strftime('%Y-%m-%d %I:%M:%S %p') # datetime objects aren't JSON serializable.


        time.sleep(5)
        driver.back()  
    
    driver.back()



# Save the dictionary as a json file.
# Filenames can't contain a colon ':' so use ISO 8601 datetime format.
timezone_utc = pytz.timezone('UTC')
scrape_timestamp_end = datetime.now(tz=timezone_utc).strftime('%Y%m%dT%I%M%SZ')
print(scrape_timestamp_end)
with open(f'rcc_{scrape_timestamp_end}.json', 'w') as json_file:
    json.dump(categories_supplements_dict, json_file, indent=4)
    



# with open('rcc_20221224T055624Z - Copy.json', 'r') as j:
#     categories_supplements_dict = json.load(j)


# Split the dictionary into Dataframes based on product category. ie create tables for each category.
# NOTE: '\u2122' is the trademark TM character.
# print(categories_supplements_dict['Pre Workout']['YEAH BUDDY\u2122 Pre-Workout Powder'])

categories_df_dict = {category: 
                      [pd.DataFrame.from_dict(categories_supplements_dict[category], 'index').reset_index()\
                       .rename(columns={'index': 'product_name'})] for category in categories_text[:]}


with pd.ExcelWriter(f'rcc_{scrape_timestamp_end}.xlsx') as writer:
    for k,v in categories_df_dict.items():
        print(k)
        try: 
            v[0].replace({k: np.nan for k in [price_not_found_text, num_sold_not_found_text, timeframe_not_found_text]},
                                  inplace=True)
            
            v[0].replace('', np.nan, inplace=True)
            
            # Remove nonsense from the supp_default_price column, so that it can be converted to float.
            v[0]['supp_default_price'] = v[0]['supp_default_price']\
                .str.replace('$', '', regex=True)\
                .str.replace('Sold Out', '', regex=True)\
                .str.replace(' USD', '', regex=True)
            v[0]['supp_default_price'] = v[0]['supp_default_price'].astype('float64')
                
            # errors='coerce' will work, but might result in data loss. Want to clean up any ValueError, not supress it.
            # ie a value of %20.00 would be sent to nan even though the value should be cleaned up to be 20.00
            # v[0]['supp_default_price'] = pd.to_numeric(v[0]['supp_default_price'], errors='coerce')
        
            # Send other columns to type float. These columns are less messy than supp_default_price.
            v[0][['supp_sold', 'current_views', 'product_rating', 'product_num_reviews', 'timeframe']] = \
                v[0][['supp_sold', 'current_views', 'product_rating', 'product_num_reviews', 'timeframe']].astype('float64')
                
            # Create a scrape_date column.
            v[0]['scrape_date'] = pd.to_datetime(v[0]['scrape_timestamp']).dt.date
            
            # Put the product category as a column on each Dataframe.
            v[0]['product_category'] = k
            
        except KeyError as e:
            print(f'KeyError on {k}, {v[0].columns.to_list()}')
            print(e)
            print(f'\tSending DataFrame {k} to excel without columns cleanup.')
            sheetname = ''.join(s for s in k if s.isalnum())
            v[0].to_excel(writer, sheet_name=sheetname, index=False)
        else:
            sheetname = ''.join(s for s in k if s.isalnum())
            v[0].to_excel(writer, sheet_name=sheetname, index=False)

# Have a look at the DataFrame of Pre Workout category.
df_preworkout = categories_df_dict['Pre Workout'][0]
print(df_preworkout.info())
print(df_preworkout.head(5))
