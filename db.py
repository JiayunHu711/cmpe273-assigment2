import sqlite3

conn = sqlite3.connect('test.db')

print ("Opened database successfully")
cursor = conn.cursor()

sql = 'SELECT * FROM TESTS'
cursor.execute(sql)
print("print table")
for row in cursor:
    print("ID = ", row[0])            
    print("SUBJECT = ", row[1])
    print("KEYS = ", row[2],"\n")