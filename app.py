from flask import Flask, escape, request
import sqlite3, json

app = Flask(__name__)

#-------------------------------------------------------------------------------
#                               Create DB
#-------------------------------------------------------------------------------
conn = sqlite3.connect('test.db',check_same_thread=False)

print ("Opened database successfully")
cursor  = conn.cursor()
cursor.execute("DROP TABLE TESTS;")

# table TESTS
cursor.execute("""CREATE TABLE IF NOT EXISTS TESTS
    (test_id INTEGER PRIMARY KEY,
    subject TEXT);""")

print ("Table TESTS created successfully")

# table SCORES
cursor.execute('''CREATE TABLE IF NOT EXISTS SCORES
       (scantron_id INT PRIMARY KEY NOT NULL, 
        scantron_url TEXT,
        name         TEXT,
        subject      TEXT,
        score        INT) ;''')
print ("Table SCORES created successfully")

test_id = 0
scantron_id = 0

#-------------------------------------------------------------------------------
#                               Create a test
#-------------------------------------------------------------------------------
@app.route('/api/tests', methods=['POST'])
def create_test():
    global test_id
    test_id = test_id + 1

    req = request.json
    subject = req["subject"]
    answer_keys = req["answer_keys"]
    
    try:
        # table TESTS
        sql = 'INSERT INTO TESTS (test_id, subject) VALUES (?,?)'
        val = (test_id, subject,)
        cursor.execute(sql, val)

        # table Test_x
        table_name = "Test_" + str(test_id)
        sql = "CREATE TABLE IF NOT EXISTS " + table_name + "(key_num INT, key CHAR(1));"
        cursor.execute(sql)
        print ("Table " + table_name +" created successfully")

        for num in answer_keys:
            sql = "INSERT INTO " + table_name + " (key_num, key) VALUES (?,?)"
            val = (num, answer_keys[num],)
            cursor.execute(sql, val)
        
        # sql = "SELECT key FROM " + table_name + " WHERE key_num = 1;" 
        # cursor.execute(sql)
        # rows = cursor.fetchall()
        # for row in rows:
        #     print(row)

    except Exception as E:
        print("Error: ", E)
    
    return{ "test_id":test_id , "subject" : subject, "answer_keys" : answer_keys, "submissions" : "[]" }, 201



#-------------------------------------------------------------------------------
#                               Upload a scantron
#-------------------------------------------------------------------------------
#curl -F 'data=@/Users/fay/Desktop/273/cmpe273-assigment2/scantron-1.json' http://localhost:5000/api/tests/1/scantrons
@app.route('/api/tests/<test_id>/scantrons', methods=['POST'])
def upload_scantrons(test_id):
    global scantron_id
    scantron_id = scantron_id + 1
    scantron_url = "http://localhost:5000/files/scantron-1.json"
    score = 0

    try:
        f = request.files['data']
        file = f.read()
        scantron = json.loads(file)
        name = scantron['name']
        subject = scantron['subject']
        answers = scantron['answers']

        # table Submission_Test_x
        table_name = "Submission_Test_" + str(test_id)
        sql = "CREATE TABLE IF NOT EXISTS " + table_name + "(scantron_id INT, name TEXT, ans_number INT, ans CHAR(1));"
        cursor.execute(sql)
        print ("Table " + table_name +" created successfully")

        for num in answers:
            sql = "INSERT INTO " + table_name + " (scantron_id, ans_number, ans) VALUES (?,?,?)"
            val = (scantron_id, num, answers[num],)
            score = score + is_correct(test_id, num, answers[num])
            cursor.execute(sql, val)
            

        # table SCORES
        sql = 'INSERT INTO SCORES (scantron_id, scantron_url, name, subject, score) VALUES (?,?,?,?,?)'
        val = (scantron_id, scantron_url, name, subject, score,)
        cursor.execute(sql, val)

        cursor.execute('SELECT * FROM SCORES')
        rows = cursor.fetchall()
        for row in rows:
            print(row)

    except Exception as E:
        print("Error: ", E)

    

    return { "scantron_id": scantron_id, "scantron_url": scantron_url, "name": name, "subject": subject,"score": score, "result": answers}, 201


def is_correct(test_id, num, ans):
    table_name = "Test_" + str(test_id)
    sql = "SELECT key FROM " + table_name + " WHERE key_num = " + num + ";" 
    cursor.execute(sql)
    key = cursor.fetchone()[0]
    if key == ans:
        return 1
    
def 

#-------------------------------------------------------------------------------
#                           Check all scantron submissions
#-------------------------------------------------------------------------------
@app.route('/api/tests/<test_id>', methods=['GET'])
def check_scantrons(test_id):
    global scantron_id
    scantron_id = scantron_id + 1


    return { }