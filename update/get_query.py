from selenium import webdriver
import requests
import os

'''
更新浏览器的登陆参数
'''

class UpDate(object):
    def __init__(self):
        self.browser = webdriver.PhantomJS()
        self.login_pic = ('/root/PiFaWang/html/image/demo.png')

    def login(self):
        self.browser.get('https://login.1688.com/member/signin.htm?tracelog=member_signout_signin')
        self.browser.maximize_window()
        self.browser.find_element_by_xpath('//*[@id="J_QRCodeImg"]/img/@src') # 登陆二维码
        self.browser.save_screenshot(self.login_pic)

        # 进入阻塞，等待扫码登陆
        while True:
            try:
                self.browser.find_element_by_xpath('//*[@id="J_QRCodeLogin"]/div[3]/div[1]/div[3]/a').click() # 尝试点击刷新按钮
                break
            except Exception as err:
                print(err)
                continue

        self.browser.close()

if __name__ == '__main__':
    login = UpDate()
    login.login()