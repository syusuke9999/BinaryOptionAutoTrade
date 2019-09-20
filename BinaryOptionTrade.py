import tkinter as tk
from tkinter import messagebox
import Scrape

root = tk.Tk()
root.withdraw()


def main():
    login()
    messagebox.showwarning("注意", "必ずメインのメニューから取引する項目を"
                                 "「HighLow・HighLowスプレッド・Turbo・Turboスプレッド」"
                                 "のいずれかから選択しておいて下さい。またメインメニューでいずれを選択した場合でも"
                                 "２段目のメニューで取引時間（間隔）を指定して下さい。")
    condition_ok = False
    while condition_ok is False:
        selected_menu, selected_duration = Scrape.get_selected_menu_and_duration()
        print("selected_menu=" + selected_menu + "    selected_duration=" + selected_duration)
        if selected_duration != "全て":
            Scrape.set_oneclick_trade()
            condition_ok = True
            Scrape.wait_signal()
        else:
            messagebox.showwarning("注意", "取引期間が選択されていません。取引期間を選択してからOKをクリックして下さい。")
            continue


def login():
    if Scrape.transit_to_login_page():
        print("ログインページに遷移できました")
        if Scrape.login_to_member_page():
            print("ログイン出来ました")
            return True
        else:
            print("何らかの理由でログインできませんでした。")
            return False
    else:
        print("何らかの理由でログインできませんでした。")
        return False


if __name__ == '__main__':
    main()
