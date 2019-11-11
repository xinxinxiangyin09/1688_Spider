# coding=utf-8

'''
########################### 翻译 ###########################
###### 将中文翻译成泰文使用ch_th , 将泰文翻译成中文使用th_ch ######
###########################################################

########################### 说明 ###########################
###### 使用mysql存储翻译原句和译句，减轻带宽压力，提升响应速度 ######
###########################################################

来吧，在这里记录一下你看到这里的感受
2019.11.4 我写的，其实可以优化，懒得优化了
'''

import http.client
import hashlib
import urllib
import random
import json
import pymysql
from configparser import ConfigParser
import os

class Tran(object):
    def __init__(self):
        config_name = os.path.join(os.path.dirname(__file__), 'config.ini')
        config = ConfigParser()
        config.readfp(open(config_name))
        host, user, password, database, port = config.get('MYSQL', 'host'), config.get('MYSQL', 'user'), config.get('MYSQL', 'password'), config.get('MYSQL', 'database'), config.get('MYSQL', 'port'),
        self.db = pymysql.connect(host=host, user=user, password=password, database=database, port=int(port), charset='utf8mb4')
        self.cursor = self.db.cursor()

    # 泰文翻译成中文
    def th_ch(self, q):
        def start(q):
            appid = '20191024000344139'  # 填写你的appid
            secretKey = 'L1QoI9n_e6_PeumRzNzP'  # 填写你的密钥

            httpClient = None
            myurl = '/api/trans/vip/translate'

            fromLang = 'th'   #原文语种
            toLang = 'zh'   #译文语种
            salt = random.randint(32768, 65536)
            sign = appid + q + str(salt) + secretKey
            sign = hashlib.md5(sign.encode()).hexdigest()
            myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
            salt) + '&sign=' + sign

            try:
                httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
                httpClient.request('GET', myurl)

                # response是HTTPResponse对象
                response = httpClient.getresponse()
                result_all = response.read().decode("utf-8")
                result = json.loads(result_all)

                return str(result['trans_result'][0]['dst']).replace('。','')

            except Exception as e:
                print (e)
            finally:
                if httpClient:
                    httpClient.close()

        # 判断要不要网络翻译, 每调用一次网络翻译就往数据库里添加一次
        sel = "select ch from translate where th = '%s';" % q
        self.cursor.execute(sel)
        result = self.cursor.fetchall()
        if result:
            content =  result[0][0]
        else:
            content = start(q)
            ins = "insert into translate(ch, th) values('%s', '%s');" % (content, q)
            self.cursor.execute(ins)
            self.db.commit()

        # 日志记录
        # previous_path = os.path.abspath(os.path.join(os.getcwd(), '..')) # 上一级路径
        # log_name = os.path.join(previous_path, 'log/tran.log') # 日志路径

        # 不好用，直接用绝对路径，出问题直接
        log_name = '/root/PiFaWang/log/tran.log'
        with open(log_name, 'a+') as f:
            log = 'ch:{} th:{}\n'.format(content, q)
            f.write(log)

        return content

    # 中文翻译成泰文
    def ch_th(self, q):
        def start(q):
            appid = '20191024000344139'  # 填写你的appid
            secretKey = 'L1QoI9n_e6_PeumRzNzP'  # 填写你的密钥

            httpClient = None
            myurl = '/api/trans/vip/translate'

            fromLang = 'zh'  # 原文语种
            toLang = 'th'  # 译文语种
            salt = random.randint(32768, 65536)
            sign = appid + q + str(salt) + secretKey
            sign = hashlib.md5(sign.encode()).hexdigest()
            myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(
                q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
                salt) + '&sign=' + sign

            try:
                httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
                httpClient.request('GET', myurl)

                # response是HTTPResponse对象
                response = httpClient.getresponse()
                result_all = response.read().decode("utf-8")
                result = json.loads(result_all)

                return str(result['trans_result'][0]['dst']).replace('。', '')

            except Exception as e:
                print(e, '翻译报错')
            finally:
                if httpClient:
                    httpClient.close()

        # 判断是否调用网络翻译
        # 判断要不要网络翻译, 每调用一次网络翻译就往数据库里添加一次
        sel = "select th from translate where ch = '%s';" % q
        self.cursor.execute(sel)
        result = self.cursor.fetchall()
        if result:
            content =  result[0][0]
        else:
            content = start(q)
            ins = "insert into translate(ch, th) values('%s', '%s');" % (q, content)
            self.cursor.execute(ins)
            self.db.commit()

        # 日志记录
        previous_path = os.path.abspath(os.path.join(os.getcwd(), '..')) # 上一级路径
        # log_name = os.path.join(previous_path, 'log/tran.log') # 日志路径
        log_name = '/root/PiFaWang/log/tran.log'
        with open(log_name, 'a+') as f:
            log = 'ch:{} th:{}\n'.format(q, content)
            f.write(log)

        return content

    def __del__(self):
        self.cursor.close()
        self.db.close()

# if __name__ == '__main__':
#     tran = Tran()
#     result = tran.th_ch('ฉันรักคุณ')
#     print(result)