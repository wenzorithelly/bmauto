import re
import pandas as pd
import numpy as np
from IPython import display
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager, ChromeType


class PriceSuggestion:
    def __init__(self):
        self.browser = self.start_driver()
        self.browser.get("https://www.mercadolivre.com.br/")

    def start_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument(
            "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.77 "
            "Safari/537.36")
        # https://stackoverflow.com/a/26283818/1689770
        options.add_argument("start-maximized")
        # / https://stackoverflow.com/a/43840128/1689770
        options.add_argument("enable-automation")
        options.add_argument("--window-size=1360,500")
        # only if you are ACTUALLY running headless
        options.add_argument("--headless=new")
        # https://stackoverflow.com/a/50725918/1689770
        options.add_argument("--no-sandbox")
        # https://stackoverflow.com/a/43840128/1689770
        options.add_argument("--disable-infobars")
        # /https://stackoverflow.com/a/50725918/1689770
        options.add_argument("--disable-dev-shm-usage")
        # https://stackoverflow.com/a/49123152/1689770
        options.add_argument("--disable-browser-side-navigation")
        options.add_argument("--disable-gpu")

        s = Service(ChromeDriverManager(
            chrome_type=ChromeType.CHROMIUM, cache_valid_range=1).install())
        driver = webdriver.Chrome(service=s, options=options)
        display.clear_output(wait=False)

        return driver

    def remove_outliers(self, df: pd.DataFrame = None,
                        columns: list = None,
                        threshold: int = 3):
        df_no_outliers = df.copy()

        for column in columns:
            z_scores = np.abs(
                (df[column] - df[column].mean()) / df[column].std())
            outliers = df[z_scores > threshold]
            df_no_outliers = df_no_outliers.drop(outliers.index)

        return df_no_outliers

    def get_price_suggestion(self, product: str = None):
        driver = WebDriverWait(self.browser, 5)
        search_name = driver.until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/header/div/div[2]/form/input')))
        search_name.click()
        search_name.send_keys(product + Keys.RETURN)

        data = []

        product_name = driver.until(EC.presence_of_all_elements_located(
            (By.CLASS_NAME, 'ui-search-item__title')))
        prices = driver.until(EC.presence_of_all_elements_located(
            (By.CLASS_NAME, 'ui-search-price--size-medium')))
        for name, price in zip(product_name, prices):
            info = name.text
            out = info.splitlines()[0]
            price_text = price.text
            numbers = re.findall(r'\d+', price_text)
            first_number = int(numbers[0] if numbers else None)
            all_info = {
                'product_name': out,
                'price': first_number
            }
            data.append(all_info)
        match = product.split()[0]
        pattern = rf"\b{match}\b"
        df = pd.DataFrame(data)
        df['product_name'] = df['product_name'].str.lower()
        clean_df = df[df['product_name'].str.contains(pattern)]

        filtered_df = self.remove_outliers(clean_df, ['price'], threshold=2)

        suggestion = np.mean(filtered_df['price'].nlargest(10))

        return suggestion
