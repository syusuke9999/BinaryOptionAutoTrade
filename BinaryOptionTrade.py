import tkinter as tk
from tkinter import messagebox
import Parameter
import Scrape

root = tk.Tk()
root.withdraw()


def main():
    login()
    condition_ok = False
    while condition_ok is False:
        messagebox.showwarning("注意", "必ずメインのメニューから取引する項目を"
                                     "「HighLow・HighLowスプレッド・Turbo・Turboスプレッド」"
                                     "のいずれかから選択しておいて下さい。")
        selected_menu, selected_term = Scrape.get_selected_menu_and_term()
        print("selected_menu=" + selected_menu + "    selected_term=" + selected_term)
        if selected_term is not "全て":
            condition_ok = True
            Scrape.wait_signal()
        else:
            continue


def login():
    if Scrape.transit_to_login_page():
        print("ログインページに遷移できました")
        if Scrape.login_to_member_page():
            print("ログイン出来ました")


if __name__ == '__main__':
    main()