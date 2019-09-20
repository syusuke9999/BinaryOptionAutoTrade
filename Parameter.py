# パラメーター
trade_page_url = "https://trade.highlow.com/"
login_page_url = "https://highlow.com/login"
script_to_transition_login_page = "goToExternal()"


# DOMパス
element_css_selector_of_login_link = "#header > div > div > div > div > div > span > span > a:nth-child(5)"
element_id_of_user_name = "login-username"
element_id_of_password = "login-password"
element_css_selector_of_login_button = "#signin-popup > div.modal-dialog-wrapper > div > div.modal-dialog >"\
                                       " div.modal-body.grid-bg > form > div > div:nth-child(6) > button"
element_css_selector_of_tradepage_button = "#main-menu > div > ul > li:nth-child(1) > span > a > svg"
element_css_selector_error_message = "#signin-popup > div.modal-dialog-wrapper > div > " \
                                               "div.modal-dialog > div.modal-body.grid-bg > form > " \
                                               "div > div.form-message-error.form-message > span > " \
                                               "span > div.content"
