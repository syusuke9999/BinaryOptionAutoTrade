import tkinter as tk
from tkinter import messagebox
import Scrape

root = tk.Tk()
root.withdraw()


def main():
    login()
    condition_ok = False
    while condition_ok is False:
        messagebox.showwarning("注意", "必ずメインのメニューから取引する項目を"
                                     "「HighLow・HighLowスプレッド・Turbo・Turboスプレッド」"
                                     "のいずれかから選択しておいて下さい。またメインメニューでいずれを選択した場合でも"
                                     "２段目のメニューで取引時間（間隔）を指定して下さい。")
        selected_menu, selected_duration = Scrape.get_selected_menu_and_duration()
        if selected_menu == "ChangingStrike":
            messagebox.showwarning("注意", "メインメニューでHighLowを選択した場合、２段目のメニューで"
                                         "取引時間（間隔）を指定して下さい")
        elif selected_menu == "FixedPayoutHL":
            messagebox.showwarning("注意", "メインメニューでHighLowスプレッドを選択した場合でも、２段目のメニューで"
                                         "取引時間（間隔）を指定して下さい")
        elif selected_menu == "ChangingStrikeOOD":
            messagebox.showwarning("注意", "メインメニューでTurboを選択した場合でも、２段目のメニューで"
                                         "取引時間（間隔）を指定して下さい")
        elif selected_menu == "FixedPayoutHLOOD":
            messagebox.showwarning("注意", "メインメニューでTurboスプレッドを選択した場合でも、２段目のメニューで"
                                         "取引時間（間隔）を指定して下さい")
        print("selected_menu=" + selected_menu + "    selected_duration=" + selected_duration)
        if selected_duration != "全て":
            Scrape.set_oneclick_trade()
            condition_ok = True
            Scrape.wait_signal()
        else:
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
