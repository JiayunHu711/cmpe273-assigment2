from flask import jsonify

def show_result(test_id):
    result = {
        "1": {
            "actual": "A",
            "expected": "B"
        },
        "50": {
            "actual": "E",
            "expected": "E"
        }
    }
    return jsonify(result)

print(show_result)