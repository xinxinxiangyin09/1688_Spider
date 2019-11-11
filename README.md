# 爬虫项目部署

> author：素心

## 一、项目简介

  该项目是获取某网站商品的信息，并将其以API的形式返现。

## 二、环境

- CentOS 7.3
- MySQL 5.7.27
- Python 3.6.5
- Nginx 

## 二、源码简介

```python
.
├── back # 备用数据
│   └── back.txt
├── config.ini # 项目主配置文件
├── image # 图片文件
│   ├── demo.png
│   └── static
│       └── image
│           └── demo.png
├── log # 日志文件
│   ├── detail.log
│   └── spider.log
├── requirements.txt # pip环境
├── tools # 项目扩展文件
│   ├── add_ua.py # User-Agent池维护
│   ├── API.py # 项目API文件
│   ├── config.ini # 扩展配置文件
│   ├── db.py # 数据库有关的操作
│   ├── detail.py # 获取商品详情
│   ├── __init__.py # 路径更改文件
│   ├── parse.py # 数据提取规则
│   ├── spider.py # 商品搜索接口
│   └── trans.py # 翻译扩展，因对泰项目，故需要翻译
├── update # 查询参数更新脚本
│   ├── demo.png 
│   ├── get_query.py
│   └── ghostdriver.log
└── web.py # Flask文件
```

## 三、项目部署

### 1. CentOS 7.3 安装

略

### 2. Python 3.6.5安装

[参考]( https://www.cnblogs.com/chancey/p/9848867.html )

### 3. MySQL 5.7.27安装

[参考]( https://www.cnblogs.com/chancey/p/9848878.html )

### 4. UWSGI安装

```bash
pip install uwsgi -i https://pypi.douban.com/simple
```

创建配置文件(在当前目录下创建uwsgi.ini文件)

```bash
[uwsgi]
socket = 本机IP以及端口
chdir = /www
wsgi-file = /www/web.py
callable = app
processes = 4
threads = 2
pythonpath = /www
```

### 5.代码部署


## 四、注意事项
启动项目<br>
`systemctl restart redis`
`systemctl restart mysqld`
`nohup python -u web.py > log/pro.log 2&1 &`
