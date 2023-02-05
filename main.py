import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json
from flask import Flask, redirect, url_for, render_template, request
import shutil
import dateutil
from datetime import datetime
import os
from collections import defaultdict
import uuid

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

        sqlTest = """
                select * from awslog
                where json_extract(entry, "$.message") = "received"
                and json_extract(entry, "$.task_id") is not null
                order by json_extract(entry, "$.asctime");

        """

        # sql3 = 'select * from awslog where json_extract(entry, "$.user_id") = ' + user + ' and json_extract(entry, "$.task_id") is not null;'

        # sql4 = 'select json_extract(entry, "$.asctime") from awslog where json_extract(entry, "$.message") = "received" and json_extract(entry, "$.task_id") is not null and json_extract(entry, "$.user_id") = ' + user + ' order by json_extract(entry, "$.asctime");'

        rows = cursor.execute(sql).fetchall()
        rows2 = cursor.execute(sql2).fetchall()
        # rows3 = cursor.execute(sql3).fetchall()
        # rows4 = cursor.execute(sql4).fetchall()
        validity = rows2[len(rows2) - 1]
        validity = str(validity)[2:-10]
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


        # taskIdSetUser = set()
        # taskGroupIdSetUser = set()
        # endPointIdSetUser = set()
        # functionIdSetUser = set()
        # for x in range(len(rows3)):    
        #         json_object = json.loads(rows3[x][0])
        #         taskIdSetUser.add(json_object["task_id"])
        #         taskGroupIdSetUser.add(json_object["task_group_id"])
        #         endPointIdSetUser.add(json_object["endpoint_id"])
        #         functionIdSetUser.add(json_object["function_id"])
        # tIU = (len(taskIdSetUser))
        # tGIU = (len(taskGroupIdSetUser))
        # ePIU = (len(endPointIdSetUser))
        # fIU = (len(functionIdSetUser))


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
        for x in range(len(newEPIx)):
                newEPIx[x] = str(newEPIx[x])[2:-2]
                #print(newEPIx[x])
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
        newTGIy = tGIy[:12]
        newTGIy.append(sum(tGIy[12:]))
        newTGIx = newTGIx[:12]
        #newTGIx get rid of {''}
        for x in range(len(newTGIx)):
                newTGIx[x] = str(newTGIx[x])[2:-2]
                #print(newEPIx[x])
        newTGIx.append("Others")
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
        newFy = fy[:12]
        newFy.append(sum(fy[12:]))
        newFx = newFx[:12]
        #newfx get rid of {''}
        for x in range(len(newFx)):
                newFx[x] = str(newFx[x])[2:-2]
                #print(newEPIx[x])
        newFx.append("Others")
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

        return render_template("index.html", time = validity, tIS = tI, tGIS = tGI, ePIS = ePI, fIS = fI, histogram = pic1, cumulative = pic2, eP = pic3, tG = pic4, func = pic5, taskId = taskIdSet, taskGroupId = taskGroupIdSet, endPointId = endPointIdSet, functionId = functionIdSet, popTaskGroups = newTGIx, popFuncGroups = newFx)

#start here


@app.route("/", methods=['POST'])
def createUserInfo():
        user = request.form['userID']
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

        uuidUser = str(uuid.uuid4())
        rows = cursor.execute(sql).fetchall()
        rows2 = cursor.execute(sql2).fetchall()
        rowsUser = cursor.execute(sql3).fetchall()
        rows2User = cursor.execute(sql4).fetchall()
        validity = rows2[len(rows2) - 1]
        validity = str(validity)[2:-10]
        rows2TimeFormatted = []
        for x in range(len(rows2)):
                rows2TimeFormatted.append(datetime.strptime(rows2[x][0], '%Y-%m-%d %H:%M:%S,%f'))
        # plt.switch_backend('Agg')
        # plt.hist(rows2TimeFormatted,bins=50)
        # plt.gcf().autofmt_xdate()
        # plt.title("Histogram")
        # plt.xlabel("Date and Time")
        # plt.ylabel("Tasks Completed")
        # plt.savefig("static/images/output_histogram.png")
        # plt.clf()

#user graph1

        rows2UserTimeFormatted = []
        for x in range(len(rows2User)):
                rows2UserTimeFormatted.append(datetime.strptime(rows2User[x][0], '%Y-%m-%d %H:%M:%S,%f'))
        plt.switch_backend('Agg')
        plt.hist(rows2UserTimeFormatted,bins=50)
        plt.gcf().autofmt_xdate()
        plt.title("Histogram")
        plt.xlabel("Date and Time")
        plt.ylabel("Tasks Completed")
        plt.savefig("static/images/output_histogram_" + uuidUser + ".png")
        plt.clf()

        # plt.hist(rows2TimeFormatted, bins=100, cumulative=True)
        # plt.gcf().autofmt_xdate()
        # plt.title("Cumulative")
        # plt.xlabel("Date and Time")
        # plt.ylabel("Number of Tasks Completed")
        # plt.savefig("static/images/output_cumulative.png")
        # plt.clf()

#user graph2

        plt.hist(rows2UserTimeFormatted, bins=100, cumulative=True)
        plt.gcf().autofmt_xdate()
        plt.title("Cumulative")
        plt.xlabel("Date and Time")
        plt.ylabel("Number of Tasks Completed")
        plt.savefig("static/images/output_cumulative_" + uuidUser + ".png")

        # taskIdSet = set()
        # taskGroupIdSet = set()
        # endPointIdSet = set()
        # functionIdSet = set()
        # for x in range(len(rows)):    
        #         json_object = json.loads(rows[x][0])
        #         taskIdSet.add(json_object["task_id"])
        #         taskGroupIdSet.add(json_object["task_group_id"])
        #         endPointIdSet.add(json_object["endpoint_id"])
        #         functionIdSet.add(json_object["function_id"])
        # tI = (len(taskIdSet))
        # tGI = (len(taskGroupIdSet))
        # ePI = (len(endPointIdSet))
        # fI = (len(functionIdSet))

        taskIdSetUser = set()
        taskGroupIdSetUser = set()
        endPointIdSetUser = set()
        functionIdSetUser = set()
        for x in range(len(rowsUser)):    
                json_object = json.loads(rowsUser[x][0])
                taskIdSetUser.add(json_object["task_id"])
                taskGroupIdSetUser.add(json_object["task_group_id"])
                endPointIdSetUser.add(json_object["endpoint_id"])
                functionIdSetUser.add(json_object["function_id"])
        tIU = (len(taskIdSetUser))
        tGIU = (len(taskGroupIdSetUser))
        ePIU = (len(endPointIdSetUser))
        fIU = (len(functionIdSetUser))


        # endPointIdTaskCounter = defaultdict(int)
        # taskGroupIdTaskCounter = defaultdict(int)
        # functionIdTaskCounter = defaultdict(int)
        
        # for x in range(len(rows)):    
        #         json_object = json.loads(rows[x][0])
        #         endPointIdTaskCounter[json_object["endpoint_id"]] += 1
        #         taskGroupIdTaskCounter[json_object["task_group_id"]] += 1
        #         functionIdTaskCounter[json_object["function_id"]] += 1
                

        # ePIx = list(endPointIdTaskCounter.keys())
        # ePIy = list(endPointIdTaskCounter.values())
        # ePIy.sort(reverse=True)
        # newEPIx = []
        # remove = ""
        # for x in range(len(ePIy)):
        #         newEPIx.append({i for i in endPointIdTaskCounter if endPointIdTaskCounter[i]== ePIy[x]})
        # for x in range(len(newEPIx)):
        #         if newEPIx[x] == {None}:
        #                 newEPIx.pop(x)
        #                 ePIy.pop(x)
        #                 break
        # plt.clf()
        # newEPIy = ePIy[:7]
        # newEPIy.append(sum(ePIy[7:]))
        # newEPIx = newEPIx[:7]
        # for x in range(len(newEPIx)):
        #         newEPIx[x] = str(newEPIx[x])[2:-2]
        #         #print(newEPIx[x])
        # newEPIx.append("Others")
        # plt.pie(newEPIy, labels = newEPIx, startangle=90)
        # plt.title("End Point Distribution")
        # plt.savefig("static/images/output_endpointDistribution.png")


#user graph3

        userEndPointIdTaskCounter = defaultdict(int)
        userTaskGroupIdTaskCounter = defaultdict(int)
        userFunctionIdTaskCounter = defaultdict(int)
        
        for x in range(len(rowsUser)):    
                json_object = json.loads(rowsUser[x][0])
                userEndPointIdTaskCounter[json_object["endpoint_id"]] += 1
                userTaskGroupIdTaskCounter[json_object["task_group_id"]] += 1
                userFunctionIdTaskCounter[json_object["function_id"]] += 1
                

        uEPIx = list(userEndPointIdTaskCounter.keys())
        uEPIy = list(userEndPointIdTaskCounter.values())
        uEPIy.sort(reverse=True)
        newUEPIx = []
        remove = ""
        for x in range(len(uEPIy)):
                newUEPIx.append({i for i in userEndPointIdTaskCounter if userEndPointIdTaskCounter[i]== uEPIy[x]})
        for x in range(len(newUEPIx)):
                if newUEPIx[x] == {None}:
                        newUEPIx.pop(x)
                        uEPIy.pop(x)
                        break
        plt.clf()
        newUEPIy = uEPIy[:7]
        newUEPIy.append(sum(uEPIy[7:]))
        newUEPIx = newUEPIx[:7]
        #newUEPIX get rid of {''}
        for x in range(len(newUEPIx)):
                newUEPIx[x] = str(newUEPIx[x])[2:-2]
                #print(newEPIx[x])
        newUEPIx.append("Others")
        plt.pie(newUEPIy, labels = newUEPIx, startangle=90)
        plt.title("End Point Distribution")
        plt.savefig("static/images/output_endpointDistribution_" + uuidUser + ".png")

        # tGIx = list(taskGroupIdTaskCounter.keys())
        # tGIy = list(taskGroupIdTaskCounter.values())

        # tGIy.sort(reverse=True)
        # newTGIx = []

        # remove = ""
        # for x in range(len(tGIy)):
        #         newTGIx.append({i for i in taskGroupIdTaskCounter if taskGroupIdTaskCounter[i]== tGIy[x]})
        # for x in range(len(newTGIx)):
        #         if newTGIx[x] == {None}:
        #                 newTGIx.pop(x)
        #                 tGIy.pop(x)
        #                 break
        # plt.clf()
        # newTGIy = tGIy[:12]
        # newTGIy.append(sum(tGIy[12:]))
        # newTGIx = newTGIx[:12]
        # for x in range(len(newTGIx)):
        #         newTGIx[x] = str(newTGIx[x])[2:-2]
        #         #print(newEPIx[x])
        # newTGIx.append("Others")
        # plt.pie(newTGIy, labels = newTGIx, startangle=90)
        # plt.title("Distribution of Most Popular Task Groups")
        # plt.savefig("static/images/output_taskGroupDistribution.png")

#user graph4

        uTGIx = list(userTaskGroupIdTaskCounter.keys())
        uTGIy = list(userTaskGroupIdTaskCounter.values())

        uTGIy.sort(reverse=True)
        newUTGIx = []

        remove = ""
        for x in range(len(uTGIy)):
                newUTGIx.append({i for i in userTaskGroupIdTaskCounter if userTaskGroupIdTaskCounter[i]== uTGIy[x]})
        for x in range(len(newUTGIx)):
                if newUTGIx[x] == {None}:
                        newUTGIx.pop(x)
                        uTGIy.pop(x)
                        break
        plt.clf()
        newUTGIy = uTGIy[:12]
        newUTGIy.append(sum(uTGIy[12:]))
        newUTGIx = newUTGIx[:12]
        #newUTGIx get rid of {''}
        for x in range(len(newUTGIx)):
                newUTGIx[x] = str(newUTGIx[x])[2:-2]
                #print(newEPIx[x])
        newUTGIx.append("Others")
        plt.pie(newUTGIy, labels = newUTGIx, startangle=90)
        plt.title("Distribution of Most Popular Task Groups")
        plt.savefig("static/images/output_taskGroupDistribution_" + uuidUser + ".png")

        # plt.clf()
        # plt.bar(range(len(tGIx)), tGIy)
        # plt.title("Task Group Distribution")
        # plt.xlabel("Task Group ID")
        # plt.ylabel("Number of Tasks Completed")
        # plt.savefig("static/images/output_taskGroupDistribution.png")

        # fx = list(functionIdTaskCounter.keys())
        # fy = list(functionIdTaskCounter.values())
        # fy.sort(reverse=True)
        # newFx = []

        # remove = ""
        # for x in range(len(fy)):
        #         newFx.append({i for i in functionIdTaskCounter if functionIdTaskCounter[i]== fy[x]})
        # for x in range(len(newFx)):
        #         if newFx[x] == {None}:
        #                 newFx.pop(x)
        #                 fy.pop(x)
        #                 break
        # plt.clf()
        # newFy = fy[:12]
        # newFy.append(sum(fy[12:]))
        # newFx = newFx[:12]
        # for x in range(len(newFx)):
        #         newFx[x] = str(newFx[x])[2:-2]
        #         #print(newEPIx[x])
        # newFx.append("Others")
        # plt.pie(newFy, labels = newFx, startangle=90)
        # plt.title("Distribution of Most Popular Function IDs")
        # plt.savefig("static/images/output_functionDistribution.png")

#user graph5

        ufx = list(userFunctionIdTaskCounter.keys())
        ufy = list(userFunctionIdTaskCounter.values())
        ufy.sort(reverse=True)
        newUFx = []

        remove = ""
        for x in range(len(ufy)):
                newUFx.append({i for i in userFunctionIdTaskCounter if userFunctionIdTaskCounter[i]== ufy[x]})
        for x in range(len(newUFx)):
                if newUFx[x] == {None}:
                        newUFx.pop(x)
                        ufy.pop(x)
                        break
        plt.clf()
        newUFy = ufy[:12]
        newUFy.append(sum(ufy[12:]))
        newUFx = newUFx[:12]
        #newUFx get rid of {''}
        for x in range(len(newUFx)):
                newUFx[x] = str(newUFx[x])[2:-2]
                #print(newEPIx[x])
        newUFx.append("Others")
        plt.pie(newUFy, labels = newUFx, startangle=90)
        plt.title("Distribution of Most Popular Function IDs")
        plt.savefig("static/images/output_functionDistribution_" + uuidUser + ".png")

        # plt.clf()
        # plt.bar(range(len(fx)), fy)
        # plt.title("Function Distribution")
        # plt.xlabel("Function ID")
        # plt.ylabel("Number of Tasks Completed")
        # plt.savefig("static/images/output_functionDistribution.png")

        # pic1 = os.path.join(app.config['UPLOAD FOLDER'], 'output_histogram.png')
        # pic2 = os.path.join(app.config['UPLOAD FOLDER'], 'output_cumulative.png')
        # pic3 = os.path.join(app.config['UPLOAD FOLDER'], 'output_endpointDistribution.png')
        # pic4 = os.path.join(app.config['UPLOAD FOLDER'], 'output_taskGroupDistribution.png')
        # pic5 = os.path.join(app.config['UPLOAD FOLDER'], 'output_functionDistribution.png')

        pic6 = os.path.join(app.config['UPLOAD FOLDER'], 'output_histogram_' + uuidUser + '.png')
        pic7 = os.path.join(app.config['UPLOAD FOLDER'], 'output_cumulative_' + uuidUser + '.png')
        pic8 = os.path.join(app.config['UPLOAD FOLDER'], 'output_endpointDistribution_' + uuidUser + '.png')
        pic9 = os.path.join(app.config['UPLOAD FOLDER'], 'output_taskGroupDistribution_' + uuidUser + '.png')
        pic10 = os.path.join(app.config['UPLOAD FOLDER'], 'output_functionDistribution_' + uuidUser + '.png')
        
        # outTask = open("taskGroupId.txt", "w")
        # for line in taskGroupIdSet:
        #         if line == None:
        #                 continue
        #         outTask.write(line)
        #         outTask.write("\n")
        # outTask.close()

        # outFunc = open("functionId.txt", "w")
        # for line in functionIdSet:
        #         if line == None:
        #                 continue
        #         outFunc.write(line)
        #         outFunc.write("\n")
        # outFunc.close()

        # outEnd = open("endPointId.txt", "w")
        # for line in endPointIdSet:
        #         if line == None:
        #                 continue
        #         outEnd.write(line)
        #         outEnd.write("\n")
        # outEnd.close()

        return render_template("userInfo.html", time = validity, tIUS = tIU, tGIUS = tGIU, ePIUS = ePIU, fIUS = fIU, picSix = pic6, picSeven = pic7, picEight = pic8, picNine = pic9, picTen = pic10, popTaskGroupsUser = newUTGIx, popFuncGroupsUser = newUFx)

if __name__ == "__main__":
        app.run(host = "0.0.0.0")

