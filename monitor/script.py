import pymysql
import re
from collections import Counter # 科学计算
import os
import shutil # 备份日志
from datetime import datetime

'''
爬虫日报
'''

# 日报
class BaoGao(object):
    def __init__(self):
        self.db = pymysql.connect(host='118.31.102.84', user='root', password='Asd.1234', port=3306, database='spider')
        self.cursor = self.db.cursor()

        self.base_file = os.path.join(os.getcwd(), '..')

        print('数据库已连接')

    # 日志备份
    def back_log(self):
        filename = os.path.join(self.base_file, '/back')
        filename = os.path.join(filename, datetime.now().strftime("%Y-%m-%d"))
        if not os.path.exists(filename):
            os.makedirs(filename)
        try:
            shutil.copyfile(os.path.join(self.base_file, 'log/detail.log'), os.path.join(filename, 'detail.log'))
            shutil.copyfile(os.path.join(self.base_file, 'log/pro.log'), os.path.join(filename, 'pro.log'))
            shutil.copyfile(os.path.join(self.base_file, 'log/spider.log'), os.path.join(filename, 'spider.log'))
            shutil.copyfile(os.path.join(self.base_file, 'log/tran.log'), os.path.join(filename, 'tran.log'))
            return 'OK'
        except Exception:
            return

    # 日志分析
    def analysis(self):

        data = {}

        # 新增ID查询
        sel = 'select count(*) from detail1 where to_days(create_time) = to_days(now());'
        self.cursor.execute(sel)
        count = self.cursor.fetchall()[0][0]
        data['新增ID'] = count

        # IP TOP3榜查询
        detail = open(os.path.join(self.base_file, 'log/detail.log'))
        content = detail.read()
        detail.close()

        ips = re.findall(r'ip:(.*?) \^*\^', content)
        counts = Counter(ips).most_common(3)
        result = {}
        for item in counts:
            result[item[0]] = item[1]
        data['IP频率'] = result


        # ID TOP3 榜
        ids = re.findall(r'.*?id:(.*?) \^*\^', content)
        counts = Counter(ids).most_common(3)
        result = {}
        for item in counts:
            result[item[0]] = item[1]
        data['ID频率'] = result

        # 重启次数
        pro = open(os.path.join(self.base_file, 'log/pro.log'))
        content = pro.read()
        pro.close()
        reset = re.findall('Press CTRL\+C to quit', content)
        data['爬虫重启次数'] = len(reset)

        # 报错次数
        error = re.findall('调用了本地数据', content)
        data['爬虫搜索报错次数'] = len(error)

        # 热搜TOP榜
        spider = open(os.path.join(self.base_file, 'log/spider.log'))
        content = spider.read().replace('"', '')
        content.replace('“', '')
        content.replace('”', '')
        kw = re.findall(r'KEY:(.*?) \^\*\^', content)
        count = Counter(kw).most_common(3)
        result = {}
        for item in count:
            result[item[0]] = item[1]
        data['今日热搜'] = result

        # 翻译TOP3榜
        tran = open(os.path.join(self.base_file, 'log/tran.log'), encoding='utf-8')
        content = tran.read()
        tran.close()

        ths = re.findall('th:(.*?)\n', content)
        chs = re.findall('ch:(.*?) ', content)

        statistics = {}
        for i in range(len(ths)):
            statistics[ths[i]] = chs[i]

        # 最终返回的报告内容
        count = Counter(ths).most_common(3)
        content = []
        for i in count:
            content.append({'th':i[0], 'ch':statistics[i[0]], 'count':i[1]})

        data['翻译频率'] = content

        return data

    # 重启爬虫
    def reset(self):
        pass

    def main(self):
        result = self.back_log()
        if result == 'OK':
            print('日志已备份')
            return self.analysis()
        else:
            print('日志备份错误')

    def __del__(self):
        self.cursor.close()
        self.db.close()
        print('数据库已断开')

# 重启脚本
class ReSet(object):
    filename = '/root/PiFaWang/web.py'
    result = os.popen('')

if __name__ == '__main__':
    report = BaoGao()
    result = report.main()
    print(result)
    # os.popen('rm -rf /root/PiFaWang/log/*') # 删除日志文件