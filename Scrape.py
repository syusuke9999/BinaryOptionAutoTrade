from typing import Dict, Any, Union
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support import expected_conditions as ec, expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
import Parameter
import re
import os
import time
import BinaryOptionTrade

selected_menu = ""
selected_term = ""


order_flag = False
order_info = {}

options = ChromeOptions()
driver = webdriver.Chrome(executable_path='c:\\chromedriver_win32\\chromedriver.exe', options=options)


def get_selected_menu_and_term():
    global driver, selected_menu, selected_term
    soup = BeautifulSoup(driver.page_source, "lxml")
    game_tab = soup.select_one('#assetsGameTypeZoneRegion')
    selected = game_tab.find_all("li", attrs={"class": "gameTab selected"})
    selected_menu = selected[0].contents[1].attrs['id']
    term = soup.select_one("#assetsCategoryFilterZoneRegion > div > div.tab.selected")
    selected_term = term.contents[1].text
    return selected_menu, selected_term


def transit_to_login_page():
    global driver
    driver.get(Parameter.top_page_url)
    WebDriverWait(driver, 60).until(expected_conditions.url_contains(Parameter.top_page_url))
    driver.execute_script(Parameter.script_to_transition_login_page)
    WebDriverWait(driver, 60).until(expected_conditions.url_contains(Parameter.login_page_url))
    if driver.current_url == Parameter.login_page_url:
        return True
    else:
        return False


def login_to_member_page():
    global driver
    """
    Returns:
        bool:
            Represent Log-in procedure is succeeded or failed.
            True: Log-in procedure is succeeded.
            False: Log-in procedure is failed because of some reason.
    """
    user_name = driver.find_element_by_id(Parameter.element_id_of_user_name)
    user_name.send_keys(Parameter.user_name)
    pass_word = driver.find_element_by_id(Parameter.element_id_of_password)
    pass_word.send_keys(Parameter.password)
    login_button = driver.find_element_by_css_selector(Parameter.element_css_selector_of_login_button)
    login_button.click()
    WebDriverWait(driver, 60).until(ec.presence_of_all_elements_located)
    source_soup = BeautifulSoup(driver.page_source, "lxml")
    logged_in = source_soup.select("Logout")
    if logged_in is not None:
        return True
    else:
        print("ログイン出来ませんでした")
        return False


def wait_signal():
    global driver, order_info, order_flag
    while order_flag is False:
        order_info = detect_signal()
    if order_flag:
        send_order()


def detect_signal():
    """
    指定されたフォルダ内のorder.txtファイルを監視して、オーダーが出力されたら内容を読み込む

    Returns
    -------    　辞書型オブジェクト
    order_info : {symbol:通貨ペア,sign:サインの種類（high・low）,term:注文形態がHighLow・highlowスプレッドの場合かつ、
                期間が15分の場合、3種類ある締め切り時刻の内どれを購入するか}
    """
    global order_flag
    if os.path.exists(Parameter.Sign_file_path):
        time.sleep(1)
        reader = open(Parameter.Sign_file_path, "r")
        order_info['symbol'] = reader.readline()
        if "/" not in order_info['symbol']:
            symbol = order_info['symbol'][0:3] + "/" + order_info['symbol'][3:6]
            order_info['symbol'] = symbol
        order_info['sigh'] = reader.readline()
        order_info['term'] = reader.readline()
        reader.close()
        print("symbol=" + order_info['symbol'] + "sign=" +
              order_info['sigh'] + "term=" + order_info['term'])
        while os.path.exists(Parameter.Sign_file_path):
            os.remove(Parameter.Sign_file_path)
            order_flag = True
        return order_info
    return order_info


def send_order():
    global order_info
    select_symbol(order_info)
    select_indicated_term()


def select_symbol(order):
    global driver
    symbol = order['symbol']
    opener = driver.find_element_by_css_selector("#highlow-asset-filter > span.asset-filter--opener")
    opener.click()
    search_box = driver.find_element_by_id('searchBox')
    search_box.send_keys(symbol)
    time.sleep(5)
    select = driver.find_element_by_css_selector("#assetsFilteredList > div")
    select.click()
    time.sleep(5)


def select_indicated_term():
    global driver, order_info, selected_menu, selected_term
    """
    メインメニューで「High・Low」または「High・Lowスプレッド」が選択されていて、
    なおかつ時間で15分と選択されていた場合、終了時刻の違う３つの選択肢がある。
    order_info変数のtermの項目がShortであれば終了時刻が現在に最も近いものを選択し、
    Middleであれば、真ん中のもの、Longであれば終了時刻が最も遅いものを選択する。
    
    """
    trade_box = []
    trade_info = {}
    if selected_menu == "ChangingStrike" or selected_menu == "FixedPayoutHL":
        if selected_term == "15分":
            # ChangingStrike(High・Low）かFixedPayoutHL（High・Lowスプレッド）の場合で、選択された期間が１５分だった場合、
            # 締め切り時刻別に３つのパネルがあるので、予め指定された期間（短期・中期・長期）に対応して注文を選択する。
            if order_info['term'].strip() == "Short":
                soup = BeautifulSoup(driver.page_source, 'lxml')
                selected_menu_expression = selected_menu + "|" + selected_menu + " selected"
                carousel_items = soup.find_all('div', class_=re.compile(selected_menu_expression))
                for item in carousel_items:
                    trade_info['id'] = item.attrs['id']
                    trade_info['expire_time'] = item.find('span', class_='time-digits').string
                    trade_info['duration'] = item.find('span', class_="duration").string
                    trade_info['order_no'] = item.attrs['order']
                    trade_box.append(trade_info)
            elif order_info['term'].strip() == 'Middle':
                soup = BeautifulSoup(driver.page_source, 'lxml')
                selected_menu_expression = selected_menu + "|" + selected_menu + " selected"
                carousel_items = soup.find_all('div', class_=re.compile(selected_menu_expression), id=re.compile("\\d{4}"))
                for item in carousel_items:
                    trade_info['id'] = item.attrs['id']
                    trade_info['expire_time'] = item.find('span', class_='time-digits').string
                    trade_info['duration'] = item.find('span', class_="duration").string
                    trade_info['order_no'] = item.attrs['order']
                    trade_box.append(trade_info)
            elif order_info['term'].strip() == 'Long':
                soup = BeautifulSoup(driver.page_source, 'lxml')
                selected_menu_expression = selected_menu + "|" + selected_menu + " selected"
                carousel_items = soup.find_all('div', class_=re.compile(selected_menu_expression))
                for item in carousel_items:
                    trade_info['id'] = item.attrs['id']
                    trade_info['expire_time'] = item.find('span', class_='time-digits').string
                    trade_info['duration'] = item.find('span', class_="duration").string
                    trade_info['order_no'] = item.attrs['order']
                    trade_box.append(trade_info)
        else:
            soup = BeautifulSoup(driver.page_source, 'lxml')
            selected_menu_expression = selected_menu + "|" + selected_menu + " selected"
            carousel_items = soup.find_all('div', class_=re.compile(selected_menu_expression))
            for item in carousel_items:
                trade_info['id'] = item.attrs['id']
                trade_info['expire_time'] = item.find('span', class_='time-digits').string
                trade_info['duration'] = item.find('span', class_="duration").string
                trade_info['order_no'] = item.attrs['order']
                trade_box.append(trade_info)
    else:
        soup = BeautifulSoup(driver.page_source, 'lxml')
        selected_menu_expression = selected_menu + "|" + selected_menu + " selected"
        carousel_items = soup.find_all('div', class_=re.compile(selected_menu_expression))
        for item in carousel_items:
            trade_info['id'] = item.attrs['id']
            trade_info['expire_time'] = item.find('span', class_='time-digits').string
            trade_info['duration'] = item.find('span', class_="duration").string
            trade_info['order_no'] = item.attrs['order']
            trade_box.append(trade_info)


def terminate_webdriver():
    global driver
    driver.close()
    driver.quit()