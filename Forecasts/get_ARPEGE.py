from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import Select
import selenium

path = r'.'

for i in range(10):
    options = webdriver.ChromeOptions()
    prefs = {'download.default_directory': r"E:\koray\HH"}
    options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(r"E:\koray\HH\chromedriver.exe", chrome_options=options)  # Path to chrome webdriver
    driver.get("https://donneespubliques.meteofrance.fr/?fond=produit&id_produit=130&id_rubrique=51")
    select = Select(driver.find_element_by_id('packageselect'))
    select.select_by_visible_text('SP1 - Paramètres courants à la surface')
    select = Select(driver.find_element_by_id('timeselect'))
    select.select_by_index(i)
    select = Select(driver.find_element_by_id('reftimeselect'))
    select.select_by_index(0)

    driver.find_element_by_class_name("publication-btn").submit()
    time.sleep(95)
    driver.close()
