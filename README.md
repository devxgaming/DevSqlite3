# PySqlite3 Helper
A Python package to create sqlite3 database and get data and insert data with python classes, you can also using Sqlite3 commands!


# Why PySqlite3 helper?
It is an easy-to-use and fastest library, where it can maintain its connection with Sqlite3 database while working

## install by PyPI:

```
pip3 install DevSqlite3==0.0.1
or
python -m pip install DevSqlite3==0.0.1
```

## Usage

first create python file called tables.py or some other name

```
# class name is your table name
class Users:
	# this is your table indexes, you must add self.id = "text" for work without any error
	def __init__(self):
		# default index
		self.id = "text"
		# add indexes to your table
		self.username = "text"
		self.password = "text"
		self.first_name = "text"
		self.last_name = "text"
		# etc...

# you can create other class for other database in this file

```

build sqlite database in your main project

```
from DevSqlite3.DevDB import Database, DatabaseBuilder

from table import * # table is your table.py python file 

@Database
class YourUsersDatabaseName(DatabaseBuilder):
	def __init__(self):
		super().__init__(self)
	
	@staticmethod
	def __superclass__():
		return Users # this is your Users class on table.py python file

# database was successfully created!!

```

now some examples:

```
# insert data to database

user = Users()
user.id = 0 # don't use it because it will change automatically to INTEGER PRIMARY KEY
user.username = "omar.othman"
user.password = "******"
user.first_name = "Omar"
user.last_name = "Othman"

db = YourUsersDatabaseName()
db.insert(user)

# get data from database
db = YourUsersDatabaseName()
result = db.select(Users).where("username").equals("omar.othman").get_first()
if result:
	print("hey i found him:\nFirstName: {}\nLastName: {}\nPassword: {}".format(result.first_name, result.last_name, result.password))
else:
	print("Oh sorry not found")

# get all users name equals omar.othman
result = db.select(Users).where("username").equals("omar.othman").get_all() # result as array
if result:
	print("got some users")
	for user in result:
		print("FirstName: {}\nLastName: {}\nPassword: {}".format(user.first_name, user.last_name, user.password))
else:
	print("Oh sorry not found")
	
# update result
if result:
	result.password = "1234"
	db.update(result) # update if exists
	# you can use also db.insertOrUpdate(result), that's mean delete if exists and insert

# delete result:
if result:
	db.delete(result)


# start with sqlite3 commands
db = YourUsersDatabaseName()
db.select(Users).query("update __table__ set password='1234' where username='omar.othman'") # use __table__ for table name


# or get result as superclass array
result = db.select(Users).query("select * from __table__ where etc.. or just select * from __table__") # result will be empty array if empty or array of Users
if result:
	for user in result:
		print(user.username)

# is not finish there is more examples XD

db = YourUsersDatabaseName()
result = db.select(Users).get_all()
# or
result = db.select(Users).order_by("variable_name", stuff="desc", limit=10).get_all() # stuff defult is asc and limit 0 is means all of data
# or
result = db.select(Users).where("first_name").like("Omar").order_by("username").get_all()
# or
result = db.select(Users).where("first_name).like("Omar").or_where("last_name").like("Othman").get_all()
# or
result = db.select(Users).where("first_name").like("Omar").and_where("last_name").like("Othman").get_all()

# or
result = db.select(Users).where("username").equals("omar.othman").and_where("password").equals("123").get_first()




# you can also insert list or dict or int or str in class varablie examples

user = Users()
user.username = "omar.othman"
user.password = "12345"
user.first_name = ["Omar", "other", "other..."]
user.last_name = {"key": "value"}
db = YourUsersDatabaseName()
db.insert(user)
# and you will got result as list or dict
db = YourUsersDatabaseName()
result = db.select(Users).where("username").equals("omar.othman").get_first()
if result:
	for item in result.first_name:
		print(item)
	for key in result.last_name:
		print("Key: {}, Value: {}".format(key, result.last_name[key]))
# etc......

```

## Database Select class functions

Function name | paramerts
------------ | -------------
where | class_variable_name
or_where | class_variable_name
and_where | class_variable_name
equals | string, integar
get_first | get the first result from sqlite3 database as python class or None if not found
get_all | get all result from sqlite3 database as array of python class or empty array if not found
query | sqlite3 comnmands use __table__ instand of table_name, return empty array if there no result, or array of class

## Database functions

Function Name | Parameter
------------ | -------------
insert | python class
insertOrUpdate | python class
delete | python class
update | python class
Select | python class


# that's was all

Thank you if you want to support me https://paypal.me/nxdev 






		