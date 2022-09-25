from funcx.sdk.client import FuncXClient
import sqlite3
import matplotlib.pyplot as plt
import json
from flask import Flask

app = Flask(__name__)

if __name__ == "__main__":
        app.run()  

fxc = FuncXClient()
@app.route("/home/")
def setSizes():
        connection = sqlite3.connect("logan.sqlite3")
        cursor = connection.cursor()
        rows = cursor.execute("SELECT * FROM awslog").fetchall()
        print(rows[0])
        taskIdSet = set()
        taskGroupIdSet = set()
        endPointIdSet = set()
        functionIdSet = set()
        for x in range(len(rows)):    
                json_object = json.loads(rows[x][0])
                taskIdSet.add(json_object["task_id"])
                taskGroupIdSet.add(json_object["task_group_id"])
                endPointIdSet.add(json_object["endpoint_id"])
                functionIdSet.add(json_object["function_id"])
        print(len(taskIdSet))
        print(len(taskGroupIdSet))
        print(len(endPointIdSet))
        print(len(functionIdSet))
        return "complete"

func_uuid = fxc.register_function(setSizes)

tutorial_endpoint = '4b116d3c-1703-4f8f-9f6f-39921e5864df'
res = fxc.run(function_id=func_uuid, endpoint_id=tutorial_endpoint)

#print(fxc.get_result(res))
