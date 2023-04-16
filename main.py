import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json
from flask import Flask, redirect, url_for, render_template, request
import shutil
import dateutil
import datetime as dt
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
        uuidImage = str(uuid.uuid4())

        test = """
                select distinct json_extract(entry, "$.endpoint_name") from awslog
                order by json_extract(entry, "$.asctime");
        """

        endPoint = """
                select distinct json_extract(entry, "$.endpoint_id"), json_extract(entry, "$.endpoint_name") from awslog
                order by json_extract(entry, "$.asctime");
        """

        testStart = """
                select json_extract(entry, "$.task_id"), json_extract(entry, "$.asctime"), json_extract(entry, "$.message") from awslog
                where json_extract(entry, "$.message") = "execution-start"
                order by json_extract(entry, "$.asctime");
        """

        testEnd = """
                select json_extract(entry, "$.task_id"), json_extract(entry, "$.asctime"), json_extract(entry, "$.message") from awslog
                where json_extract(entry, "$.message") = "execution-end"
                order by json_extract(entry, "$.asctime");
        """

        testQueued = """
                select json_extract(entry, "$.task_id"), json_extract(entry, "$.asctime"), json_extract(entry, "$.message") from awslog
                where json_extract(entry, "$.message") = "waiting-for-launch"
                order by json_extract(entry, "$.asctime");
        """

        sql = """
                select * from awslog where json_extract(entry, "$.task_id") is not null
                order by json_extract(entry, "$.asctime");

        """
        sql2 = """
                select json_extract(entry, "$.asctime") from awslog
                where json_extract(entry, "$.message") = "received"
                and json_extract(entry, "$.task_id") is not null
                order by json_extract(entry, "$.asctime");

        """

        sqlRecent = """
                select * from awslog
                where json_extract(entry, "$.message") = "received"
                and json_extract(entry, "$.task_id") is not null
                order by json_extract(entry, "$.asctime");

        """

        testQuery = cursor.execute(test).fetchall()

        endPointQuery = cursor.execute(endPoint).fetchall()
        print(endPointQuery)
        endPoints_dict = defaultdict(str)
        for result in endPointQuery:
                # print(result[0])
                # # endpoint_id = json.loads(result[0])
                # # endpoint_name = json.loads(result[1])
                endPoints_dict[result[0]] = result[1]
        testMessage = cursor.execute(testStart).fetchall()

        testQueue = cursor.execute(testQueued).fetchall()

        start = defaultdict()

        for x in testMessage:
                start[x[0]] = x[1]

        testMessage2 = cursor.execute(testEnd).fetchall()

        end = defaultdict()

        for y in testMessage2:
                end[y[0]] = y[1]

        queued = defaultdict()

        for z in testQueue:
                queued[z[0]] = z[1]

        runtimes = []
        queuetimes = []

        for x in start.keys():
                timeStart = datetime.strptime(start[x], '%Y-%m-%d %H:%M:%S,%f')
                timeEnd = datetime.strptime(end[x], '%Y-%m-%d %H:%M:%S,%f')
                runtimes.append(timeEnd - timeStart)
                if (x in queued.keys()):
                        timeQueued = datetime.strptime(queued[x], '%Y-%m-%d %H:%M:%S,%f')
                        queuetimes.append(timeStart - timeQueued)

        microseconds = [runtime.microseconds for runtime in runtimes]
        plt.switch_backend('Agg')
        plt.hist(microseconds ,bins=50)
        plt.gcf().autofmt_xdate()
        plt.title("Histogram")
        plt.xlabel("Microseconds")
        plt.ylabel("Tasks Completed")
        plt.savefig("static/images/runtime_histogram" + uuidImage + ".png")
        
        microseconds2 = [queuetime.microseconds for queuetime in queuetimes]
        plt.switch_backend('Agg')
        plt.hist(microseconds2 ,bins=50)
        plt.gcf().autofmt_xdate()
        plt.title("Histogram")
        plt.xlabel("Microseconds")
        plt.ylabel("Tasks Completed")
        plt.savefig("static/images/queuetime_histogram" + uuidImage + ".png")

        rows = cursor.execute(sql).fetchall()
        rows2 = cursor.execute(sql2).fetchall()
        rowsRecent = cursor.execute(sqlRecent).fetchall()

        mostRecentT = 'select distinct json_extract(entry, "$.task_id") from awslog order by json_extract(entry, "$.asctime")'
        mostRecentTasks = cursor.execute(mostRecentT).fetchall();
        mostRecentF = 'select distinct json_extract(entry, "$.function_id") from awslog order by json_extract(entry, "$.asctime")'
        mostRecentFunctions = cursor.execute(mostRecentF).fetchall();
        mostRecentE = 'select distinct json_extract(entry, "$.endpoint_id") from awslog order by json_extract(entry, "$.asctime")'
        mostRecentEnd = cursor.execute(mostRecentE).fetchall();
        mostRecentTG = 'select distinct json_extract(entry, "$.task_group_id") from awslog order by json_extract(entry, "$.asctime")'
        mostRecentTaskGroups = cursor.execute(mostRecentTG).fetchall();
        mostRecentTaskGroups.reverse()

        validity = rows2[len(rows2) - 1]
        validity = str(validity)[2:-10]
        rows2TimeFormatted = []
        for x in range(len(rows2)):
                rows2TimeFormatted.append(datetime.strptime(rows2[x][0], '%Y-%m-%d %H:%M:%S,%f'))

        plt.switch_backend('Agg')
        plt.hist(rows2TimeFormatted,bins=50)
        plt.gcf().autofmt_xdate()
        plt.title("Histogram")
        plt.xlabel("Date")
        plt.ylabel("Tasks Completed")
        plt.savefig("static/images/output_histogram" + uuidImage + ".png")

        plt.switch_backend('Agg')

        # Calculate the date range for the last year
        last_year = datetime.now() - dt.timedelta(days=365)

        # Filter the data based on the date range
        last_year_data = [date for date in rows2TimeFormatted if date >= last_year]

        # Plot the histogram
        plt.hist(last_year_data, bins=50)
        plt.gcf().autofmt_xdate()
        plt.title("Histogram of Last Year's Entries")
        plt.xlabel("Date")
        plt.ylabel("Tasks Completed")
        plt.savefig("static/images/output_histogram_lastYear" + uuidImage + ".png")


        today = dt.date.today()
        last_month = today.replace(day=1) - dt.timedelta(days=1)
        one_month_ago = last_month.replace(day=1) 

        # filter rows2TimeFormatted to include only dates from last month
        last_month_entries = [d for d in rows2TimeFormatted if one_month_ago <= d.date() <= last_month]

        # plot the histogram of last month's entries
        plt.switch_backend('Agg')
        plt.hist(last_month_entries, bins=50)
        plt.gcf().autofmt_xdate()
        plt.title("Histogram of Completed Tasks in Last Month")
        plt.xlabel("Date")
        plt.ylabel("Tasks Completed")
        plt.savefig("static/images/output_histogram_lastMonth" + uuidImage + ".png")

        plt.clf()
        plt.hist(rows2TimeFormatted, bins=100, cumulative=True)
        plt.gcf().autofmt_xdate()
        plt.title("Cumulative")
        plt.xlabel("Date")
        plt.ylabel("Number of Tasks Completed")
        plt.savefig("static/images/output_cumulative" + uuidImage + ".png")

        tI = (len(mostRecentTasks))
        tGI = (len(mostRecentTaskGroups))
        ePI = (len(mostRecentEnd))
        fI = (len(mostRecentFunctions))

        endPointIdTaskCounter = defaultdict(int)
        taskGroupIdTaskCounter = defaultdict(int)
        taskGroupIdTimeStampMap = defaultdict(str)
        functionIdTaskCounter = defaultdict(int)
        
        for x in range(len(rows)):    
                json_object = json.loads(rows[x][0])
                endPointIdTaskCounter[json_object["endpoint_id"]] += 1
                if (taskGroupIdTaskCounter[json_object["task_group_id"]] == 0):
                        # print(json_object["asctime"])
                        taskGroupIdTimeStampMap[json_object["task_group_id"]] = json_object["asctime"]
                        # print(taskGroupIdTimeStampMap[json_object["task_group_id"]])
                taskGroupIdTaskCounter[json_object["task_group_id"]] += 1
                functionIdTaskCounter[json_object["function_id"]] += 1

        ePIx = list(endPointIdTaskCounter.keys())
        ePIy = list(endPointIdTaskCounter.values())

        ePIy.sort(reverse=True)
        newEPIx = []
        remove = ""
        for x in range(len(ePIy)):
                for i in endPointIdTaskCounter:
                        if endPointIdTaskCounter[i] == ePIy[x]:
                                newEPIx.append(i);
                                endPointIdTaskCounter[i] = -1
        for x in range(len(newEPIx)):
                if newEPIx[x] == None:
                        newEPIx.pop(x)
                        ePIy.pop(x)
                        break
        plt.clf()

        newEPIy = ePIy[:7]
        newEPIy.append(sum(ePIy[7:]))
        newEPIx = newEPIx[:7]
        for x in range(len(newEPIx)):
                newEPIx[x] = str(newEPIx[x])
        newEPIx.append("Others")
        plt.pie(newEPIy, labels = newEPIx, startangle=90)
        plt.title("End Point Distribution")
        plt.savefig("static/images/output_endpointDistribution" + uuidImage + ".png")

        tGIx = list(taskGroupIdTaskCounter.keys())
        tGIy = list(taskGroupIdTaskCounter.values())

        tGIy.sort(reverse=True)
        newTGIx = []
        
        remove = ""
        
        tGIC = dict()

        for x in range(len(tGIy)):
                for i in taskGroupIdTaskCounter:
                        if taskGroupIdTaskCounter[i] == tGIy[x]:
                                newTGIx.append(i)
                                taskGroupIdTaskCounter[i] = -1
                                tGIC[i] = tGIy[x]

        for x in tGIC.keys():
                taskGroupIdTaskCounter[x] = tGIC[x]

        for x in range(len(newTGIx)):
                if newTGIx[x] == None or newTGIx == "":
                        newTGIx.pop(x)
                        tGIy.pop(x)
                        break

        plt.clf()
        newTGIy = tGIy[:12]
        newTGIy.append(sum(tGIy[12:]))
        newTGIx = newTGIx[:12]
        #newTGIx get rid of {''}
        for x in range(len(newTGIx)):
                newTGIx[x] = str(newTGIx[x])

        newTGIx.append("Others")
        plt.pie(newTGIy, labels = newTGIx, startangle=90)
        plt.title("Distribution of Most Popular Task Groups")
        plt.savefig("static/images/output_taskGroupDistribution" + uuidImage + ".png")

        fx = list(functionIdTaskCounter.keys())
        fy = list(functionIdTaskCounter.values())
        fy.sort(reverse=True)
        newFx = []

        remove = ""
        for x in range(len(fy)):
                for i in functionIdTaskCounter:
                        if functionIdTaskCounter[i] == fy[x]:
                                newFx.append(i);
                                functionIdTaskCounter[i] = -1
        for x in range(len(newFx)):
                if newFx[x] == None or newFx[x] == "":
                        newFx.pop(x)
                        fy.pop(x)
                        break
        plt.clf()
        newFy = fy[:12]
        newFy.append(sum(fy[12:]))
        newFx = newFx[:12]
        # for x in newFx:
        #         # print(x)
        for x in range(len(newFx)):
                newFx[x] = str(newFx[x])
                #print(newEPIx[x])
        newFx.append("Others")
        plt.pie(newFy, labels = newFx, startangle=90)
        plt.title("Distribution of Most Popular Function IDs")
        plt.savefig("static/images/output_functionDistribution" + uuidImage + ".png")

        pic1 = os.path.join(app.config['UPLOAD FOLDER'], 'output_histogram' + uuidImage + '.png')
        pic2 = os.path.join(app.config['UPLOAD FOLDER'], 'output_cumulative' + uuidImage + '.png')
        pic3 = os.path.join(app.config['UPLOAD FOLDER'], 'output_endpointDistribution' + uuidImage + '.png')
        pic4 = os.path.join(app.config['UPLOAD FOLDER'], 'output_taskGroupDistribution' + uuidImage + '.png')
        pic5 = os.path.join(app.config['UPLOAD FOLDER'], 'output_functionDistribution' + uuidImage + '.png')
        pic6 = os.path.join(app.config['UPLOAD FOLDER'], 'output_histogram_lastYear' + uuidImage + '.png')
        pic7 = os.path.join(app.config['UPLOAD FOLDER'], 'output_histogram_lastMonth' + uuidImage + '.png')
        imageRT = os.path.join(app.config['UPLOAD FOLDER'], 'runtime_histogram' + uuidImage + '.png')
        imageQT = os.path.join(app.config['UPLOAD FOLDER'], 'queuetime_histogram' + uuidImage + '.png')

        # for x in taskGroupIdTimeStampMap.keys():
        #         print(taskGroupIdTimeStampMap[x])
        print(taskGroupIdTimeStampMap.keys())
        # print("here")
        # print(taskGroupIdTimeStampMap['a62fcc67-87a6-4539-a5b4-8c1369c65236'])
        # print("here")
        for x in range(5):
                newTGIx[x] = str(taskGroupIdTaskCounter[newTGIx[x]]) + " tasks at " + taskGroupIdTimeStampMap[newTGIx[x]]
                mostRecentTaskGroups[x] = str(taskGroupIdTaskCounter[mostRecentTaskGroups[x][0]]) + " tasks at " + taskGroupIdTimeStampMap[mostRecentTaskGroups[x][0]]
                mostRecentFunctions[x] = mostRecentFunctions[x][0]
                mostRecentEnd[x] = mostRecentEnd[x][0]
                if (endPoints_dict[newEPIx[x]] != None):
                        newEPIx[x] = endPoints_dict[newEPIx[x]]
                if (endPoints_dict[mostRecentEnd[x]] != None):
                        mostRecentEnd[x] = endPoints_dict[mostRecentEnd[x]]

        return render_template("index.html", time = validity, tIS = tI, tGIS = tGI, ePIS = ePI, fIS = fI, histogram = pic1, cumulative = pic2, eP = pic3, tG = pic4, func = pic5, popTaskGroups = newTGIx, popFuncGroups = newFx, popEndGroups = newEPIx, mRT = mostRecentTaskGroups, mRE = mostRecentEnd, mRF = mostRecentFunctions, picSix = pic6, picSeven = pic7, rt = imageRT, qt = imageQT)

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

        sqlRecent = """
                select * from awslog
                where json_extract(entry, "$.message") = "received"
                and json_extract(entry, "$.task_id") is not null
                and json_extract(entry, "$.user_id") = """ + user + """
                order by json_extract(entry, "$.asctime");
        """

        testUser = """
                select distinct json_extract(entry, "$.endpoint_name") from awslog
                where json_extract(entry, "$.user_id") = """ + user + """
                order by json_extract(entry, "$.asctime");
        """

        testQueryUser = cursor.execute(testUser).fetchall()
        print(testQueryUser)

        sql3 = 'select * from awslog where json_extract(entry, "$.user_id") = ' + user + ' and json_extract(entry, "$.task_id") is not null;'

        sql4 = 'select json_extract(entry, "$.asctime") from awslog where json_extract(entry, "$.message") = "received" and json_extract(entry, "$.task_id") is not null and json_extract(entry, "$.user_id") = ' + user + ' order by json_extract(entry, "$.asctime");'

        uuidUser = str(uuid.uuid4())
        rows = cursor.execute(sql).fetchall()
        rows2 = cursor.execute(sql2).fetchall()
        rowsUser = cursor.execute(sql3).fetchall()
        rows2User = cursor.execute(sql4).fetchall()
        rowsRecent = cursor.execute(sqlRecent).fetchall()
        mostRecentTasks = []
        mostRecentFunctions = []
        mostRecentEnd = []
        for x in range(len(rowsRecent) - 1, -1, -1 ):    
                json_object = json.loads(rowsRecent[x][0])
                if (json_object["task_id"] not in mostRecentTasks):
                        mostRecentTasks.append(json_object["task_id"][0])
                if (json_object["function_id"] not in mostRecentFunctions):
                        mostRecentFunctions.append(json_object["function_id"][0])
                if (json_object["endpoint_id"] not in mostRecentEnd):
                        mostRecentEnd.append(json_object["endpoint_id"][0])
        validity = rows2[len(rows2) - 1]
        validity = str(validity)[2:-10]
        rows2TimeFormatted = []
        for x in range(len(rows2)):
                rows2TimeFormatted.append(datetime.strptime(rows2[x][0], '%Y-%m-%d %H:%M:%S,%f'))

        rows2UserTimeFormatted = []
        for x in range(len(rows2User)):
                rows2UserTimeFormatted.append(datetime.strptime(rows2User[x][0], '%Y-%m-%d %H:%M:%S,%f'))
        plt.switch_backend('Agg')
        plt.hist(rows2UserTimeFormatted,bins=50)
        plt.gcf().autofmt_xdate()
        plt.title("Histogram")
        plt.xlabel("Date")
        plt.ylabel("Tasks Completed")
        plt.savefig("static/images/output_histogram_" + uuidUser + ".png")
        plt.clf()


        plt.switch_backend('Agg')

        # Calculate the date range for the last year
        last_year = datetime.now() - dt.timedelta(days=365)

        # Filter the data based on the date range
        last_year_data = [date for date in rows2UserTimeFormatted if date >= last_year]

        # Plot the histogram
        plt.hist(last_year_data, bins=50)
        plt.gcf().autofmt_xdate()
        plt.title("Histogram of Last Year's Entries")
        plt.xlabel("Date")
        plt.ylabel("Tasks Completed")
        plt.savefig("static/images/output_histogram_lastYear" + uuidUser + ".png")


        today = dt.date.today()
        last_month = today.replace(day=1) - dt.timedelta(days=1)
        one_month_ago = last_month.replace(day=1) 

        # filter rows2TimeFormatted to include only dates from last month
        last_month_entries = [d for d in rows2UserTimeFormatted if one_month_ago <= d.date() <= last_month]

        # plot the histogram of last month's entries
        plt.switch_backend('Agg')
        plt.hist(last_month_entries, bins=50)
        plt.gcf().autofmt_xdate()
        plt.title("Histogram of Completed Tasks in Last Month")
        plt.xlabel("Date")
        plt.ylabel("Tasks Completed")
        plt.savefig("static/images/output_histogram_lastMonth" + uuidUser + ".png")

        plt.hist(rows2UserTimeFormatted, bins=100, cumulative=True)
        plt.gcf().autofmt_xdate()
        plt.title("Cumulative")
        plt.xlabel("Date")
        plt.ylabel("Number of Tasks Completed")
        plt.savefig("static/images/output_cumulative_" + uuidUser + ".png")

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
                for i in userEndPointIdTaskCounter:
                        if userEndPointIdTaskCounter[i] == uEPIy[x]:
                                newUEPIx.append(i);
                                userEndPointIdTaskCounter[i] = -1

        for x in range(len(newUEPIx)):
                if newUEPIx[x] == None:
                        newUEPIx.pop(x)
                        uEPIy.pop(x)
                        break
        plt.clf()
        newUEPIy = uEPIy[:7]
        newUEPIy.append(sum(uEPIy[7:]))
        newUEPIx = newUEPIx[:7]
        #newUEPIX get rid of {''}
        for x in range(len(newUEPIx)):
                newUEPIx[x] = str(newUEPIx[x])
                #print(newEPIx[x])
        newUEPIx.append("Others")
        plt.pie(newUEPIy, labels = newUEPIx, startangle=90)
        plt.title("End Point Distribution")
        plt.savefig("static/images/output_endpointDistribution_" + uuidUser + ".png")

        uTGIx = list(userTaskGroupIdTaskCounter.keys())
        uTGIy = list(userTaskGroupIdTaskCounter.values())

        uTGIy.sort(reverse=True)
        newUTGIx = []

        remove = ""

        for x in range(len(uTGIy)):
                for i in userTaskGroupIdTaskCounter:
                        if userTaskGroupIdTaskCounter[i] == uTGIy[x]:
                                newUTGIx.append(i);
                                userTaskGroupIdTaskCounter[i] = -1

        for x in range(len(newUTGIx)):
                if newUTGIx[x] == None:
                        newUTGIx.pop(x)
                        uTGIy.pop(x)
                        break
        plt.clf()
        newUTGIy = uTGIy[:12]
        newUTGIy.append(sum(uTGIy[12:]))
        newUTGIx = newUTGIx[:12]
        #newUTGIx get rid of {''}
        for x in range(len(newUTGIx)):
                newUTGIx[x] = str(newUTGIx[x])
                #print(newEPIx[x])
        newUTGIx.append("Others")
        plt.pie(newUTGIy, labels = newUTGIx, startangle=90)
        plt.title("Distribution of Most Popular Task Groups")
        plt.savefig("static/images/output_taskGroupDistribution_" + uuidUser + ".png")

        ufx = list(userFunctionIdTaskCounter.keys())
        ufy = list(userFunctionIdTaskCounter.values())
        ufy.sort(reverse=True)
        newUFx = []

        remove = ""
        
        for x in range(len(ufy)):
                for i in userFunctionIdTaskCounter:
                        if userFunctionIdTaskCounter[i] == ufy[x]:
                                newUFx.append(i);
                                userFunctionIdTaskCounter[i] = -1

        for x in range(len(newUFx)):
                if newUFx[x] == None:
                        newUFx.pop(x)
                        ufy.pop(x)
                        break
        plt.clf()
        newUFy = ufy[:12]
        newUFy.append(sum(ufy[12:]))
        newUFx = newUFx[:12]
        #newUFx get rid of {''}
        for x in range(len(newUFx)):
                newUFx[x] = str(newUFx[x])
                #print(newEPIx[x])
        newUFx.append("Others")
        plt.pie(newUFy, labels = newUFx, startangle=90)
        plt.title("Distribution of Most Popular Function IDs")
        plt.savefig("static/images/output_functionDistribution_" + uuidUser + ".png")

        pic6 = os.path.join(app.config['UPLOAD FOLDER'], 'output_histogram_' + uuidUser + '.png')
        pic7 = os.path.join(app.config['UPLOAD FOLDER'], 'output_cumulative_' + uuidUser + '.png')
        pic8 = os.path.join(app.config['UPLOAD FOLDER'], 'output_endpointDistribution_' + uuidUser + '.png')
        pic9 = os.path.join(app.config['UPLOAD FOLDER'], 'output_taskGroupDistribution_' + uuidUser + '.png')
        pic10 = os.path.join(app.config['UPLOAD FOLDER'], 'output_functionDistribution_' + uuidUser + '.png')
        pic11 = os.path.join(app.config['UPLOAD FOLDER'], 'output_histogram_lastYear' + uuidUser + '.png')
        pic12 = os.path.join(app.config['UPLOAD FOLDER'], 'output_histogram_lastMonth' + uuidUser + '.png')

        return render_template("userInfo.html", time = validity, tIUS = tIU, tGIUS = tGIU, ePIUS = ePIU, fIUS = fIU, picSix = pic6, picSeven = pic7, picEight = pic8, picNine = pic9, picTen = pic10, popTaskGroupsUser = newUTGIx, popFuncGroupsUser = newUFx, popEndUser = newUFx, mRT = mostRecentTasks, mRE = mostRecentEnd, mRF = mostRecentFunctions, picEleven = pic11, picTwelve = pic12, popNameUser = testQueryUser)

if __name__ == "__main__":
        app.run(host = "0.0.0.0")

