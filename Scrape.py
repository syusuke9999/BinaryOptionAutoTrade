from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support import expected_conditions as ec, expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import Parameter
import re
import os
import time
import datetime
import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.withdraw()

selected_menu = ""
selected_duration = ""
Sign_file_path = ""
username = ""
password = ""

order_flag = False
order_info = {}

options = ChromeOptions()
driver = webdriver.Chrome(executable_path='c:\\chromedriver_win32\\chromedriver.exe', options=options)


def get_selected_menu_and_duration():
    """
    ブラウザー上で選択されているメインの取引方法と、各取引時間を調べる。
    :return:
        selected_menu:
            選択されているメインの取引方法
        selected_duration:
            選択されている期間
    """
    global driver, selected_menu, selected_duration
    soup = BeautifulSoup(driver.page_source, "lxml")
    game_tab = soup.select_one('#assetsGameTypeZoneRegion')
    selected = game_tab.find_all("li", attrs={"class": "gameTab selected"})
    selected_menu = selected[0].contents[1].attrs['id']
    term = soup.select_one("#assetsCategoryFilterZoneRegion > div > div.tab.selected")
    selected_duration = term.contents[1].text
    return selected_menu, selected_duration


def transit_to_login_page():
    """
    ログイン画面へ遷移する
    :return:
        boolean: 遷移に成功したらTrue、失敗したらFalseを返す。
    """
    global driver, Sign_file_path, username, password
    # 設定ファイルを読み込んで、シグナルファイルのパスと、ユーザー名、パスワードを読み取り、変数に代入する
    reader = open("setting.txt", "r", encoding='utf-8')
    Sign_file_path = reader.readline()
    # 改行文字を取り除く
    Sign_file_path = Sign_file_path.strip()
    username = reader.readline()
    password = reader.readline()
    # トップページを表示
    driver.get(Parameter.trade_page_url)
    WebDriverWait(driver, 60).until(expected_conditions.url_contains(Parameter.trade_page_url))
    # JavaScriptの実行でログインページへ遷移
    driver.execute_script(Parameter.script_to_transition_login_page)
    WebDriverWait(driver, 60).until(expected_conditions.url_contains(Parameter.login_page_url))
    while driver.current_url != Parameter.login_page_url:
        time.sleep(5)
        link_button_to_login_page = driver.find_element_by_css_selector(Parameter.login_page_url)
        link_button_to_login_page.click()
    if driver.current_url == Parameter.login_page_url:
        return True
    else:
        return False


def login_to_member_page():
    global driver, Sign_file_path, username, password
    """
    Returns:
        bool:
            Represent Log-in procedure is succeeded or failed.
            True: Log-in procedure is succeeded.
            False: Log-in procedure is failed because of some reason.
    """
    user_name = driver.find_element_by_id(Parameter.element_id_of_user_name)
    user_name.send_keys(username.strip())
    pass_word = driver.find_element_by_id(Parameter.element_id_of_password)
    pass_word.send_keys(password.strip())
    try_count = 0
    driver.implicitly_wait(10)
    # ログインボタンをクリック
    login_button = driver.find_element_by_css_selector(Parameter.element_css_selector_of_login_button)
    login_button.click()
    time.sleep(5)
    while driver.current_url != Parameter.trade_page_url or \
            driver.current_url != "https://highlow.com/my-account/dashboard":
        soup = BeautifulSoup(driver.page_source, "lxml")
        tradepage_button_soup = soup.select_one(Parameter.element_css_selector_of_tradepage_button)
        if tradepage_button_soup is None:
            time.sleep(3)
            try_count += 1
            if try_count > 10:
                messagebox.showerror("ログインエラー", "ログインボタンをクリックすることが出来ません。プログラムを終了します。")
        else:
            tradepage_button = driver.find_element_by_css_selector(Parameter.element_css_selector_of_tradepage_button)
            tradepage_button.click()
            break
        soup = BeautifulSoup(driver.page_source, "lxml")
        form_message_content = soup.select_one(Parameter.element_css_selector_error_message)
        if form_message_content is not None:
            if form_message_content.text.strip() == 'ユーザー名またはパスワードが無効です。':
                messagebox.showerror("ログインエラー", "ブラウザー上でユーザー名またはパスワードが無効との表示がありました。"
                                                "ユーザー名やパスワードが正しく設定ファイルに記載されている事を確認して下さい。"
                                                "プログラムを終了します。")
                terminate_webdriver()
                return False
    source_soup = BeautifulSoup(driver.page_source, "lxml")
    logged_in = source_soup.select("Logout")
    if logged_in is not None:
        return True
    else:
        print("ログイン出来ませんでした")
        return False


def wait_signal():
    global order_info, order_flag
    print("MT4のEAがシグナルファイルを生成するのを待っています。")
    while order_flag is False:
        order_info, order_flag = detect_signal()
    if order_flag:
        send_order()
        order_flag = False
        wait_signal()


def detect_signal():
    """
    指定されたフォルダ内のorder.txtファイルを監視して、オーダーが出力されたら内容を読み込み、返り値として返す。
    Returns
    -------発注情報が格納された辞書型オブジェクト
    order_info :
    項目：
        sign:HighまたはLow
        term：メインメニューで選択された取引手法がHighLow・HighLowスプレッドだった場合の、短期・中期・長期の指定
        amount:発注する金額
    """
    global order_flag, Sign_file_path
    order_flag = False
    if os.path.exists(Sign_file_path):
        time.sleep(1)
        # MT4が出力するシグナルファイルが存在するか調べて存在する場合は、
        # その内容を辞書型オブジェクトに格納し、order_flagをTrueにして、シグナルファイルを削除する。
        reader = open(Sign_file_path, "r")
        order_info['symbol'] = reader.readline()
        if "/" not in order_info['symbol']:
            symbol = order_info['symbol'][0:3] + "/" + order_info['symbol'][3:6]
            order_info['symbol'] = symbol
        order_info['sign'] = reader.readline()
        order_info['term'] = reader.readline()
        order_info['amount'] = reader.readline()
        reader.close()
        order_flag = True
        print("symbol=" + order_info['symbol'] + "sign=" +
              order_info['sign'] + "term=" + order_info['term'], " Amount=" + order_info['amount'])
        while os.path.exists(Sign_file_path):
            os.remove(Sign_file_path)
        return order_info, order_flag
    return order_info, order_flag


def send_order():
    """
    グローバル変数（辞書型）であるorder_infoの内容を元にブラウザーを自動操作して、実際の発注を行う。
    :return:
    """
    global driver, order_info
    select_symbol(order_info)
    trade_data = select_indicated_term()
    WebDriverWait(driver, 10).until(expected_conditions.element_to_be_clickable((
        By.ID, trade_data['id'])))
    trade_box = driver.find_element_by_id(trade_data['id'])
    trade_box.click()
    soup = BeautifulSoup(driver.page_source, "lxml")
    tradebox_soup = soup.find('div', id=trade_data['id'])
    while 'selected' not in tradebox_soup['class']:
        trade_box.click()
        soup = BeautifulSoup(driver.page_source, "lxml")
        tradebox_soup = soup.find('div', id=trade_data['id'])
    if 'selected' in tradebox_soup['class']:
        amount_input = driver.find_element_by_id("amount")
        amount_input.clear()
        amount_input.send_keys(order_info['amount'])
        soup = BeautifulSoup(driver.page_source, "lxml")
        is_read_only = soup.find('input', id='amount', readonly='readonly')
        if is_read_only is None:
            if order_info['sign'].strip() == "HIGH":
                high_button = driver.find_element_by_id("up_button")
                high_button.click()
            elif order_info['sign'].strip() == "LOW":
                low_button = driver.find_element_by_id("down_button")
                low_button.click()
        else:
            messagebox.showerror('発注', "発注締め切り時間後のため、発注出来ません。")
            return False


def select_symbol(order):
    """
    受け取った引数の通貨ペアをハイロードットコムの発注画面で選択する
    :param order:
    発注情報が格納された辞書型オブジェクト
    項目：
        sign:HighまたはLow
        term：メインメニューで選択された取引手法がHighLow・HighLowスプレッドだった場合の、短期・中期・長期の指定
        amount:発注する金額
    :return:
    """
    global driver
    symbol = order['symbol']
    opener = driver.find_element_by_css_selector("#highlow-asset-filter > span.asset-filter--opener")
    opener.click()
    search_box = driver.find_element_by_id('searchBox')
    search_box.send_keys(symbol)
    time.sleep(3)
    select = driver.find_element_by_css_selector("#assetsFilteredList > div")
    select.click()
    time.sleep(1)


def select_indicated_term():
    global driver, order_info, selected_menu, selected_duration
    """
    メインメニューで「High・Low」または「High・Lowスプレッド」が選択されていて、
    なおかつ時間で15分と選択されていた場合、終了時刻の違う３つの選択肢がある。
    order_info変数のtermの項目がShortであれば終了時刻が現在に最も近いものを選択し、
    Middleであれば、真ん中のもの、Longであれば終了時刻が最も遅いものを選択する。
    
    Returns:
        辞書型オブジェクト:
            {"id": "4桁の注文ID", "order_id": "39桁の注文ID"}
    """
    trade_box = []
    trade_info = {}
    trade_data = {}
    long_term_trade_data = {}
    middle_term_trade_data = {}
    short_term_trade_data = {}

    if selected_menu == "ChangingStrike" or selected_menu == "FixedPayoutHL":
        if selected_duration == "15分":
            soup = BeautifulSoup(driver.page_source, 'lxml')
            # メインメニューでChangingStrike(High・Low）かFixedPayoutHL（High・Lowスプレッド）が選択されていて、
            # かつ２番目のメニューで選択された期間が１５分だった場合、締め切り時刻別に３つのパネルがあるので、
            # 予め指定された期間（短期・中期・長期）に対応して注文を選択する。
            selected_menu_expression = selected_menu + "|" + selected_menu + " selected"
            carousel_items = soup.find_all('div', class_=re.compile(selected_menu_expression), id=re.compile("\d{4}"))
            now = datetime.datetime.now()
            today = datetime.date(now.year, now.month, now.day)
            for item in carousel_items:
                id_ = item.attrs['id']
                expire_time = item.find('span', class_='time-digits').string
                # duration = item.find('span', class_="duration").string
                order_no = item.attrs['order']
                trade_box.append({"id": id_, "expire_time": expire_time, "order_no": order_no})
            time_0 = datetime.datetime.strptime(trade_box[0]['expire_time'].encode('utf-8').decode(), '%H:%M')
            time_1 = datetime.datetime.strptime(trade_box[1]['expire_time'].encode('utf-8').decode(), '%H:%M')
            time_2 = datetime.datetime.strptime(trade_box[2]['expire_time'].encode('utf-8').decode(), '%H:%M')
            datetime_0 = datetime.datetime(year=today.year, month=today.month, day=today.day, hour=time_0.hour,
                                           minute=time_0.minute, second=0)
            datetime_1 = datetime.datetime(year=today.year, month=today.month, day=today.day, hour=time_1.hour,
                                           minute=time_1.minute, second=0)
            datetime_2 = datetime.datetime(year=today.year, month=today.month, day=today.day, hour=time_2.hour,
                                           minute=time_2.minute, second=0)
            if datetime_0 < datetime_1:
                if datetime_2 < datetime_0:
                    short_term_trade_data = trade_box[2]
                    middle_term_trade_data = trade_box[0]
                    long_term_trade_data = trade_box[1]
                elif datetime_1 < datetime_2:
                    short_term_trade_data = trade_box[0]
                    middle_term_trade_data = trade_box[1]
                    long_term_trade_data = trade_box[2]
            else:
                if datetime_2 > datetime_0:
                    short_term_trade_data = trade_box[1]
                    middle_term_trade_data = trade_box[0]
                    long_term_trade_data = trade_box[2]
                elif datetime_1 < datetime_2:
                    short_term_trade_data = trade_box[1]
                    middle_term_trade_data = trade_box[2]
                    long_term_trade_data = trade_box[0]
            if order_info['term'].strip() == "Short":
                trade_data = {"id": short_term_trade_data['id'], "order_no": short_term_trade_data['order_no']}
            elif order_info['term'].strip() == "Middle":
                trade_data = {"id": middle_term_trade_data['id'], "order_no": middle_term_trade_data['order_no']}
            elif order_info['term'].strip() == "Long":
                trade_data = {"id": long_term_trade_data['id'], "order_no": long_term_trade_data['order']}
            return trade_data
        else:
            # HighLowまたは、HighLowスプレッドで、１５分以外が選択されていた場合
            soup = BeautifulSoup(driver.page_source, 'lxml')
            selected_menu_expression = "carousel_item " + selected_menu + " selected"
            carousel_items = soup.find_all('div', class_=re.compile(selected_menu_expression), id=re.compile("\d{4}"))
            trade_info['id'] = carousel_items[0].attrs['id']
            trade_info['order_no'] = carousel_items[0].attrs['order']
            trade_data = {"id": trade_info['id'], 'order_no': trade_info['order_no']}
            return trade_data
    else:
        # メインメニューでTurboまたはTurboスプレッドが選択されていた場合
        soup = BeautifulSoup(driver.page_source, 'lxml')
        selected_menu_expression = "carousel_item " + selected_menu + " selected"
        carousel_items = soup.find_all('div', class_=selected_menu_expression, id=re.compile("\d{4}"))
        trade_info['id'] = carousel_items[0].attrs['id']
        trade_info['order_no'] = carousel_items[0].attrs['order']
        trade_data = {"id": trade_info['id'], 'order_no': trade_info['order_no']}
    return trade_data


def set_oneclick_trade():
    """
    ワンクリックトレードをONにする
    """
    global driver
    oneclick_trade = driver.find_element_by_css_selector(
        "#strikeAreaRegion > div > div.chartTimeArea.pull-right.last-child > a")
    oneclick_trade.click()
    WebDriverWait(driver, 60).until(ec.presence_of_all_elements_located)


def terminate_webdriver():
    global driver
    driver.close()
    driver.quit()
