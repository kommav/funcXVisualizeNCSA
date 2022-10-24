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
   
        rows = cursor.execute(sql).fetchall()
        rows2 = cursor.execute(sql2).fetchall()
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
        plt.hist(rows2TimeFormatted, bins=100, histtype='step',cumulative=True)
        plt.gcf().autofmt_xdate()
        plt.title("Cumulative")
        plt.xlabel("Date and Time")
        plt.ylabel("Percentage of Tasks Completed")
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
        ePIy.sort()
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
        plt.pie(ePIy, labels = newEPIx, startangle=90)
        # plt.bar(range(len(ePIx)), ePIy, tick_label=ePIx)
        plt.title("End Point Distribution")
        # plt.legend(loc=2, prop={'size': 6})
        # plt.xlabel("EndPoint ID")
        # plt.ylabel("Number of Tasks Completed")
        plt.savefig("static/images/output_endpointDistribution.png")

        tGIx = list(taskGroupIdTaskCounter.keys())
        tGIy = list(taskGroupIdTaskCounter.values())

        plt.clf()
        plt.bar(range(len(tGIx)), tGIy)
        plt.title("Task Group Distribution")
        plt.xlabel("Task Group ID")
        plt.ylabel("Number of Tasks Completed")
        plt.savefig("static/images/output_taskGroupDistribution.png")

        fx = list(functionIdTaskCounter.keys())
        fy = list(functionIdTaskCounter.values())

        plt.clf()
        plt.bar(range(len(fx)), fy)
        plt.title("Function Distribution")
        plt.xlabel("Function ID")
        plt.ylabel("Number of Tasks Completed")
        plt.savefig("static/images/output_functionDistribution.png")

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

        return render_template("index.html", tIS = tI, tGIS = tGI, ePIS = ePI, fIS = fI, histogram = pic1, cumulative = pic2, eP = pic3, tG = pic4, func = pic5, taskId = taskIdSet, taskGroupId = taskGroupIdSet, endPointId = endPointIdSet, functionId = functionIdSet)

if __name__ == "__main__":
        app.run(host = "0.0.0.0")

