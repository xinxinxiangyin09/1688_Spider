from selenium import webdriver
import re
import os
import time

'''
获取需要请求的URl，一直有编码问题，如果字段过长的话编码总会出现问题
这里模拟浏览器获取当前的URL
'''

class GetUrl(object):
    def __init__(self):
        service_args = []
        service_args.append('--load-images=no')
        service_args.append('--disk-cache=yes')
        service_args.append('--ignore-ssl-errors=true')
        self.url = 'https://www.1688.com/'
        self.browser = webdriver.PhantomJS(service_args=service_args)

    # 模拟访问以获取准确的URL
    def main(self, keyword):
        self.browser.get(self.url) # 打开首页
        self.browser.set_window_size(1366, 768) # 这里按钮识别会出问题，自定义窗口分辨率
        self.browser.find_element_by_xpath('//*[@id="home-header-searchbox"]').send_keys(keyword) # 输入关键字
        self.browser.find_element_by_xpath('//*[@id="app"]/div/div[3]/section/div[2]/div/div/div/form/fieldset/div/div[2]/button').click() # 点击搜索
        url = self.browser.current_url
        keyword = re.findall(r'\?keywords=(.*?)&', url)[0]
        return keyword

    def __del__(self):
        self.browser.quit()

if __name__ == '__main__':
    get_url = GetUrl()
    result = get_url.main('女装')
    print(result)