from selenium import webdriver

class GetPic(object):
    def __init__(self):
        self.browser = webdriver.PhantomJS()

    def get_html(self, url):
        self.browser.get(url)
        html = self.browser.page_source
        print(html)

    def __del__(self):
        self.browser.close()

if __name__ == '__main__':
    get_pic = GetPic()
    url = 'https://desc.alicdn.com/i2/581/780/589787026171/TB1z2LnNkvoK1RjSZPf8qtPKFla.desc%7Cvar%5Edesc%3Blang%5Egbk%3Bsign%5E77725c365f24eb583d03349ee5d6befa%3Bt%5E1571371227'
    get_pic.get_html(url)
