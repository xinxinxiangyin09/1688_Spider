from configparser import ConfigParser
import os
import pymysql
import json
import random

from tools.parse import *

'''
详情页的提取关键字 
'''

class DetailsSpider(object):
    def __init__(self):
        config = ConfigParser()
        filename = os.path.join(os.path.dirname(__file__), 'config.ini')
        config.readfp(open(filename))

        self.username = config.get('USER', 'username')
        self.TPL_password_2 = config.get('USER', 'TPL_password_2')
        self.ua = config.get('USER', 'ua')

        self.url = 'https://detail.1688.com/offer/{}.html'

        # host, user, password, database, port = config.get('MYSQL', 'host'), config.get('MYSQL', 'user'), config.get('MYSQL', 'password'), config.get('MYSQL', 'database'), config.get('MYSQL', 'port'),

        # 数据库
        self.db = pymysql.connect(host='localhost', user='root', password='0', database='spider', port=3306, charset='utf8mb4')
        self.cursor = self.db.cursor()

        # 日志文件

    # 获取源码
    def get_html(self, url):

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
            'cache-control': 'max-age=0',
            'cookie': 'hng=CN%7Czh-CN%7CCNY%7C156; cna=RY4bFQvik3QCAXkgIDM5ce14; ali_ab=119.130.214.179.1571810964934.5; UM_distinctid=16dfbd9545d2a0-0b17a5da2395a1-b363e65-1fa400-16dfbd9545e931; taklid=23aa31a6247c48f1aed0776e51220914; lid=xinxinxiangyin0923; ali_apache_track=c_mid=b2b-1754602771|c_lid=xinxinxiangyin0923|c_ms=1; CNZZDATA1261052687=471186303-1571994272-%7C1572070012; cookie2=1c4e086c05206f501afcbe98ea5a0311; t=e1298dd8aa1bcd1cdb98b91d47ab6bda; _tb_token_=538ae8e66e3e; ali_apache_tracktmp=c_w_signed=Y; last_mid=b2b-1754602771; __cn_logon__=true; __cn_logon_id__=xinxinxiangyin0923; _csrf_token=1573177329190; csg=fe1dff8b; uc4=nk4=0%40GToZeNIMSK0x89tFcHTjfdHpldP8ACV0D%2F6WL4U%3D&id4=0%40UO6SFJIuOtvcdrvh%2F7ns3XKgln4f; h_keys="%u5973%u88c5#%u80cc%u5fc3%u540a%u5e26#%u84dd%u7259#%u5185%u8863%u5973#%u65e0%u7ebf%u5145#%u8033%u673a#%u624b%u673a%u58f3#%u684c%u5e03#%u60c5%u8da3%u5185%u8863"; ad_prefer="2019/11/08 10:35:43"; alicnweb=touch_tb_at%3D1573193218593%7Clastlogonid%3Dxinxinxiangyin0923; CNZZDATA1253659577=128205233-1568301296-https%253A%252F%252Fwww.1688.com%252F%7C1573192080; JSESSIONID=B3B96F8BFED8B000CE05032E792FB4D8; l=dBE6RRGVqc3foMZDBOCZhurza779HIRAguPzaNbMi_5CtTL_-Z_OkQ9Pfnp6cjWfGsLp4ysIWiy9-etkjNsZ2izxkcBcnxDc.; isg=BLKy83TMOwgLkweLzvltV4yMA_hU67en6Je9kHyLrGVQD1IJZdNp7XVl_-sWfy51',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
        }

        # 计算请求参数spm的值
        spm = 'b26110380.sw1688.mof001.{}.422f5285cDLDG3'.format(random.randint(10, 99))
        # spm = 'b26110380.sw1688.mof001.1.422f5285cDLDG3'

        data1 = {
            'TPL_username': self.username,
            'TPL_password': '',
            'ncoToken': 'a98e8fb62aba545ed63cd01158c7ed5c0ef785a7',
            'slideCodeShow': 'false',
            'useMobile': 'false',
            'lang': 'zh_CN',
            'loginsite': '0',
            'newlogin': '0',
            'from': 'tb',
            'fc': 'default',
            'style': 'default',
            'keyLogin': 'false',
            'qrLogin': 'true',
            'newMini': 'false',
            'newMini2': 'false',
            'loginType': '3',
            'TPL_password_2': self.TPL_password_2,
            'loginASR': '1',
            'loginASRSuc': '1',
            'oslanguage': 'zh-CN',
            'sr': '1920*1080',
            'naviVer': 'chrome|77.0386512',
            'osACN': 'Mozilla',
            'osAV': '5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
            'osPF': 'Win32',
            'appkey': '00000000',
            'nickLoginLink': '',
            'showAssistantLink': '',
            'um_token': 'TC01F4982C8A68707B7176F44EF7BE14B016D2C83E03AE38E5BC0D89E34',
            'ua': self.ua
        }

        data2 = {'spm': spm}

        while True:
            print("正在请求二级页面")
            response = requests.get(url=url, headers=headers, params=data1)
            if response.status_code == 200:
                html = response.text
                print("获取源码：\033[32mOK\033[0m")
                return html
            else:
                print('请求失败，正在重新请求。。。')
                continue

    # 解析网页
    def parse_html(self, url, id):
        html = self.get_html(url)

        # print(html)

        if '<span class="sub-logo">登录</span>' in html:
            print('登陆过期，重新配置config.ini')
            return '登陆过期', id
        # print(html)

        elif 'Error 404' in html:
            print('页面未找到', id)
            return '页面未找到', id

        title = get_shop_title_two(html) # 商品名称 （固定）
        spics = get_shop_spic_two(html)  # 宣传栏图片 （固定）
        # pics = get_detail_pic(html)# 详细图片 （固定）

        try:
            prices = get_price(html) # 两种提取规则， 1、起批量 2、范围价格
            types = get_types(html) # 提取类型信息


            print("解析源码：\033[32mOK\033[0m")

            # print('名称', title)
            # print('价格：', len(prices), prices)
            # print('类型：', len(types), types)
            # print('展示栏图片', len(spics), spics)
            # print('详细图片', len(pics), pics)

            # 数据整合
            d = {}
            d['title'], d['price'], d['type'], d['display_img'],  = title, prices, types, spics,
            # d['detail_img'] = pics
            html = json.dumps(d, ensure_ascii=False)

            # 数据入库
            result = self.write(html, id)
            if result == "OK":
                return html

            # 日志文件，该项日志在web.py中写

            return html

        except IndexError: # 如果代码运行到这里则源码没有json数据,这里单独处理
            title = re.findall('<h1 class="d-title">(.*?)</h1>', html)[0]
            price = re.findall("data-range='(.*?)'", html)
            stock = re.findall('<span class="total">(.*?)</span>', html)[0]
            display_img = re.findall('<img src="(.*?).60x60.jpg"', html)
            '''
            print(title)
            print(type(price),price)
            print(stock)
            print(display_img)
            '''

            data = {}
            data['title'] = title
            # 价格整合
            # {'type':1, 'price':[[1999, 3.00], []]}
            prices = []
            for item in price:
                item = eval(item)
                # [[1999, 3.00], []]
                prices.append([item['begin'], float(item['price'])])

            stock = re.findall('(\d+)', stock) # 库存清洗

            data['price'] = {'type':1, 'price': prices}
            data['type'] = [{'title':'', 'specifications':[{'name':'', 'stock':stock, 'price':prices[0][1]}], 'url':''}]

            # 展示栏图片整合
            display_imgs = []
            for item in display_img:
                display_imgs.append(item+'.jpg')

            data['display_img'] = display_imgs

            html = json.dumps(data, ensure_ascii=False)
            # 数据入库
            result = self.write(html, id)
            if result == "OK":
                return html
            return html

    # 写入数据库
    def write(self, html, id):
        # t = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        # html = html.replace('"', '/"')

        sql = "INSERT INTO detail1 (content, keyword) VALUES ('%s', %s);" % (html, id)
        try:
            self.cursor.execute(sql)
            self.db.commit()
            print("数据库保存成功")
            return "OK"

        except Exception:
            print('数据库已存在')

    def main(self, id):
        url = self.url.format(id)
        return self.parse_html(url, id)

    def __del__(self):
        self.cursor.close()
        self.db.close()
#
# if __name__ == '__main__':
#     spider = DetailsSpider()
#     result = spider.main('594538886502')
#     print(result)