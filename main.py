import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json
from flask import Flask, redirect, url_for, render_template
import shutil
import dateutil
from datetime import datetime
import os
from collections import defaultdict

app = Flask(__name__)

picFolder = os.path.join('static', 'images')
exportFolder = os.path.join('static', 'exports')

app.config['UPLOAD FOLDER'] = picFolder

@app.route("/")
def setSizes():
        user = input("Please Input Your User ID: ")
        connection = sqlite3.connect("funcx.sqlite3")
        cursor = connection.cursor()
        sql = """
                select * from awslog where json_extract(entry, "$.task_id") is not null;

        """
        sql2 = """
                select json_extract(entry, "$.asctime") from awslog
                where json_extract(entry, "$.message") = "received"
                and json_extract(entry, "$.task_id") is not null
                order by json_extract(entry, "$.asctime");

        """

        sqlTest = """
                select * from awslog
                where json_extract(entry, "$.message") = "received"
                and json_extract(entry, "$.task_id") is not null
                order by json_extract(entry, "$.asctime");

        """

        sql3 = 'select * from awslog where json_extract(entry, "$.user_id") = ' + user + ' and json_extract(entry, "$.task_id") is not null;'

        sql4 = 'select json_extract(entry, "$.asctime") from awslog where json_extract(entry, "$.message") = "received" and json_extract(entry, "$.task_id") is not null and json_extract(entry, "$.user_id") = ' + user + ' order by json_extract(entry, "$.asctime");'

        rows = cursor.execute(sql).fetchall()
        rows2 = cursor.execute(sql2).fetchall()
        rows3 = cursor.execute(sql3).fetchall()
        rows4 = cursor.execute(sql4).fetchall()
        print(rows2[0])
        print(rows4[0])
        rows2TimeFormatted = []
        for x in range(len(rows2)):
                rows2TimeFormatted.append(datetime.strptime(rows2[x][0], '%Y-%m-%d %H:%M:%S,%f'))
        plt.switch_backend('Agg')
        plt.hist(rows2TimeFormatted,bins=50)
        plt.gcf().autofmt_xdate()
        plt.title("Histogram")
        plt.xlabel("Date and Time")
        plt.ylabel("Tasks Completed")
        plt.savefig("static/images/output_histogram.png")
        plt.clf()
        plt.hist(rows2TimeFormatted, bins=100, cumulative=True)
        plt.gcf().autofmt_xdate()
        plt.title("Cumulative")
        plt.xlabel("Date and Time")
        plt.ylabel("Number of Tasks Completed")
        plt.savefig("static/images/output_cumulative.png")
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
        tI = (len(taskIdSet))
        tGI = (len(taskGroupIdSet))
        ePI = (len(endPointIdSet))
        fI = (len(functionIdSet))


        taskIdSetUser = set()
        taskGroupIdSetUser = set()
        endPointIdSetUser = set()
        functionIdSetUser = set()
        for x in range(len(rows3)):    
                json_object = json.loads(rows3[x][0])
                taskIdSetUser.add(json_object["task_id"])
                taskGroupIdSetUser.add(json_object["task_group_id"])
                endPointIdSetUser.add(json_object["endpoint_id"])
                functionIdSetUser.add(json_object["function_id"])
        tIU = (len(taskIdSetUser))
        tGIU = (len(taskGroupIdSetUser))
        ePIU = (len(endPointIdSetUser))
        fIU = (len(functionIdSetUser))


        endPointIdTaskCounter = defaultdict(int)
        taskGroupIdTaskCounter = defaultdict(int)
        functionIdTaskCounter = defaultdict(int)
        
        for x in range(len(rows)):    
                json_object = json.loads(rows[x][0])
                endPointIdTaskCounter[json_object["endpoint_id"]] += 1
                taskGroupIdTaskCounter[json_object["task_group_id"]] += 1
                functionIdTaskCounter[json_object["function_id"]] += 1
                

        ePIx = list(endPointIdTaskCounter.keys())
        ePIy = list(endPointIdTaskCounter.values())
        ePIy.sort(reverse=True)
        newEPIx = []
        remove = ""
        for x in range(len(ePIy)):
                newEPIx.append({i for i in endPointIdTaskCounter if endPointIdTaskCounter[i]== ePIy[x]})
        for x in range(len(newEPIx)):
                if newEPIx[x] == {None}:
                        newEPIx.pop(x)
                        ePIy.pop(x)
                        break
        plt.clf()
        newEPIy = ePIy[:7]
        newEPIy.append(sum(ePIy[7:]))
        newEPIx = newEPIx[:7]
        newEPIx.append("Others")
        plt.pie(newEPIy, labels = newEPIx, startangle=90)
        plt.title("End Point Distribution")
        plt.savefig("static/images/output_endpointDistribution.png")

        tGIx = list(taskGroupIdTaskCounter.keys())
        tGIy = list(taskGroupIdTaskCounter.values())

        tGIy.sort(reverse=True)
        newTGIx = []

        remove = ""
        for x in range(len(tGIy)):
                newTGIx.append({i for i in taskGroupIdTaskCounter if taskGroupIdTaskCounter[i]== tGIy[x]})
        for x in range(len(newTGIx)):
                if newTGIx[x] == {None}:
                        newTGIx.pop(x)
                        tGIy.pop(x)
                        break
        plt.clf()
        newTGIy = tGIy[:7]
        newTGIx = newTGIx[:7]
        plt.pie(newTGIy, labels = newTGIx, startangle=90)
        plt.title("Distribution of Most Popular Task Groups")
        plt.savefig("static/images/output_taskGroupDistribution.png")

        # plt.clf()
        # plt.bar(range(len(tGIx)), tGIy)
        # plt.title("Task Group Distribution")
        # plt.xlabel("Task Group ID")
        # plt.ylabel("Number of Tasks Completed")
        # plt.savefig("static/images/output_taskGroupDistribution.png")

        fx = list(functionIdTaskCounter.keys())
        fy = list(functionIdTaskCounter.values())
        fy.sort(reverse=True)
        newFx = []

        remove = ""
        for x in range(len(fy)):
                newFx.append({i for i in functionIdTaskCounter if functionIdTaskCounter[i]== fy[x]})
        for x in range(len(newFx)):
                if newFx[x] == {None}:
                        newFx.pop(x)
                        fy.pop(x)
                        break
        plt.clf()
        newFy = fy[:7]
        newFx = newFx[:7]
        plt.pie(newFy, labels = newFx, startangle=90)
        plt.title("Distribution of Most Popular Function IDs")
        plt.savefig("static/images/output_functionDistribution.png")

        # plt.clf()
        # plt.bar(range(len(fx)), fy)
        # plt.title("Function Distribution")
        # plt.xlabel("Function ID")
        # plt.ylabel("Number of Tasks Completed")
        # plt.savefig("static/images/output_functionDistribution.png")

        pic1 = os.path.join(app.config['UPLOAD FOLDER'], 'output_histogram.png')
        pic2 = os.path.join(app.config['UPLOAD FOLDER'], 'output_cumulative.png')
        pic3 = os.path.join(app.config['UPLOAD FOLDER'], 'output_endpointDistribution.png')
        pic4 = os.path.join(app.config['UPLOAD FOLDER'], 'output_taskGroupDistribution.png')
        pic5 = os.path.join(app.config['UPLOAD FOLDER'], 'output_functionDistribution.png')
        
        outTask = open("taskGroupId.txt", "w")
        for line in taskGroupIdSet:
                if line == None:
                        continue
                outTask.write(line)
                outTask.write("\n")
        outTask.close()

        outFunc = open("functionId.txt", "w")
        for line in functionIdSet:
                if line == None:
                        continue
                outFunc.write(line)
                outFunc.write("\n")
        outFunc.close()

        outEnd = open("endPointId.txt", "w")
        for line in endPointIdSet:
                if line == None:
                        continue
                outEnd.write(line)
                outEnd.write("\n")
        outEnd.close()

        return render_template("index.html", tIS = tI, tIUS = tIU, tGIS = tGI, tGIUS = tGIU, ePIS = ePI, ePIUS = ePIU, fIS = fI, fIUS = fIU, histogram = pic1, cumulative = pic2, eP = pic3, tG = pic4, func = pic5, taskId = taskIdSet, taskGroupId = taskGroupIdSet, endPointId = endPointIdSet, functionId = functionIdSet)

if __name__ == "__main__":
        app.run(host = "0.0.0.0")

