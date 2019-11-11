from configparser import ConfigParser
import os

from tools.parse import *
from tools.trans import Tran # 翻译
from URL.get_url import GetUrl # 构造URL

'''
获取搜索链接的商品信息
'''

class ALiSpider(object):
    def __init__(self):
        # URL变更三个参数 keywords {} beginPage {} startIndex {} requestId {}
        self.first_url = 'https://s.1688.com/selloffer/rpc_async_render.jsonp?keywords={}&descendOrder=true&n=y&netType=1%2C11&qrwRedirectEnabled=false&sortType=va_rmdarkgmv30rt&uniqfield=userid&beginPage={}&templateConfigName=marketOfferresult&offset=0&pageSize=60&asyncCount=20&startIndex={}&async=true&enableAsync=true&rpcflag=new&_pageName_=market&requestId={}&callback=jQuery17204997447339086898_1573179428701'
        # URL变更三个参数 keywords {} beginPage {} requestId{} startIndex {} requestId {}
        self.end_url = 'https://s.1688.com/selloffer/rpc_async_render.jsonp?keywords={}&descendOrder=true&n=y&netType=1%2C11&qrwRedirectEnabled=false&sortType=va_rmdarkgmv30rt&uniqfield=userid&beginPage={}&requestId={}&templateConfigName=marketOfferresult&offset=0&pageSize=60&asyncCount=20&startIndex={}&async=true&enableAsync=true&rpcflag=new&_pageName_=market&requestId={}&callback=jQuery17204997447339086898_1573179428701'
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
            'cache-control': 'max-age=0',
            'cookie': '__sw_newuno_count__=1; __sw_ktsz_count__=1; hng=CN%7Czh-CN%7CCNY%7C156; cna=RY4bFQvik3QCAXkgIDM5ce14; alisw=swIs1200%3D1%7C; ali_ab=119.130.214.179.1571810964934.5; _bl_uid=9wkpp2d62F8veFo7F0t8vdgm9Cbv; UM_distinctid=16dfbd9545d2a0-0b17a5da2395a1-b363e65-1fa400-16dfbd9545e931; taklid=23aa31a6247c48f1aed0776e51220914; lid=xinxinxiangyin0923; ali_apache_track=c_mid=b2b-1754602771|c_lid=xinxinxiangyin0923|c_ms=1; cookie2=1c4e086c05206f501afcbe98ea5a0311; t=e1298dd8aa1bcd1cdb98b91d47ab6bda; _tb_token_=538ae8e66e3e; ali_apache_tracktmp=c_w_signed=Y; last_mid=b2b-1754602771; cookie1=W5xgUu285bGi961T7mIF8vzT6AXoEkZZCwXbCiWHquM%3D; cookie17=UoYbz91WGwwbIw%3D%3D; sg=31d; unb=1754602771; __cn_logon__=true; __cn_logon_id__=xinxinxiangyin0923; _nk_=xinxinxiangyin0923; _csrf_token=1573177329190; _is_show_loginId_change_block_=b2b-1754602771_false; _show_force_unbind_div_=b2b-1754602771_false; _show_sys_unbind_div_=b2b-1754602771_false; _show_user_unbind_div_=b2b-1754602771_false; __rn_alert__=false; alicnweb=touch_tb_at%3D1573177815601%7Clastlogonid%3Dxinxinxiangyin0923; isg=BKOjjEkh-k6xcbbEpzKMMGW3MueNMDagcfxsn9UAioIiFMM2XWsKKtRODqS_tI_S; l=dBE6RRGVqc3fo1WLBOCwhurza77tMIRAguPzaNbMi_5CTTvI-pQOkQHRDnv6cjWfGT8B4ysIWiy9-etktEM-o8zJIACVNxDc.; csg=fe1dff8b; uc4=nk4=0%40GToZeNIMSK0x89tFcHTjfdHpldP8ACV0D%2F6WL4U%3D&id4=0%40UO6SFJIuOtvcdrvh%2F7ns3XKgln4f; ad_prefer="2019/11/08 10:25:35"; h_keys="%u80cc%u5fc3%u540a%u5e26#%u5973%u88c5#%u84dd%u7259#%u5185%u8863%u5973#%u65e0%u7ebf%u5145#%u8033%u673a#%u624b%u673a%u58f3#%u684c%u5e03#%u60c5%u8da3%u5185%u8863"',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'
        }

        # 数据库用来存放翻译信息，以备遇到的重复的数据能直接显示
        config = ConfigParser()
        filename = os.path.join(os.path.dirname(__file__), 'config.ini')
        config.readfp(open(filename))

    # 构造URL
    def structure_url(self, keywords, page):
        '''原来构造URL的代码，为确保数据的准确性。使用selenium获取
        if keywords == "女鞋":
            keywords = 'ŮЬ'
        elif keywords == "少女":
            keywords = 'Ůװ'
        elif keywords == "内衣":
            keywords = '%C4%DA%D2%C2'
        else:
            keywords = str(keywords.encode('gb2312'))
            keywords = keywords.replace("b'", '')
            keywords = keywords.replace("'", '')
            keywords = keywords.replace('\\x', '%').upper()
        '''

        get_url = GetUrl()
        keywords = get_url.main(keywords)

        url_list = []

        for startIndex in range(0, 60, 20): # 前20条数据只需要一个requestsid, 后40条数据需要两个
            config = ConfigParser()
            filename = os.path.join(os.path.dirname(__file__), 'config.ini')
            config.readfp(open(filename))
            requestsId = config.get('ID', 'requestId') # 会过期，及时更新， 在config.ini 文件里面
            if startIndex != 40 :
                url = self.first_url.format(keywords, page, startIndex, requestsId)  # 编码
                url_list.append(url)
            else:
                url = self.end_url.format(keywords, page, requestsId, startIndex, requestsId)
                url_list.append(url)
            # print(url_list)

        return url_list

    # 请求次数较多，封装类方法
    def get_html(self, url):
        return requests.get(url=url, headers=self.headers).text

    # 提取一级页面图片
    def extract_img_one(self, html):
        img = get_shop_img(html)
        return img

    # 提取一级页面标题
    def extract_title_one(self, html):
        title = get_shop_title(html)
        return title

    # 提取一级页面价格
    def extract_price_one(self, html):
        price = get_shop_price(html)
        return price

    # 提取一级页面商品ID，构造二级页面的URL
    def extract_ids_one(self, html):
        ids = get_shop_id(html)
        return ids

    def main(self, keywords, page):
        url_list = self.structure_url(keywords, page)
        print('构造URL：\033[32mOK\033[0m')

        # print('三次请求的URL', url_list)

        titles = []
        prices = []
        imgs = []
        two_urls = []
        ids = []

        for url in url_list:
            html = self.get_html(url)
            print('获取一级页面源码：\033[32mOK\033[0m')
            # 提取封面图片
            img = self.extract_img_one(html)
            imgs.extend(img)

            # 提取封面标题
            title = self.extract_title_one(html)
            titles.extend(title)

            # 提取封面价格
            price = self.extract_price_one(html)
            prices.extend(price)

            # 提取商品ID
            id = self.extract_ids_one(html)
            ids.extend(id)

            # 二级页面的URL拼接
            for item in id:
                two_url = 'https://detail.1688.com/offer/%s.html'%str(item)
                two_urls.append(two_url)

        # shops 商品列表整合
        print('翻译中...')
        # 翻译
        i = 0
        for item in titles:
            tran = Tran()
            titles[i] = tran.ch_th(item)
            i += 1

        print('翻译：\033[32mOK\033[0m')

        shops = []

        '''
        print('titles',len(titles), titles)
        print('prices',len(prices), prices)
        print('img', len(imgs), imgs)
        print('url', len(two_urls), two_urls)
        print('id', len(ids), ids)
        '''

        for i in range(60):
            shop = {"title":titles[i], "price":prices[i], "img":imgs[i], "url":two_urls[i], "id":ids[i]}
            shops.append(shop)

        html = str(shops).replace("'", '"')

        return html

# 测试
# if __name__ == '__main__':
#     spider = ALiSpider()
#     result = spider.main('背心吊带', 1)
#     print(result)