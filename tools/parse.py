import re
import requests

from .API import get_ua

'''
各类字段提取规则
'''

####################################   提取一级页面   ####################################
def get_shop_img(html):
    # 提取商品图片
    all_goods_imgs = []
    result = re.findall('<img src=(.*?).jpg', html)
    for item in result:
        good = str(item).replace('\\', '')
        good = str(good).replace(' ', '')
        good = str(good).replace('"', '')
        # "https://cbu01.alicdn.com/img/ibank/2019/792/289/11903982297_745176060.220x220xz.jpg",
        good += '.jpg'
        good = good.replace('.220x220xz', '')
        all_goods_imgs.append(good)
    return all_goods_imgs

def get_shop_title(html):
    # 提取商品标题
    all_goods_titles = []
    result = re.findall('alt.*?=(.*?.)\">', html)
    for item in result:
        title = str(item).replace('"', '')
        title = str(title).replace('\\', '').lstrip()
        all_goods_titles.append(title)
    return all_goods_titles

def get_shop_price(html):
    # 提取商品价格
    result = re.findall(r'sm-offer-priceNum sw-dpl-offer-priceNum.*? title.*?=(.*?).>', html)
    all_goods_prices = []
    for item in result:
        price = str(item).replace('\\', '')
        price = str(price).replace('"&yen;', '')
        all_goods_prices.append(price)
    if len(all_goods_prices) == 19:
        all_goods_prices.insert(13, '')
    return all_goods_prices

def get_shop_id(html):
    # 提取商品ID，构造二级页面的URL
    result = re.findall("t-offer-id.*?=(.*?).t", html)
    goods_ids = []
    for item in result:
        # print(re.findall(r'[0-9]\d', item))
        goods_id = re.sub("\D", "", item)
        # https://detail.1688.com/offer/597910617731.html
        goods_ids.append(goods_id)
    return goods_ids

####################################   提取二级页面   ####################################
'''
如果价格是范围性的，则类型价格不一致，需要在“skuMap”中再次提取价格数据
如果价格是起批量决定的，则类型价格无需再次提取
'''
# 获取json文件, 返回一个字典
def get_json(html):
    # 获取json文件, 这里返回的是一个字典类型的数据
    s = re.findall('"sku".*?{(.*?)};', html, re.S)[0]
    s = str(s).replace('\n', '')
    s = s.replace(' ', '')
    s = '{' + s

    global false, null, true
    false = null = true = ''

    s = eval(s)
    return s

# 提取二级页面的商品标题
def get_shop_title_two(html):
    # 提取二级页面的商品标题, 固定
    result = re.findall('<h1 class="d-title">(.*?)</h1>', html)[0]
    return result

# 提取类型信息
def get_types(html):
    # 提取的方式有里两种，一种是有类型图片的，一种是文字类型的

    # 无论是哪种提取方式，都必须先判断价格是批发价还是范围价

    # 提取图片类型
    def get_types_pic(result):
        print('[图片类型]')
        # 价格为批发价格时的处理
        def pi_fa(result, price):
            print('[图片类型] 批发价')

            # 特殊处理
            def te_shu(result):
                print('[批发价] 特殊处理')
                # 提取所有的颜色
                color = {}
                for item in result['skuProps'][0]['value']:
                    try:
                        color[item['name']] = item['imageUrl']  # 获取URL
                    except Exception:
                        color[item['name']] = ''

                skuMap = []
                sku_list = []
                for c in color:
                    # sku_list = {'name':'规格名', 'stock(库存)': '', 'price(原价)':'', 'discountPrice(折扣价)':''}
                    name = c
                    try:
                        stock = result['skuMap'][c]['canBookCount']
                    except Exception:
                        stock = 0
                    try:
                        price = result['skuMap'][c]['price']
                    except Exception:
                        price = result['price']
                    try:
                        discountPrice = result['skuMap'][c]['discountPrice']
                    except Exception:
                        discountPrice = ''

                    sku_list = {'name': c, 'stock': stock, 'price': price, 'discountPrice': discountPrice}

                skuMap.append({'title': '', 'specifications': sku_list, 'url':''})

                return skuMap

            # 判断是否需要特殊处理
            if len(result['skuProps']) == 1:
                return te_shu(result)

            print('[批发价格] 正常处理')
            # 提取所有的颜色
            color = {}
            for item in result['skuProps'][0]['value']:
                try:
                    color.setdefault(item['name'], item['imageUrl'])
                except KeyError:
                    color.setdefault(item['name'], '')

            # 提取所有的尺码
            size = []
            for item in result['skuProps'][1]['value']:
                try:
                    size.append(item['name'])
                except Exception:
                    size.append('')

            # 提取URL
            urls = {}
            for item in result['skuProps'][0]['value']:
                try:
                    urls[item['name']] = item['imageUrl']
                except Exception:
                    urls[item['name']] = ''

            # 两两自由组合，skuMap
            # {'title(类型)': '', 'specifications(规格)': sku_list, 'url':''}
            skuMap_keys = []
            for c in set(color):
                # [{'name':'规格名', 'stock(库存)': '', 'price(原价)':'', 'discountPrice(折扣价)':''}, {...}]
                sku_list = []
                for s in set(size):
                    key = (c + '&gt;' + s)
                    try:
                        stock = result['skuMap'][key]['canBookCount']  # 库存
                    except Exception:
                        stock = 0  # 库存
                    try:
                        price = result['skuMap'][key]['price']  # 原价
                    except Exception:
                        price = result['priceRange'][0][1]  # 原价

                    discountPrice = ''  # 折扣价
                    sku_list.append(
                        {'name': s, 'stock': stock, 'price': price, 'discountPrice': discountPrice})  # 把同一类型下的所有规格添加到列表

                skuMap_keys.append({'title': c, 'specifications': sku_list, 'url': urls[c]})  # 数据整合
            # {'title(类型)': '', 'specifications(规格)': [{'name':'规格名', 'stock(库存)': '', 'price(原价)':'', 'discountPrice(折扣价)':''}, {...}], 'url':''}
            return skuMap_keys

        # 价格为范围价格时的处理
        def fan_wei(result):
            print('[图片类型] 范围价')

            # 特殊处理
            def te_shu(result):
                print('特殊处理')
                # 提取所有的颜色
                color = {}
                for item in result['skuProps'][0]['value']:
                    try:
                        color[item['name']] = item['imageUrl']  # 获取URL
                    except Exception:
                        color[item['name']] = ''

                skuMap = []
                sku_list = []
                for c in color:
                    # sku_list = {'name':'规格名', 'stock(库存)': '', 'price(原价)':'', 'discountPrice(折扣价)':''}
                    name = c
                    try:
                        stock = result['skuMap'][c]['canBookCount']
                    except Exception:
                        stock = 0
                    try:
                        price = result['skuMap'][c]['price']
                    except Exception:
                        price = ''
                    try:
                        discountPrice = result['skuMap'][c]['discountPrice']
                    except Exception:
                        discountPrice = ''

                    sku_list = {'name': c, 'stock': stock, 'price': price, 'discountPrice': discountPrice}

                skuMap.append({'title': '', 'specifications': sku_list, 'url': ''})

                return skuMap

            # 判断是否只有规格
            if len(result['skuProps']) == 1:
                return te_shu(result)

            # 正常处理
            print('正常处理')
            # 提取颜色
            color = {}
            for item in result['skuProps'][0]['value']:
                try:
                    color[item['name']] = item['imageUrl']
                except Exception:
                    color[item['name']] = ''

            # 提取尺码
            size = []
            for item in result['skuProps'][1]['value']:
                size.append(item['name'])

            # 两两自由组合
            skuMap = []
            for c in color:
                sku_list = []
                for s in size:
                    # {'name':'规格名', 'stock(库存)': '', 'price(原价)':'', 'discountPrice(折扣价)':''}
                    key = c + '&gt;' + s
                    name = s
                    try:
                        stock = result['skuMap'][key]['canBookCount']
                    except Exception:
                        stock = 0
                    try:
                        price = result['skuMap'][key]['price']
                    except Exception:
                        price = ''
                    try:
                        discountPrice = result['skuMap'][key]['discountPrice']
                    except Exception:
                        discountPrice = ''
                    sku_list.append({'name':name, 'stock':stock, 'price':price, 'discountPrice':discountPrice})
                # {'title(类型)': '', 'specifications(规格)': sku_list, 'url': ''}
                try:
                    skuMap.append({'title':c, 'specifications':sku_list, 'url':color[c]})
                except Exception:
                    skuMap.append({'title': c, 'specifications': sku_list, 'url': ''})

            return skuMap

        # 折扣价
        def zhe_kou(result):
            # 批发价格的处理
            def pi_fa(result):
                print('[折扣价] 批发价')
                # 特殊处理
                def te_shu(result):
                    print('[批发价] 特殊处理')
                    # 提取所有的颜色
                    color = {}
                    for item in result['skuProps'][0]['value']:
                        try:
                            color[item['name']] = item['imageUrl']  # 获取URL
                        except Exception:
                            color[item['name']] = ''

                    skuMap = []
                    sku_list = []
                    for c in color:
                        # sku_list = {'name':'规格名', 'stock(库存)': '', 'price(原价)':'', 'discountPrice(折扣价)':''}
                        name = c
                        try:
                            stock = result['skuMap'][c]['canBookCount']
                        except Exception:
                            stock = 0
                        try:
                            price = result['skuMap'][c]['price']
                        except Exception:
                            price = result['price']
                        try:
                            discountPrice = result['skuMap'][c]['discountPrice']
                        except Exception:
                            discountPrice = ''

                        sku_list = {'name': c, 'stock': stock, 'price': price, 'discountPrice': discountPrice}
                    skuMap.append({'title': '', 'specifications': sku_list, 'url': ''})

                    return skuMap

                # 判断是否需要特殊处理
                if len(result['skuProps']) == 1:
                    return te_shu(result)

                print('[批发价] 正常处理')
                # 提取所有的颜色
                color = {}
                for item in result['skuProps'][0]['value']:
                    try:
                        color.setdefault(item['name'], item['imageUrl'])
                    except KeyError:
                        color.setdefault(item['name'], '')

                # 提取所有的尺码
                size = []
                for item in result['skuProps'][1]['value']:
                    try:
                        size.append(item['name'])
                    except Exception:
                        size.append('')

                # 提取URL
                urls = {}
                for item in result['skuProps'][0]['value']:
                    try:
                        urls[item['name']] = item['imageUrl']
                    except Exception:
                        urls[item['name']] = ''

                # 两两自由组合，skuMap
                # {'title(类型)': '', 'specifications(规格)': sku_list, 'url':''}
                skuMap = []
                for c in set(color):
                    # [{'name':'规格名', 'stock(库存)': '', 'price(原价)':'', 'discountPrice(折扣价)':''}, {...}]
                    sku_list = []
                    for s in set(size):
                        key = (c + '&gt;' + s)
                        try:
                            stock = result['skuMap'][key]['canBookCount'] # 库存
                        except Exception:
                            stock = 0  # 库存
                        try:
                            price = result['skuMap'][key]['price'] # 原价
                        except Exception:
                            price = result['price'] # 原价
                        try:
                            discountPrice = result['skuMap'][key]['discountPrice']  # 折扣价
                        except Exception:
                            discountPrice = ''  # 折扣价

                        sku_list.append({'name':s, 'stock':stock, 'price':price, 'discountPrice':discountPrice}) # 把同一类型下的所有规格添加到列表
                    try:
                        skuMap.append({'title':c, 'specifications':sku_list, 'url':urls[c]}) # 数据整合
                    except Exception:
                        skuMap.append({'title': c, 'specifications': sku_list, 'url': ''})  # 数据整合
                # {'title(类型)': '', 'specifications(规格)': [{'name':'规格名', 'stock(库存)': '', 'price(原价)':'', 'discountPrice(折扣价)':''}, {...}], 'url':''}

                return skuMap

            # 范围价格的处理
            def fan_wei(result):
                print('[折扣价] 范围价')

                # 特殊处理
                def te_shu(result):
                    print('[范围价] 特殊价')
                    # 提取所有的颜色
                    color = {}
                    for item in result['skuProps'][0]['value']:
                        try:
                            color[item['name']] = item['imageUrl']  # 获取URL
                        except Exception:
                            color[item['name']] = ''
                    skuMap = []
                    sku_list = []
                    for c in color:
                        # sku_list = {'name':'规格名', 'stock(库存)': '', 'price(原价)':'', 'discountPrice(折扣价)':''}
                        name = c
                        try:
                            stock = result['skuMap'][c]['canBookCount']
                        except Exception:
                            stock = 0
                        try:
                            price = result['skuMap'][c]['price']
                        except Exception:
                            price = ''
                        try:
                            discountPrice = result['skuMap'][c]['discountPrice']
                        except Exception:
                            discountPrice = ''

                        sku_list = {'name': c, 'stock': stock, 'price': price, 'discountPrice': discountPrice}
                    skuMap.append({'title': '', 'specifications': sku_list, 'url': ''})

                    return skuMap

                # 判断是否需要特殊处理
                if len(result['skuProps']) == 1:
                    return te_shu(result)

                print('[范围价] 正常处理')
                # 提取所有颜色
                color = {}
                for item in result['skuProps'][0]['value']:
                    try:
                        color[item['name']] = item['imageUrl']
                    except Exception:
                        color[item['name']] = ''

                # 提取所有尺码
                size = []
                for item in result['skuProps'][1]['value']:
                    size.append(item['name'])

                # 两两自由组合
                skuMap = []
                for c in color:
                    sku_list = []
                    for s in size:
                        key = c + '&gt;' + s
                        # [{'name':'规格名', 'stock(库存)': '', 'price(原价)':'', 'discountPrice(折扣价)':''}, {...}]
                        stock = result['skuMap'][key]['canBookCount'] # 库存
                        try:
                            price = result['skuMap'][key]['price'] # 原价
                        except Exception:
                            price = ''  # 原价
                        try:
                            discountPrice = result['skuMap'][key]['discountPrice'] # 折扣价
                        except Exception:
                            discountPrice = '' # 折扣价
                        # [{'name':'规格名', 'stock(库存)': '', 'price(原价)':'', 'discountPrice(折扣价)':''}, {...}]
                        sku_list.append({'name':s, 'stock':stock, 'price':price, 'discountPrice':discountPrice})
                    # {'title(类型)': '', 'specifications(规格)': sku_list, 'url': ''}

                    skuMap.append({'title':c, 'specifications':sku_list, 'url':color[c]})

                return skuMap

            # 判断条件
            if '-' in result['discountPrice']: # 范围价格
                return fan_wei(result)
            else:
                return pi_fa(result)

        # 判断需要哪种处理规则，判断思路：先判断是否活动价格，再判断批发或者范围
        result = dict(result) # 转为字典

        # 判断是不是活动价格
        try:
            if result['discountPrice']: # 折扣价
                return zhe_kou(result)
        except Exception:
            if '-' in result['price']: # 范围价格
                return fan_wei(result)
            else:
                try:
                    price = result['priceRange'] # 批发价格
                    return pi_fa(result, price)
                except Exception:
                    price = result['price']  # 批发价格
                    return pi_fa(result, price)

    # 提取文字类型
    def get_types_word(result):
        # 范围价
        def fan_wei(result):
            print('[文字类型] 范围价')

            # 特殊处理
            def te_shu(result):
                print('[范围价] 特殊处理')
                # 提取所有的颜色
                color = {}
                for item in result['skuProps'][0]['value']:
                    try:
                        color[item['name']] = item['imageUrl']  # 获取URL
                    except Exception:
                        color[item['name']] = ''
                skuMap = []
                sku_list = []
                for c in color:
                    # sku_list = {'name':'规格名', 'stock(库存)': '', 'price(原价)':'', 'discountPrice(折扣价)':''}
                    name = c
                    try:
                        stock = result['skuMap'][c]['canBookCount']
                    except Exception:
                        stock = 0
                    try:
                        price = result['skuMap'][c]['price']
                    except Exception:
                        price = ''
                    try:
                        discountPrice = result['skuMap'][c]['discountPrice']
                    except Exception:
                        discountPrice = ''

                    sku_list = {'name': c, 'stock': stock, 'price': price, 'discountPrice': discountPrice}

                skuMap.append({'title': '', 'specifications': sku_list, 'url': ''})

                return skuMap

            # 判断是否需要特殊处理
            if len(result['skuProps']) == 1:
                return te_shu(result)

            # 提取所有颜色
            color = []
            for item in result['skuProps'][0]['value']:
                color.append(item['name'])

            # 提取所有尺码
            size = []
            for item in result['skuProps'][1]['value']:
                size.append(item['name'])

            # 两两自由组合
            # {'title(类型)': '', 'specifications(规格)': sku_list, 'url':''}
            skuMap = []
            for c in set(color):
                # [{'name':'规格名', 'stock(库存)': '', 'price(原价)':'', 'discountPrice(折扣价)':''}, {...}]
                sku_list = []
                for s in set(size):
                    key = c + '&gt;' + s
                    try:
                        price = result['skuMap'][key]['price'] # 原价
                    except Exception:
                        price = ''  # 原价
                    try:
                        discountPrice = result['skuMap'][key]['discountPrice'] # 折扣价
                    except Exception:
                        discountPrice = ''  # 折扣价
                    stock = result['skuMap'][key]['canBookCount'] # 库存
                    sku_list.append({'name':s, 'stock':stock, 'price':price, 'discountPrice':discountPrice})

                skuMap.append({'title':c, 'specifications': sku_list, 'url': ''})
            return skuMap

        # 批发价
        def pi_fa(result):
            print('[文字类型] 批发价')
            # 特殊处理
            def te_shu(result):
                print('[批发价] 特殊处理')
                # 提取所有的颜色
                color = {}
                for item in result['skuProps'][0]['value']:
                    try:
                        color[item['name']] = item['imageUrl']  # 获取URL
                    except Exception:
                        color[item['name']] = ''
                skuMap = []
                sku_list = []
                for c in color:
                    # sku_list = {'name':'规格名', 'stock(库存)': '', 'price(原价)':'', 'discountPrice(折扣价)':''}
                    name = c
                    try:
                        stock = result['skuMap'][c]['canBookCount']
                    except Exception:
                        stock = 0
                    try:
                        price = result['skuMap'][c]['price']
                    except Exception:
                        price = result['priceRange'][0][1]
                    try:
                        discountPrice = result['skuMap'][c]['discountPrice']
                    except Exception:
                        discountPrice = ''

                    sku_list = {'name': c, 'stock': stock, 'price': price, 'discountPrice': discountPrice}

                skuMap.append({'title': '', 'specifications': sku_list, 'url': ''})

                return skuMap

            # 判断是否需要特殊处理
            if len(result['skuProps']) == 1:
                return te_shu(result)

            price = result['priceRange'][0][1]

            # 提取所有颜色
            color = []
            for item in result['skuProps'][0]['value']:
                color.append(item['name'])

            # 提取所有尺码
            size = []
            for item in result['skuProps'][1]['value']:
                size.append(item['name'])

            # 两两组合
            skuMap = []
            for c in color:
                sku_list = []
                for s in size:
                    key = c + '&gt;' + s
                    stock = result['skuMap'][key]['canBookCount'] # 库存
                    price = price # 原价
                    discountPrice = '' # 折扣价
                    sku_list.append({'name':s, 'stock':stock, 'price':price, 'discountPrice':discountPrice})
                skuMap.append({'title': c, 'specifications': sku_list, 'url':''})
            return skuMap

        # 折扣价
        def zhe_kou(result):
            def fan_wei(result):
                print('[折扣价] 范围价')

                # 特殊处理
                def te_shu(result):
                    print('[折扣价] 特殊处理')
                    # 提取所有的颜色
                    color = {}
                    for item in result['skuProps'][0]['value']:
                        try:
                            color[item['name']] = item['imageUrl']  # 获取URL
                        except Exception:
                            color[item['name']] = ''
                    skuMap = []
                    sku_list = []
                    for c in color:
                        # sku_list = {'name':'规格名', 'stock(库存)': '', 'price(原价)':'', 'discountPrice(折扣价)':''}
                        name = c
                        try:
                            stock = result['skuMap'][c]['canBookCount']
                        except Exception:
                            stock = 0
                        try:
                            price = result['skuMap'][c]['price']
                        except Exception:
                            price = ''
                        try:
                            discountPrice = result['skuMap'][c]['discountPrice']
                        except Exception:
                            discountPrice = ''

                        sku_list = {'name': c, 'stock': stock, 'price': price, 'discountPrice': discountPrice}

                    skuMap.append({'title': '', 'specifications': sku_list, 'url': ''})

                    return skuMap

                # 判断是否需要特殊处理
                if len(result['skuProps']) == 1:
                    return te_shu(result)

                # 提取颜色
                color = {}
                for item in result['skuProps'][0]['value']:
                    try:
                        color[item['name']] = item['imageUrl']
                    except Exception:
                        color[item['name']] = ''

                # 提取尺码
                size = []
                for item in result['skuProps'][1]['value']:
                    size.append(item['name'])

                # 两两自由组合
                skuMap = []
                for c in color:
                    sku_list = []
                    for s in size:
                        key = c + '&gt;' + s
                        try:
                            price = result['skuMap'][key]['price']
                        except Exception:
                            price = ''
                        try:
                            stock = result['skuMap'][key]['canBookCount']
                        except Exception:
                            stock = 0
                        try:
                            discountPrice = result['skuMap'][key]['discountPrice']
                        except Exception:
                            discountPrice = ''
                        sku_list.append({'name':s, 'stock':stock, 'price':price, 'discountPrice':discountPrice})
                    try:
                        skuMap.append({'title':c, 'specifications':sku_list, 'url': color[c]})
                    except Exception:
                        skuMap.append({'title': c, 'specifications': sku_list, 'url': color[c]})
                return skuMap

            def pi_fa(result):
                print('[折扣价] 批发价')
                # 特殊处理
                def te_shu(result):
                    print('[批发价] 特殊处理')
                    # 提取所有的颜色
                    color = {}
                    for item in result['skuProps'][0]['value']:
                        try:
                            color[item['name']] = item['imageUrl']  # 获取URL
                        except Exception:
                            color[item['name']] = ''
                    skuMap = []
                    sku_list = []
                    for c in color:
                        # sku_list = {'name':'规格名', 'stock(库存)': '', 'price(原价)':'', 'discountPrice(折扣价)':''}
                        try:
                            stock = result['skuMap'][c]['canBookCount']
                        except Exception:
                            stock = 0
                        try:
                            price = result['skuMap'][c]['price']
                        except Exception:
                            price = result['priceRange'][0][1]
                        try:
                            discountPrice = result['skuMap'][c]['discountPrice']
                        except Exception:
                            discountPrice = ''

                        sku_list = {'name': c, 'stock': stock, 'price': price, 'discountPrice': discountPrice}

                    skuMap.append({'title': '', 'specifications': sku_list, 'url': ''})

                    return skuMap

                # 判断是否需要特殊处理
                if len(result['skuProps']) == 1:
                    return te_shu(result)

                # 提取所有颜色
                color = []
                for item in result['skuProps'][0]['value']:
                    color.append(item['name'])

                # 提取所有尺码
                size = []
                for item in result['skuProps'][1]['value']:
                    size.append(item['name'])

                # 两两自由组合
                skuMap = []
                for c in color:
                    sku_list = []
                    for s in size:
                        key = c + '&gt;' + s
                        try:
                            price = result['skuMap'][key]['price'] # 原价
                        except Exception:
                            try:
                                price = result['priceRange'][0][1] # 原价
                            except Exception:
                                price = result['price']
                        try:
                            discountPrice = result['skuMap'][key]['discountPrice'] # 折扣价
                        except Exception:
                            discountPrice = ''  # 折扣价
                        try:
                            stock = result['skuMap'][key]['canBookCount'] # 库存
                        except Exception:
                            stock = 0  # 库存
                        sku_list.append({'name':s, 'stock':stock, 'price':price, 'discountPrice':discountPrice})
                    skuMap.append({'title':c, 'specifications':sku_list, 'url': ''})
                return skuMap

            # 判断范围价还是批发价
            if '-' in result['discountPrice']: # 范围价
                return fan_wei(result)
            else:
                return pi_fa(result)


        # 判断折扣价
        try:
            if result['priceRange']: # 批发价
                return pi_fa(result)
        except Exception:
            try:
                if result['discountPrice']: # 折扣价
                    return zhe_kou(result)
            except Exception:
                return pi_fa(result)

        if '-' in result['price']: # 范围价
            return fan_wei(result)


    # 提取json，返回字典
    html_json = get_json(html)
    result = dict(html_json)

    # 判断调用图片提取规则还是文字提取规则
    if 'imageUrl' in str(result):
        # 图片类型
        d = get_types_pic(result)
        return d
    else:
        # 文字类型
        d = get_types_word(result)
        return d

# 提取商品展示栏的图片
def get_shop_spic_two(html):
    # 提取商品展示栏的图片 (固定，无需更换)
    results = re.findall(',"original":"(.*?)"}', html)
    return list(set(results)) # 去重

# 提取详细的图片(反爬过于严重，使用selenium获取)
def get_detail_pic(html):
    # 提取详细的图片 (固定，无需更换提取方式)
    pic_list_url = re.findall('data-tfs-url="(.*?)"', html)[0].strip() # 图片列表的URL

    # print('详细图片列表的URL:', pic_list_url)

    # 已经反爬，目前没研究出新的方案，使用selenium获取源码

    html = requests.get(url = pic_list_url, headers = get_ua()).text # 访问源码之后获取所有图片的连接

    pic_list = re.findall('undefined.*?https://(.*?)\"', html) # 破网页，一会undefined， 一会absmiddle，还好我没固定，这里有新的字段直接列表叠加即可
    pic_list.extend(re.findall('absmiddle.*?https://(.*?)\"', html))
    pic_list.extend(re.findall('<img alt=.*?jpg.*?src=.*?"https://(.*?)\"', html))

    # 去重
    pic_list = set(pic_list)
    pic_list = list(pic_list)

    for item in pic_list:
        number = pic_list.index(item)
        pic_list[number] = str('https://' + item).replace('\\', '')
    return list(set(pic_list))

# 提取标题价格    价格有两种，一种是起批量决定的价格，一种是范围性的价格
def get_price(html):
    result = get_json(html)

    # 批发价
    def pi_fa(result):
        print('[标题价格] 正常的批发价')
        prices = result['priceRange']
        prices = {'type':1, 'price':prices}
        return prices

    # 特殊的批发价
    def pi_fa_te_shu(result):
        print('[标题价格] 特殊的批发价')
        # 需要提取起批量
        try:
            batch = re.findall('<span class="value">&ge;(.*?)</span>', html)[0]
        except Exception:
            try:
                batch = re.findall('<div class="obj-amount">\n(.*?)<span class="unit">', html)[0].strip()
            except Exception:
                print('提取起批量错误，默认为2')
                batch = 2

        price = result['price']

        result = [[int(batch), float(price)]]
        result = {'type': 1, 'price': result}

        return result

    # 范围价
    def fan_wei(result):
        # 需要提取起批量
        print('[标题价格] 正常的范围价')
        batch = int(re.findall('<span class="value">&ge;(.*?)</span>', html)[0])
        prices = result['price'].split('-')

        price = []
        # 字符串转列表
        for item in prices:
            price.append(float(item))

        price.insert(0, batch)

        prices = {'type':2, 'price':price}
        return prices

    # 判断是哪一种价格
    try:
        if '-' in result['price']:
            # print('范围价')
            return fan_wei(result)
        elif result['priceRange']:
            # print('正常的批发价')
            return pi_fa(result)
    except KeyError:
        # print('特殊批发价')
        return pi_fa_te_shu(result)


# 测试
# import os
# filename = os.path.join(os.path.dirname(__file__), 'index.html')
# with open(filename, 'r', encoding='gbk') as f:
#     html = f.read()
#     print(get_types(html))