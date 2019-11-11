'''
项目API文件
'''
import os
from redis import Redis
import configparser
import requests

# 获取随机header
def get_ua():
    config = configparser.ConfigParser()
    filename = os.path.join(os.path.dirname(__file__), 'config.ini')
    config.readfp(open(filename))
    redis = Redis(host=config.get('DB', 'host'), port=config.get('DB', 'port'), password=config.get('DB', 'password'), db=config.get('DB', 'db'))
    return {'User-Agent': str(redis.srandmember('ua'), 'utf-8')}

# 获取随机代理
def get_proxy():
    config = configparser.ConfigParser()
    filename = os.path.join(os.path.dirname(__file__), 'config.ini')
    config.readfp(open(filename))
    url = config.get('PROXY', 'url')
    ip = requests.get(url=url).text
    proxy = {
        'http' : 'http://{}'.format(ip),
        'https' : 'https://{}'.format(ip),
    }
    return proxy
