from flask import Flask
from flask import request
import datetime
import os

from tools.spider import ALiSpider # 一级页面的爬虫
from tools.detail import DetailsSpider # 二级页面的爬虫
from tools.trans import Tran # 翻译
from tools.db import MySQL # 操作数据库
from langdetect import detect # 语种识别

tran = Tran()
app = Flask(__name__)

@app.errorhandler(404)
def miss(e):
    return "404"

@app.errorhandler(500)
def error(e):
    return "500, 服务器内部错误,请联系管理员"

@app.route('/demo')
def demo():
    return "OK"

@app.route('/index')
def index():
    return '<h3>API说明</h3><p><b>访问搜索接口</b></p><p>http://118.31.102.84:5000/search?kw=搜索关键字&page=页码</p><p><b>进入详情页面</b></p><p>http://118.31.102.84:5000/detail?id=商品ID</p>'

@app.route('/search', methods=['get', 'post'])
def search():
    # 获取通过url请求传参的数据
    keyword = request.values.get('kw')
    page = request.values.get('page')

    if page is None:
        return '缺少page字段<br/>说明：<a href="http://118.31.102.84:5000/index">点击跳转'

    # 识别语种
    if detect(keyword) == 'zh-cn': # 中文
        print("键入了中文，无需翻译", keyword)
    elif detect(keyword) == 'th': # 泰文
        tran = Tran()
        keyword = tran.th_ch(keyword)
        print('键入了泰文，已翻译', keyword)

    try:

        spider = ALiSpider()
        html = spider.main(keyword, int(page))

        # 日志文件
        log_filename = os.path.join(os.path.dirname(__file__), 'log/spider.log')
        with open(log_filename, 'a+') as log:
            log.write('{} ^*^ IP:{} ^*^ KEY:{} ^*^ PAGE:{} \n'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), request.remote_addr , keyword, page))
            print('日志已记录')

        return html

    except ValueError:
        html = '请键入纯数字的page字段'
        return html

    # 返回本地数据
    except Exception as err:
        log_filename = os.path.join(os.path.dirname(__file__), 'log/spider.log')
        with open(log_filename, 'a+') as log:
            log.write('{} ^*^ IP:{} ^*^ KEY:{} ^*^ PAGE:{} ^*^ "本地数据" \n'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), request.remote_addr, keyword, page))
        back_filename = os.path.join(os.path.dirname(__file__), 'back/back.txt')
        f = open(back_filename, encoding='utf-8')
        html = f.read()
        f.close()
        print('调用了本地数据， 错误：{}'.format(err))
        return html

@app.route('/detail', methods=['get', 'post'])
def detail():
    # 获取通过url请求传参的数据
    id = request.values.get('id')
    ip = request.remote_addr

    mysql = MySQL()
    spider = DetailsSpider()

    log_name =os.path.join(os.path.dirname(__file__), 'log/detail.log')
    f = open(log_name, 'a+') # 撰写日志文件
    try:
        result = mysql.detail_ok(keyword=id) # 查询数据库是否存在， 存在则返回内容，不存在返回空

        if len(id) != 12:
            f.write('{} ^*^ ip:{} ^*^ id:{} ^*^ 查询ID不满12位\n'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ip, id))
            return "商品ID不满12位，请检查后查询"

        elif result: # 从数据库调用
            result = mysql.detail_ok(keyword=id)
            f.write('{} ^*^ ip:{} ^*^ id:{} ^*^ 查询ID数据库已存在\n'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ip, id))
            return result

        else: # 重新调用爬虫
            result = spider.main(id=id)
            f.write('{} ^*^ ip:{} ^*^ id:{} ^*^ 成功写入数据库\n'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ip, id))
            return result

    except ValueError as err:
        f.write('{}, 查询ID不符合规则, id={}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id))
        return '商品ID：{}, <br/> 错误信息：{}, 请检查商品ID是否正确'.format(id, err)

    finally:
        f.close()

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)