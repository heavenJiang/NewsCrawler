import pymysql
from pymysql.cursors import DictCursor
from DBUtils.PooledDB import PooledDB
# from utils.config import cfg

class MySqlPool(object):
    __pool = None

    def __init__(self, db, host, port,
                 user, passwd):
        # 数据库构造函数，从连接池中取出连接，并生成操作游标
        
        try:
            self._conn = PooledDB(creator=pymysql, mincached=1, maxcached=5, host=host, port=port,
                              user=user, passwd=passwd, db=db, use_unicode=True, charset='utf8', cursorclass=DictCursor).connection()
            self._cursor = self._conn.cursor()
        except Exception as e:
            print (e)
            

    def __query(self, sql, param=None):
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        return count

    def __execute(self, sql, param=None):
        conn = self._conn
        cursor = conn.cursor()
        try:
            cursor.execute(sql, param)
            conn.commit()
        except pymysql.Error as e:
            conn.rollback()
            print (e)
            

    def __execute_many(self, sql, param=None):
        conn = self._conn
        cursor = conn.cursor()
        try:
            cursor.executemany(sql, param)
            conn.commit()
        except pymysql.Error as e:
            conn.rollback()
            print (e)
            

    def update(self, sql, param=None):
        """
        pool = MySqlPool()
        pool.update("update user_info set name = %s where user_id = %s", param=('Lucy', '001'))
        """
        self.__execute(sql, param)

    def delete(self, sql, param=None):
        """
        pool = MySqlPool()
        pool.delete('delete from user_info where name is null')
        """
        self.__execute(sql, param)

    def insert_one(self, sql, param=None):
        """
        pool = MySqlPool()
        pool.insert_one("INSERT INTO `user_info` (`user_id`,`name`) VALUES (%s,%s)", ('001', 'Jim'))
        """
        self.__execute(sql, param)

    def insert_many(self, sql, param=None):
        """
        pool = MySqlPool()
        pool.insert_many("INSERT INTO `user_info` (`user_id`,`name`) VALUES (%s,%s)", [('001', 'Jim'), ('002', 'Lucius')])
        """
        self.__execute_many(sql, param)

    def get_all(self, sql, param=None):
        conn = self._conn
        cursor = conn.cursor()
        count = cursor.execute(sql, param)
        if count > 0:
            result = cursor.fetchall()
        else:
            result = False
        return result

    def get_one(self, sql, param=None):
        conn = self._conn
        cursor = conn.cursor()
        count = cursor.execute(sql, param)
        if count > 0:
            result = cursor.fetchone()
        else:
            result = False
        return result

    def get_many(self, sql, num, param=None):
        conn = self._conn
        cursor = conn.cursor()
        count = cursor.execute(sql, param)
        if count > 0:
            result = cursor.fetchmany(num)
        else:
            result = False
        return result

    def dispose(self):
        self._conn.close()