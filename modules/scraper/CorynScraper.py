import json
import time

from os import getcwd
from re import search

from selenium.webdriver.common.by import By
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.common.exceptions import NoSuchElementException

from modules.file.FileHelper import FileHelper


class CorynScraper:
    def __init__(self):

        options = FirefoxOptions()

        options.add_argument("--headless")
        options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"

        root = getcwd()
        self.browser = Firefox(executable_path=fr"{root}\\modules\\scraper\\geckodriver.exe", options=options)

        self.base_urls = {
            'equipments': 'https://coryn.club/item.php?&show=10&order=name&special=eq&p=0',
            'consumables': 'https://coryn.club/item.php?&show=10&type=1&order=name&p=0',
            'crystals': 'https://coryn.club/item.php?&show=11&order=name&special=xtal&p=0',
            'materials': 'https://coryn.club/material.php?proc=1'
        }


    def find_element(self, by: str, value: str):
        return self.browser.find_element(by, value)


    def find_elements(self, by: str, value: str):
        return self.browser.find_elements(by, value)


    def get_last_page_number_from_html(self):
        url = self.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[3]/div/a[9]").get_attribute('href')
        return int(url.split('&')[-1].split('=')[-1])


    def get_page(self, url):
        self.browser.get(url)
        time.sleep(5)


    def go_to_page(self, page_type, page_number):

        valid_type = page_type in self.base_urls.keys()

        if valid_type:
            base_url = self.base_urls[page_type]

            base_url = base_url.replace("p=0", f"p={page_number}")
            base_url = base_url.replace("proc=1", f"proc={page_number}")

            self.get_page(base_url)

        return valid_type


    def get_items_list(self):
        items_list = self.find_elements(By.XPATH, "/html/body/div[2]/div[2]/div[2]/div")
        items_list = [x for x in items_list if x.text != '']
        return items_list


    def get_item_common_attributes(self, item):

        item_attributes = {
            "Name":    "div[1]",
            "Sell":    "div[2]/?/div/div[1]/p[2]",
            "Process": "div[2]/?/div/div[2]/p[2]",
        }

        try:
            item_attributes_list = item_attributes.keys()

            for attribute in list(item_attributes_list):

                child = item.find_elements(By.XPATH, 'div[2]/div')

                xpath = item_attributes[attribute]
                xpath = xpath.replace('?', 'div' if len(child) == 1 else 'div[2]')

                content = item.find_element(By.XPATH, xpath).text

                if attribute == 'Name':
                    matches = search(r"^(?P<Name>.*) \[(?P<Category>.*)]$", content)

                    if matches:
                        item_attributes[attribute] = matches.group("Name")
                        item_attributes["Category"] = matches.group("Category")

                else:
                    item_attributes[attribute] = content

        except NoSuchElementException:
            pass

        finally:
            return item_attributes


    def get_item_exclusive_attributes(self, item_attributes, item):
        try:

            item_exclusive_attributes = item.find_elements(By.XPATH, "ul/li[1]/div[2]/div")[1:]

            for attribute in item_exclusive_attributes:

                attribute_name = attribute_value = ""

                while attribute_name == "" or attribute_value == "":
                    attribute_name = attribute.find_element(By.XPATH, 'div[1]').text
                    attribute_value = attribute.find_element(By.XPATH, 'div[2]').text

                item_attributes[attribute_name] = float(attribute_value)

        except NoSuchElementException:
            pass

        finally:
            return item_attributes


    def scrape(self, scraping_type: str):

        if scraping_type in self.base_urls.keys():

            first_page = 0
            start_page = 0

            self.go_to_page(scraping_type, first_page)
            last_page = self.get_last_page_number_from_html()

            file = FileHelper(f"{scraping_type}.json")

            file.write('[\n')

            for page in range(start_page, last_page + 1):

                print(f"Scraping Page ({scraping_type}): " + str(page))

                items_list = self.get_items_list()

                for item_number, item in enumerate(items_list):

                    item_attributes = self.get_item_common_attributes(item)
                    item_attributes = self.get_item_exclusive_attributes(item_attributes, item)

                    item_attributes = json.dumps(item_attributes)

                    comma = ","
                    if item_number == len(items_list) - 1 and page == last_page:
                        comma = ""

                    file.write(item_attributes + comma + '\n')

                self.go_to_page(scraping_type, page + 1)

            file.write(']')
