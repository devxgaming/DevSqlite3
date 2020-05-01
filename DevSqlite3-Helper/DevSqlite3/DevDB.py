# Dev Database

# create by Omar Oth
from types import *

import sqlite3

CONNECTION = {}


def Database(_class: classmethod):
    DatabaseCreator(_class)
    return _class


class DatabaseCreator:
    def __init__(self, _class):
        self._class = _class
        self.connection = None
        self.cursor = None
        self.error = False
        self.keys = None
        self.sqlite_do()

    def sqlite_do(self):
        if self._class.__superclass__().__name__ in CONNECTION:
            self.connection = CONNECTION[self._class.__superclass__().__name__]["connection"]
            self.cursor = CONNECTION[self._class.__superclass__().__name__]["cursor"]
        else:
            self.connection = sqlite3.connect(self._class.__name__, timeout=5, check_same_thread=False)
            self.connection.isolation_level = None

            self.cursor = self.connection.cursor()
            CONNECTION[self._class.__superclass__().__name__] = {"connection": self.connection, "cursor": self.cursor}

        self.build()

    def build(self):
        if self._class is None:
            raise TypeError("Class must not by None")
        self.keys = self.__get_keys()
        if not self.keys:
            raise TypeError("There is not variable on class, please before you call @Database, make sure you have add variable to the super class")
        values = "id INTEGER PRIMARY KEY, "
        for key in self.keys:
            if key == "id":
                continue
            x = self._class.__superclass__()
            values += key + " "+eval("x().{}".format(key))+", "

        values = values[0: len(values) - 2].strip()

        self.create_table(self._class.__superclass__().__name__, values)

    def create_table(self, name, values):
        self.cursor.execute("create table if not exists {}({})".format(name, values))
        m = self.cursor.execute("select id from {} order by id desc limit 1".format(self._class.__superclass__().__name__))
        c = m.fetchone()
        if c:
            CONNECTION[self._class.__superclass__().__name__]["max"] = int(c[0])
        else:
            CONNECTION[self._class.__superclass__().__name__]["max"] = 1

    def __get_keys(self):
        x = self._class.__superclass__()
        return list(vars(x()).keys())


class Select(object):
    def __init__(self):
        self.__class = None
        self.__where = {}
        self.sql = ""

    def query(self, sql: str):
        if not self.__class:
            raise RuntimeError("To use Sqlite3 query, please first call 'select' example:\nYourDatabaseClass.select(Users).query('select * from __table__ where username='user'")
        if not sql.count("__table__"):
            raise RuntimeError("To select table please add on your query code, __table__, example: select * from __table__ .... etc...")

        sql = sql.replace("__table__", self.__class.__name__)
        try:
            cursor = CONNECTION[self.__class.__name__]["cursor"]
        except Exception:
            raise RuntimeError("Error, class {} is not supported, please make sure you have using this class on database __superclass__".format(self.__class.__name__))

        c = cursor.execute(sql)
        res = c.fetchall()
        final = []
        for data in res:
            result = dict(zip([c[0] for c in c.description], data))
            cls = self.__class()
            for k in result:
                setattr(cls, k, result[k])
            final.append(cls)
        return final

    def select(self, _class):
        if self.__class:
            raise Exception("Don't use tow time at one variable 'where' use one 'where' then use 'and_where'")
        self.__class = _class
        try:
            self.__class()
        except Exception as why:
            raise Exception("Select must callable, pass just class name, example:\nclass Name: etc....\n\nYourDatabase.select(Name). etc...")
        return self

    def where(self, variable: str):
        if self.__where:
            raise Exception("Don't use tow time at one variable 'where' use one 'where' then use 'and_where'")
        self.__where[variable] = {"target": None, "fix": None, "or": False}
        return self

    def and_where(self, variable: str):
        for key in self.__where:
            if self.__where[key]["target"] is None:
                raise Exception("You need to use some like [equals, like, count, order_by] for the first 'where' then use 'and_where' ")

        self.__where[variable] = {"target": None, "fix": None, "or": False}
        return self

    def or_where(self, variable: str):
        if not self.__where:
            raise Exception("Use where instance or_'where', you can use 'or_where' after 'where'")

        for key in self.__where:
            if self.__where[key]["target"] is None:
                raise Exception("You need to use some like [equals, like, order_by] for the first 'where' or 'and_where' ")

        self.__where[variable] = {"target": None, "fix": None, "or": True}
        return self

    def equals(self, to):
        for key in self.__where:
            if self.__where[key]["target"] is None:
                self.__where[key]["target"] = to
                self.__where[key]["fix"] = "="
                if self.__where[key]["fix"] == "=":
                    if isinstance(self.__where[key]["target"], str):
                        if self.__where[key]["or"] is True:
                            if self.sql:
                                self.sql += " or {}{}'{}'".format(key, self.__where[key]["fix"], self.__where[key]["target"])
                        else:
                            if self.sql:
                                self.sql += " and {}{}'{}'".format(key, self.__where[key]["fix"], self.__where[key]["target"])
                            else:
                                self.sql += "{}{}'{}'".format(key, self.__where[key]["fix"], self.__where[key]["target"])
                    else:
                        if self.sql:
                            self.sql += " and {}{}{}".format(key, self.__where[key]["fix"], self.__where[key]["target"])
                        else:
                            self.sql += "{}{}{}".format(key, self.__where[key]["fix"], self.__where[key]["target"])
                else:
                    if self.sql:
                        self.sql += " and {} {} {}".format(key, self.__where[key]["fix"], self.__where[key]["target"])
                    else:
                        self.sql += "{} {} {}".format(key, self.__where[key]["fix"], self.__where[key]["target"])
                break

        return self

    def order_by(self, variable, stuff="asc", limit=0):
        if self.sql:
            if limit > 0:
                self.sql += " order by {} {} limit {}".format(variable, stuff, limit)
            else:
                self.sql += " order by {} {}".format(variable, stuff)
        else:
            if limit > 0:
                self.sql = " order by {} {} limit {}".format(variable, stuff, limit)
            else:
                self.sql = " order by {} {}".format(variable, stuff)

        return self

    def like(self, string: str):
        for key in self.__where:
            if self.__where[key]["target"] is None:
                self.__where[key]["target"] = string
                self.__where[key]["fix"] = "like"
                if self.__where[key]["fix"] == "=":
                    if isinstance(self.__where[key]["target"], str):
                        if self.__where[key]["or"] is True:
                            if self.sql:
                                self.sql += " or {}{}'{}'".format(key, self.__where[key]["fix"], self.__where[key]["target"])
                        else:
                            if self.sql:
                                self.sql += " and {}{}'{}'".format(key, self.__where[key]["fix"],
                                                                 self.__where[key]["target"])
                            else:
                                self.sql += "{}{}'{}'".format(key, self.__where[key]["fix"],
                                                                 self.__where[key]["target"])
                    else:
                        if self.sql:
                            self.sql += " and {}{}{}".format(key, self.__where[key]["fix"], self.__where[key]["target"])
                        else:
                            self.sql += "{}{}{}".format(key, self.__where[key]["fix"], self.__where[key]["target"])
                else:
                    if self.sql:
                        self.sql += " and {} {} '{}'".format(key, self.__where[key]["fix"], self.__where[key]["target"])
                    else:
                        self.sql += "{} {} '{}'".format(key, self.__where[key]["fix"], self.__where[key]["target"])
                break

        return self

    def get_first(self):
        x = list(vars(self.__class()).keys())
        sql = "select {} from {}".format(", ".join(x), self.__class.__name__)
        if self.sql:
            if self.sql.startswith(" order"):
                sql += self.sql
            else:
                sql += " where " + self.sql
        try:
            cursor = CONNECTION[self.__class.__name__]["connection"]
            cursor = cursor.cursor()
        except Exception as w:
            raise RuntimeError("Error, class {} is not supported, please make sure you have using this class on database __superclass__".format(self.__class.__name__))
        c = cursor.execute(sql)
        result = c.fetchone()
        c.close()
        if result:
            cls = self.__class()
            i = 0
            for key in x:
                if isinstance(result[i], str):
                    try:
                        if result[i]:
                            value = eval(result[i])
                        else:
                            value = result[i]
                    except NameError:
                        value = result[i]
                    except SyntaxError:
                        value = result[i]
                else:
                    value = result[i]
                setattr(cls, key, value)
                i += 1
            return cls
        return None

    def get_all(self):
        x = list(vars(self.__class()).keys())
        sql = "select {} from {}".format(", ".join(x), self.__class.__name__)
        if self.sql:
            if self.sql.startswith(" order"):
                sql += self.sql
            else:
                sql += " where " + self.sql
        try:
            cursor = CONNECTION[self.__class.__name__]["connection"]
            cursor = cursor.cursor()
        except Exception as w:
            raise RuntimeError(
                "Error, class {} is not supported, please make sure you have using this class on database __superclass__".format(
                    self.__class.__name__))
        c = cursor.execute(sql)
        result = c.fetchall()
        c.close()
        final_result = []
        if result:
            for data in result:
                cls = self.__class()
                i = 0
                for key in x:
                    if isinstance(data[i], str):
                        try:
                            if data[i]:
                                value = eval(data[i])
                            else:
                                value = data[i]
                        except NameError:
                            value = data[i]
                        except SyntaxError:
                            value = data[i]
                    else:
                        value = data[i]
                    setattr(cls, key, value)
                    i += 1
                final_result.append(cls)
        return final_result


def __get_variable_name(self, variable):
        c = self.__class()
        x = list(vars(c).keys())
        for name in x:
            if eval("c.{}".format(name)) == variable:
                return name
        return None


class DatabaseBuilder(Select):
    def __init__(self, x):
        super().__init__()
        self.x = x

    def insert(self, data):
        if type(data) is not eval("self.x.__superclass__()"):
            raise Exception("Insert class must like super class")

        keys = self.__get_keys(eval("self.x.__superclass__()"))
        setattr(data, "id", CONNECTION[self.x.__superclass__().__name__]["max"] + 1)
        values = []
        for key in keys:
            if key == "id":
                continue
            value = eval("data.{}".format(key))
            if isinstance(value, str) or isinstance(value, int) or isinstance(value, dict) or isinstance(value, list) or isinstance(value, float) or value is None:
                values.append(value)
            else:
                raise BaseException(
                    "Error, variable type must be [str, int, dict, float, None], got: " + str(type(value)))
        keys.remove("id")
        limit = ["?" for x in keys]
        k = tuple(keys)
        v = tuple(values)
        l = tuple(limit)
        sql = "insert into {}{} values {}".format(self.x.__superclass__().__name__, str(k), l)
        sql = sql.replace("'", "")
        con = CONNECTION[self.x.__superclass__().__name__]["connection"]
        cur = con.cursor()
        cur.execute(sql, v)
        con.commit()
        cur.close()

    def delete(self, data):
        if type(data) is not eval("self.x.__superclass__()"):
            raise Exception("Delete class must like super class")

        con = CONNECTION[self.x.__superclass__().__name__]["connection"]
        cur = con.cursor()
        cur.execute("delete from {} where id=:id".format(self.x.__superclass__().__name__), {"id": data.id})
        con.commit()
        cur.close()

    def insertOrUpdate(self, data):
        if type(data) is not eval("self.x.__superclass__()"):
            raise Exception("Delete class must like super class")

        self.delete(data)
        self.insert(data)

    def update(self, data):
        if type(data) is not eval("self.x.__superclass__()"):
            raise Exception("Delete class must like super class")

        cur = CONNECTION[self.x.__superclass__().__name__]["connection"]
        cur = cur.cursor()
        row = cur.execute("select id from {} where id=:id".format(self.x.__superclass__().__name__), {"id": data.id})
        if row:
            self.delete(data)
            self.insert(data)
        cur.close()

    def __get_keys(self, data):
        return list(vars(data()).keys())








