from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.common.proxy import ProxyType
import time
import random
import json
import pprint
import re
import ast
from pathlib import Path
from proxies.check_valid_proxy import check_proxy_valid

# Use proxy (multiple) --> OK
# Go each page and get all link
# Get data from link
# Add to csv (save page, column for next time)

# Dựng class theo cấp độ js có css class
# Nếu nằm bên trong 

class PageContainer():
    def __init__(self, base_link):
        self.__base_link = base_link

        with open('proxies/proxies_valid.txt', 'r') as file:
            self.proxies_list = file.read().split('\n')

        self.chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument("--window-size=1200x880")
        self.chrome_options.add_argument("--start-maximized")
        proxy_stt = random.randrange(0, len(self.proxies_list))

        self.chrome_options.proxy = Proxy({
            'proxyType': ProxyType.MANUAL,
            'httpProxy': self.proxies_list[proxy_stt],
            'sslProxy': self.proxies_list[proxy_stt]
        })

        # chrome_options.add_argument('--ignore-ssl-errors=yes')
        # chrome_options.add_argument('--ignore-certificate-errors')
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument("--incognito")

        self.driver = webdriver.Chrome(options=self.chrome_options)

        self.driver.implicitly_wait(5)

        with open('previous_crawl.txt', 'r') as file:
            self.page_num, self.link_num = map(int, file.read().split('\n'))

    def get_link_page(self, page):
        if page:
            if page == 1: return self.__base_link
            else: return f'{self.__base_link}/p{page}'
        else:
            if self.page == 1: return self.__base_link
            else: return f'{self.__base_link}/p{self.page_num}'

    def get_proxy_random(self):
        proxy_stt = random.randrange(0, len(self.proxies_list))

        proxy = Proxy({
            'proxyType': ProxyType.MANUAL,
            'httpProxy': self.proxies_list[proxy_stt],
            'sslP`roxy': self.proxies_list[proxy_stt]
        })

        return proxy
    
    def get_driver_with_another_proxy(self):
        self.chrome_options.proxy = self.get_proxy_random()

        driver = webdriver.Chrome(options=self.chrome_options)
        driver.implicitly_wait(5)

        return driver

    def get_all_links_in_page(self, page):
        try: 
            print(f"\n------------------------ LẤY LINK TRONG TRANG {self.page_num} ------------------------ ")
            self.driver = self.get_driver_with_another_proxy()

            self.driver.get(self.get_link_page(page))

            all_elements_have_link = self.driver.find_elements(By.CSS_SELECTOR, value='.js__card.js__card-full-web > .js__product-link-for-product-id')
            all_links = [ele.get_attribute('href') for ele in all_elements_have_link if ele.get_attribute('href')]

            return all_links
        except:
            time.sleep(1)
            print(f"LẤY LẠI: {page}")
            return self.get_all_links_in_page(page)
        
    def get_data_safe_find(self, selector, multi_value = False, scope_element = None, return_text = False):
        try:
            scope = scope_element if scope_element else self.driver

            if multi_value:
                elements = scope.find_elements(By.CSS_SELECTOR, value = selector)
                return elements
            else:
                element = scope.find_element(By.CSS_SELECTOR, value = selector)
                if return_text:
                    return element.text
                return element
        except:
            return None
    
    def add_data_to_json(self, data):
        path = Path('./data.json')
        merged_data = [data]
        if path.exists():
            with open(path, 'r') as file:
                try:
                    data_in_file = json.load(file)
                except:
                    data_in_file = []
                
                merged_data.extend(data_in_file)

        with open(path, 'w') as file:
            json.dump(merged_data, file, ensure_ascii=False)
        
        self.link_num += 1
        self.change_previous_crawl()
        print('---- LẤY THÀNH CÔNG ----')
    
    def change_previous_crawl(self):
        with open('./previous_crawl.txt', 'w') as file:
            file.write(f'{self.page_num}\n{self.link_num}')
 
    def get_data_in_link(self, link):
        print(f'\n---- LẤY DỮ LIỆU LINK {self.link_num} ----')
        time.sleep(2)
        try:
            self.driver.get(link)

            # Get undisplayed data
            script_elements = self.get_data_safe_find('script[type="text/javascript"]', multi_value=True) # script
            undisplayed_data_container = '' # contain text inside script
            for i in script_elements:
                text_inside = i.get_attribute('innerHTML').strip()
                if text_inside.find('getListingRecommendationParams') != -1:
                    undisplayed_data_container = text_inside
                    break

            undisplayed_text_start = 0
            undisplayed_text_end = 0

            for i in range(len(undisplayed_data_container)):
                # get nearest {
                if undisplayed_data_container[i] == '{': 
                    undisplayed_text_start = i
                # get first }
                if undisplayed_data_container[i] == '}':
                    undisplayed_text_end = i
                    break
            
            undisplayed_in_curly_braces = undisplayed_data_container[undisplayed_text_start:(undisplayed_text_end + 1)]
            undisplayed_change_before_to_dict = undisplayed_in_curly_braces.replace('`', "'").replace('"', "'")
            undisplayed_change_before_to_dict = re.sub(r'(\w+): ', r'"\1":', undisplayed_change_before_to_dict)
            undisplayed_info = ast.literal_eval(undisplayed_change_before_to_dict)

            # landlord_data
            landlord_data_container = ''
            for i in script_elements:
                text_inside = i.get_attribute('innerHTML').strip()
                if text_inside.find('FrontEnd_Product_Details_ContactBox') != -1:
                    landlord_data_container = text_inside
                    break
            
            landlord_text_start = landlord_data_container.index('window.FrontEnd_Product_Details_ContactBox')
            landlord_text_start = landlord_data_container.find('{', landlord_text_start)
            landlord_text_end = 0

            landlord_container_from_first_curly_braces = landlord_data_container[landlord_text_start:]

            array = [] # contain { } , as same as stack

            for i in range(len(landlord_container_from_first_curly_braces)):
                if landlord_container_from_first_curly_braces[i] == '{': 
                    array.append(landlord_container_from_first_curly_braces[i])
                if landlord_container_from_first_curly_braces[i] == '}':
                    array.pop()
                    if len(array) == 0:
                        landlord_text_end = i + 1
                        break

            landlord_in_curly_braces = landlord_container_from_first_curly_braces[0:landlord_text_end] 
            landlord_change_before_to_dict = landlord_in_curly_braces.replace('`', "'").replace('"', "'")
            landlord_change_before_to_dict = re.sub(r'(\w+): ', r'"\1":', landlord_change_before_to_dict)  
            landlord_change_before_to_dict = re.sub(r"(parseInt\(('\d+'))\)", r'\2', landlord_change_before_to_dict)  
            landlord_info = ast.literal_eval(landlord_change_before_to_dict)

            key_needed = ['nameSeller', 'emailSeller', 'userId']
            landlord_needed_info = {key: value for key, value in landlord_info.items() if key in key_needed}

            # Get display data
            displayed_data_container = {}

            displayed_data_container['Link'] = link

            displayed_data_container['Title'] = self.get_data_safe_find('.re__pr-title.pr-title.js__pr-title', return_text=True)

            displayed_data_container['Address'] = self.get_data_safe_find('.re__pr-short-description.js__pr-address', return_text=True)

            displayed_data_container['Verified'] = True if self.get_data_safe_find('.re__pr-stick-listing-verified') else None

            images = self.get_data_safe_find('.re__media-thumb-item.js__media-thumbs-item > img', multi_value=True)

            link_images = [image_element.get_attribute('src') for image_element in images if image_element.get_attribute('src')]

            displayed_data_container['Images'] = ','.join(link_images)

            a = self.get_data_safe_find('.re__pr-short-info-item.js__pr-short-info-item', multi_value=True)
            for couple in a:
                key = self.get_data_safe_find('.title', scope_element=couple ,return_text=True)

                if not key: continue

                value = self.get_data_safe_find('.value', scope_element=couple ,return_text=True)

                ext = self.get_data_safe_find('.ext', scope_element = a, return_text=True)
                
                displayed_data_container[key] = value
                displayed_data_container[key + ' ' + 'ext'] = ext

            displayed_data_container['Detail'] = self.get_data_safe_find('.re__detail-content', return_text=True)

            b = self.get_data_safe_find('.re__pr-specs-content-item', multi_value=True)
            for couple in b:
                key = self.get_data_safe_find('.re__pr-specs-content-item-title', scope_element=couple ,return_text=True)

                if not key: continue

                value = self.get_data_safe_find('.re__pr-specs-content-item-value', scope_element=couple ,return_text=True)

                displayed_data_container[key] = value        

            c = self.get_data_safe_find('.re__pr-short-info-item.js__pr-config-item', multi_value=True)
            for couple in c:
                key = self.get_data_safe_find('.title', scope_element=couple ,return_text=True)

                if not key: continue

                value = self.get_data_safe_find('.value', scope_element=couple ,return_text=True)

                displayed_data_container[key] = value    
        
            # displayed_data_container.update(undisplayed_info)
            # displayed_data_container.update(landlord_needed_info)
            full_data = {
                'landlord': landlord_needed_info,
                'product_info_number': undisplayed_info,
                'product_info': displayed_data_container
            }

            return full_data
        except:
            return self.get_data_in_link(link)
    
    def run(self): # Chuaw xong can chinh ti
        while True:
            all_links = self.get_all_links_in_page(self.get_link_page(self.page_num))
            for i in range(len(all_links)):
                if i >= self.link_num:
                    data = self.get_data_in_link(all_links[i])
                    # print(data)
                    self.add_data_to_json(data)
            
            self.page_num += 1
            self.link_num = 0
            self.change_previous_crawl()

    def quit(self):
        self.driver.quit()


page = PageContainer('https://batdongsan.com.vn/cho-thue-nha-tro-phong-tro-tp-hcm')
page.run()
# print(len(page.get_all_links_in_page(page.get_link_page(16))))
