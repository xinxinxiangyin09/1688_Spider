import pymysql

'''
数据库的操作
'''

class MySQL(object):
    def __init__(self):
        self.db =pymysql.connect(host='localhost', user='root', password='0', db='spider')
        self.cursor = self.db.cursor()

    # 查询数据库中是否存在查询结果
    def detail_ok(self, keyword):
        sel = 'select content from detail1 where keyword = %s' % keyword
        self.cursor.execute(sel)
        result = self.cursor.fetchall()
        if result: # 数据存在
            return result[0][0]
        else:
            return


    def __del__(self):
        self.cursor.close()
        self.db.close()

if __name__ == '__main__':
    mysql = MySQL()
    result = mysql.detail_ok('594441078981')
    print(result)