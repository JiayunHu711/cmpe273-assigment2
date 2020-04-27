from flask import Flask, escape, request, jsonify
import sqlite3, json

app = Flask(__name__)

#-------------------------------------------------------------------------------
#                               Create DB
#-------------------------------------------------------------------------------
conn = sqlite3.connect('test.db',check_same_thread=False)

print ("Opened database successfully")
cursor  = conn.cursor()
#cursor.execute("DROP TABLE TESTS;")
#cursor.execute("DROP TABLE SCORES;")

# table TESTS
cursor.execute("""CREATE TABLE IF NOT EXISTS TESTS
    (test_id INTEGER PRIMARY KEY,
    subject TEXT);""")

print ("Table TESTS created successfully")

# table SCORES
cursor.execute("""CREATE TABLE IF NOT EXISTS SCORES
    (scantron_id INTEGER PRIMARY KEY,
    scantron_url TEXT,
    subject TEXT,
    score INTEGER);""")
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
    scantron_url = request.url_root + "files/scantron-1.json"
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
        val = (scantron_id, scantron_url, name, subject, score, )
        cursor.execute(sql, val)

    except Exception as E:
        print("Error: ", E)

    result = get_result(test_id, scantron_id)    

    return jsonify({"scantron_id": scantron_id, "scantron_url": scantron_url, "name": name, "subject": subject,"score": score, "result": result}), 201



def is_correct(test_id, num, ans):
    table_name = "Test_" + str(test_id)
    sql = "SELECT key FROM " + table_name + " WHERE key_num = " + num + ";" 
    cursor.execute(sql)
    key = cursor.fetchone()[0]
    if key == ans:
        return 1



def get_result(test_id, scantron_id):
    result = {}
    # table Test_x
    table_name = "Test_" + str(test_id)
    sql = "SELECT * FROM " + table_name + ";" 
    cursor.execute(sql)
    keys = cursor.fetchall()

    # table Submission_Test_x
    table_name = table_name = "Submission_Test_" + str(test_id)
    sql = "SELECT ans FROM " + table_name + " WHERE scantron_id = " + str(scantron_id) + ";" 
    cursor.execute(sql)
    answers = cursor.fetchall()

    for row in keys:
        num = row[0]
        key = row[1]
        ans = answers[num-1][0]
        num_dict = {"actual" : ans, "expected" : key}
        result[num] = num_dict

    return result



#-------------------------------------------------------------------------------
#                           Check all scantron submissions
#-------------------------------------------------------------------------------
@app.route('/api/tests/<test_id>', methods=['GET'])
def check_scantrons(test_id):

    try:
        # get subject
        # table TESTS
        sql = "SELECT subject FROM TESTS WHERE test_id = " + test_id + ";"
        cursor.execute(sql)
        subject = cursor.fetchone()[0]

        # get answer keys
        # table Test_x
        answer_keys = get_answers(test_id)

        # get submissions 
        # get all the scantron_ids from table Submission_Test_x
        scantron_ids = get_scantron_ids(test_id)

        submissions = []

        for scantron_id in scantron_ids:
            submission_dict = {}
            sql = "SELECT * FROM SCORES WHERE scantron_id = " + str(scantron_id) + ";"
            cursor.execute(sql)
            info = cursor.fetchall()
            for row in info:
                submission_dict["scantron_id"] = row[0]
                submission_dict["scantron_url"] = row[1]
                submission_dict["name"] = row[2]
                submission_dict["subject"] = row[3]
                submission_dict["score"] = row[4]
                submission_dict["result"] = get_result(test_id, scantron_id)
            submissions.append(submission_dict)

    except Exception as E:
        print("Error: ", E)

    return {"test_id": test_id, "subject": subject, "answer_keys": answer_keys, "submissions": submissions}



def get_answers(test_id):
    answer_keys = {}
    
    # table Test_x
    table_name = "Test_" + str(test_id)
    sql = "SELECT * FROM " + table_name + ";" 
    cursor.execute(sql)
    keys = cursor.fetchall()

    for row in keys:
        num = row[0]
        key = row[1]
        answer_keys[num] = key
    
    return answer_keys

def get_scantron_ids(test_id):
    ids = []
    # table Submission_Test_x
    table_name = table_name = "Submission_Test_" + str(test_id)
    sql = "SELECT DISTINCT scantron_id FROM " + table_name + ";" 
    cursor.execute(sql)
    scantron_ids = cursor.fetchall()

    for row in scantron_ids:
        num = row[0]
        ids.append(num)

    return ids
