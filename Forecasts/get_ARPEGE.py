#!usr/local/python3
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import Select
import selenium

path = r'.'

def get_data(i):
    try:
        options = webdriver.ChromeOptions()
        prefs = {'download.default_directory': '/home/cak/Desktop/Jupyter-lumped-models/Forecasts/ARPEGE'}
        options.add_experimental_option('prefs', prefs)
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome('/home/cak/Desktop/chrome/chromedriver',
                                  options=options)  # Path to chrome webdriverl
        driver.get("https://donneespubliques.meteofrance.fr/?fond=produit&id_produit=130&id_rubrique=51")
        select = Select(driver.find_element_by_id('packageselect'))
        select.select_by_index(6)
        select = Select(driver.find_element_by_id('timeselect'))
        select.select_by_index(i)
        select = Select(driver.find_element_by_id('reftimeselect'))
        select.select_by_index(0)
        print(i, ' started')
        driver.find_element_by_class_name("publication-btn").submit()
        time.sleep(180)
        print(i, ' finished')
        driver.close()
    except:
        driver.close()
        get_data(i)


for i in range(10):
    get_data(i)
