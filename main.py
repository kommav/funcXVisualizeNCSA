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
import parsl
from parsl import python_app, ThreadPoolExecutor
# from parsl.configs.local_threads import config
import concurrent.futures

# Set up Parsl ThreadPoolExecutor
from parsl.config import Config
from parsl.executors.threads import ThreadPoolExecutor

config = Config(executors=[ThreadPoolExecutor(max_threads=8)])

parsl.load(config)
parsl.set_stream_logger()
# workers = ThreadPoolExecutor(max_threads=8)

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
                select distinct json_extract(entry, "$.endpoint_id") from awslog
                order by json_extract(entry, "$.asctime");
        """

        test_new = """
                select distinct endpoint_uuid from new_awslog2 order by asctime;
        """

        endPoint = """
                select distinct json_extract(entry, "$.endpoint_uuid"), json_extract(entry, "$.endpoint_name") from awslog
                order by json_extract(entry, "$.asctime");
        """

        endPoint_new = """
                select distinct endpoint_id, endpoint_name from new_awslog3;
        """

        testStart = """
                select json_extract(entry, "$.task_uuid"), json_extract(entry, "$.asctime"), json_extract(entry, "$.message") from awslog
                where json_extract(entry, "$.message") = "execution-start"
                order by json_extract(entry, "$.asctime");
        """

        testStart_new = """
                select task_uuid, asctime, message from new_awslog2
                where message = "execution-start"
                order by asctime;
        """

        testEnd = """
                select json_extract(entry, "$.task_uuid"), json_extract(entry, "$.asctime"), json_extract(entry, "$.message") from awslog
                where json_extract(entry, "$.message") = "execution-end"
                order by json_extract(entry, "$.asctime");
        """

        testEnd_new = """
                select task_uuid, asctime, message from new_awslog2
                where message = "execution-end"
                order by asctime;
        """

        testQueued = """
                select json_extract(entry, "$.task_uuid"), json_extract(entry, "$.asctime"), json_extract(entry, "$.message") from awslog
                where json_extract(entry, "$.message") = "waiting-for-launch"
                order by json_extract(entry, "$.asctime");
        """

        testQueued_new = """
                select task_uuid, asctime, message from new_awslog2
                where message = "waiting-for-launch"
                order by asctime;
        """

        sql = """
                select * from awslog where json_extract(entry, "$.task_uuid") is not null
                and json_extract(entry, "$.task_group_uuid") is not null
                and json_extract(entry, "$.function_uuid") is not null
                and json_extract(entry, "$.endpoint_uuid") is not null
                order by json_extract(entry, "$.asctime");

        """

        sql_new = """
                select * from new_awslog2 where task_uuid is not null
                and task_group_uuid is not null
                and function_uuid is not null
                and endpoint_uuid is not null
                order by asctime;

        """

        sql2 = """
                select json_extract(entry, "$.asctime"), json_extract(entry, "$.user_id") from awslog
                where json_extract(entry, "$.message") = "received"
                and json_extract(entry, "$.task_uuid") is not null
                order by json_extract(entry, "$.asctime");

        """

        sql2_new = """
                select asctime, user_id from new_awslog2
                where message = "received"
                and task_uuid is not null
                order by asctime;

        """

        sqlRecent = """
                select * from awslog
                where json_extract(entry, "$.message") = "received"
                and json_extract(entry, "$.task_uuid") is not null
                order by json_extract(entry, "$.asctime");

        """

        sqlRecent_new = """
                select * from new_awslog2
                where message = "received"
                and task_uuid is not null
                order by asctime;

        """

        mostRecentT = 'select distinct json_extract(entry, "$.task_uuid") from awslog order by json_extract(entry, "$.asctime")'

        mostRecentT_new = 'select distinct task_uuid from new_awslog2 order by asctime'

        mostRecentF = 'select distinct json_extract(entry, "$.function_uuid") from awslog order by json_extract(entry, "$.asctime")'

        mostRecentF_new = 'select distinct function_uuid from new_awslog2 order by asctime'

        mostRecentE = 'select distinct json_extract(entry, "$.endpoint_uuid") from awslog order by json_extract(entry, "$.asctime")'

        mostRecentE_new = 'select distinct endpoint_uuid from new_awslog2 order by asctime'

        mostRecentTG = 'select distinct json_extract(entry, "$.task_group_uuid") from awslog order by json_extract(entry, "$.asctime")'

        mostRecentTG_new = 'select distinct task_group_uuid from new_awslog2 order by asctime'

        query_endpoint_uuid = """
                SELECT endpoint_uuid, COUNT(*) AS frequency
                FROM new_awslog2
                GROUP BY endpoint_uuid
                ORDER BY asctime;
        """

        query_task_group_uuid = """
                SELECT task_group_uuid, COUNT(*) AS frequency
                FROM new_awslog2
                GROUP BY task_group_uuid
                ORDER BY asctime;
        """

        query_function_uuid = """
                SELECT function_uuid, COUNT(*) AS frequency
                FROM new_awslog2
                GROUP BY function_uuid
                ORDER BY asctime;
        """

        query_user_id = """
                SELECT user_id, COUNT(*) AS frequency
                FROM new_awslog2
                GROUP BY user_id
                ORDER BY asctime;
        """

        # @python_app(executors=["workers"])
        # def execute_query(query):
        #         conn = sqlite3.connect("funcx.sqlite3")
        #         cursor = conn.cursor()
        #         cursor.execute(query)
        #         result = cursor.fetchall()
        #         conn.close()
        #         return result
        
        # Define Parsl tasks
        @python_app
        def execute_query(query):
        # Create a new SQLite connection
                conn = sqlite3.connect('funcx.sqlite3')
                cursor = conn.cursor()

                # Execute the SQL query
                cursor.execute(query)

                # Get the query results
                results = cursor.fetchall()

                # Close the cursor and connection
                cursor.close()
                conn.close()

                # Return the query results
                return results


# Create a list of Parsl tasks
        tasks = [
                execute_query(test_new),
                execute_query(endPoint_new),
                execute_query(testStart_new),
                execute_query(testEnd_new),
                execute_query(testQueued_new),
                execute_query(sql_new),
                execute_query(sql2_new),
                execute_query(sqlRecent_new),
                execute_query(mostRecentT_new),
                execute_query(mostRecentF_new),
                execute_query(mostRecentE_new),
                execute_query(mostRecentTG_new)
        ]

# Execute Parsl tasks in parallel
        results = [task.result() for task in tasks]

# Store the results in the corresponding fields
        (
        testQuery_new,
        endPointQuery,
        testMessage_new,
        testMessage2_new,
        testQueue_new,
        rows_new,
        rows2_new,
        rowsRecent_new,
        mostRecentTasks_new,
        mostRecentFunctions_new,
        mostRecentEnd_new,
        mostRecentTaskGroups_new
        ) = results

        mostRecentTaskGroups_new.reverse()

        endPoints_dict = defaultdict(str)
        for result in endPointQuery:
                endPoints_dict[result[0]] = result[1]

        # start = defaultdict()
        # for x in testMessage_new:
        #         start[x[0]] = x[1]

        # end = defaultdict()
        # for y in testMessage2_new:
        #         end[y[0]] = y[1]

        # queued = defaultdict()
        # for z in testQueue_new:
        #         queued[z[0]] = z[1]

        @python_app
        def process_start_data(testMessage_new):
                start = defaultdict()
                for x in testMessage_new:
                        start[x[0]] = x[1]
                
                return start

        @python_app
        def process_end_data(testMessage2_new):
                end = defaultdict()
                for y in testMessage2_new:
                        end[y[0]] = y[1]
                
                return end

        @python_app
        def process_queued_data(testQueue_new):
                queued = defaultdict()
                for z in testQueue_new:
                        queued[z[0]] = z[1]
                
                return queued
        
        start = process_start_data(testMessage_new)
        end = process_end_data(testMessage2_new)
        queued = process_queued_data(testQueue_new)

        @python_app
        def calculate_runtimes(start, end, queued):
                runtimes = []
                queuetimes = []

                for x in start.keys():
                        timeStart = datetime.strptime(start[x], '%Y-%m-%d %H:%M:%S,%f')
                        timeEnd = datetime.strptime(end[x], '%Y-%m-%d %H:%M:%S,%f')
                        runtime_microseconds = (timeEnd - timeStart).microseconds
                        runtimes.append((start[x], runtime_microseconds))
                        
                        if x in queued.keys():
                                timeQueued = datetime.strptime(queued[x], '%Y-%m-%d %H:%M:%S,%f')
                                queuetime_microseconds = (timeStart - timeQueued).microseconds
                                queuetimes.append((start[x], queuetime_microseconds))
                
                return runtimes, queuetimes

        runtimes, queuetimes = calculate_runtimes(start, end, queued).result()

        plt.switch_backend('Agg')

        @python_app
        def create_runtime_scatterplot(runtimes):
                x_values = [runtime[0] for runtime in runtimes]
                y_values = [runtime[1] for runtime in runtimes]

                plt.scatter(x_values, y_values)
                plt.gcf().autofmt_xdate()
                plt.title("Runtime Scatter Plot")
                plt.xlabel("Date")
                plt.ylabel("Runtime (Microseconds)")
                plt.xticks([])
                plt.savefig("static/images/runtime_scatterplot" + uuidImage + ".png")
                plt.clf()

        create_runtime_scatterplot(runtimes).result()
        # create scatter plot for queuetime

        @python_app
        def create_queuetime_scatterplot(queuetimes):
                x_values = [queuetime[0] for queuetime in queuetimes]
                y_values = [queuetime[1] for queuetime in queuetimes]
                plt.scatter(x_values, y_values)
                plt.gcf().autofmt_xdate()
                plt.title("Queuetime Scatter Plot")
                plt.xlabel("Date")
                plt.ylabel("Queuetime (Microseconds)")
                plt.xticks([])
                plt.savefig("static/images/queuetime_scatterplot" + uuidImage + ".png")
                plt.clf()

        create_queuetime_scatterplot(queuetimes).result()

        # @python_app
        # def calculate_runtimes2(start, end, queued):
        #         for x in start.keys():
        #                 timeStart = datetime.strptime(start[x], '%Y-%m-%d %H:%M:%S,%f')
        #                 timeEnd = datetime.strptime(end[x], '%Y-%m-%d %H:%M:%S,%f')
        #                 runtimes.append(timeEnd - timeStart)
        #                 if (x in queued.keys()):
        #                         timeQueued = datetime.strptime(queued[x], '%Y-%m-%d %H:%M:%S,%f')
        #                         queuetimes.append(timeStart - timeQueued)
        #         return runtimes, queuetimes
        
        # runtimes2, queuetimes2 = calculate_runtimes2(start, end, queued).result()

        @python_app
        def calculate_runtimes_histogram(runtimes):
                microseconds = [runtime[1] for runtime in runtimes]
                # plt.switch_backend('Agg')
                # plt.hist(microseconds ,bins=50)
                # plt.gcf().autofmt_xdate()
                # plt.title("Histogram")
                # plt.xlabel("Microseconds")
                # plt.ylabel("Tasks Completed")
                # plt.savefig("static/images/runtime_histogram" + uuidImage + ".png")
                return microseconds

        mic = calculate_runtimes_histogram(runtimes).result()
        print(mic)
        
        @python_app
        def calculate_queuetimes_histogram(queuetimes):
                # for queuetime in queuetimes:
                #         print(queuetime)
                microseconds2 = [queuetime[1] for queuetime in queuetimes]
                plt.switch_backend('Agg')
                plt.hist(microseconds2 ,bins=50)
                plt.gcf().autofmt_xdate()
                plt.title("Histogram")
                plt.xlabel("Microseconds")
                plt.ylabel("Tasks Completed")
                plt.savefig("static/images/queuetime_histogram" + uuidImage + ".png")

        calculate_queuetimes_histogram(queuetimes).result()

        validity = rows2_new[len(rows2_new) - 1]
        validity = str(validity)[2:-10]

        # Format the data
        rows2TimeFormatted = []
        rows2TimeFormatted2 = []
        for x in range(len(rows2_new)):
                rows2TimeFormatted2.append((datetime.strptime(rows2_new[x][0], '%Y-%m-%d %H:%M:%S,%f'), rows2_new[x][1]))
                # print(rows2_new[x][1])
                rows2TimeFormatted.append(datetime.strptime(rows2_new[x][0], '%Y-%m-%d %H:%M:%S,%f'))

        groups = {}
        for r in rows2TimeFormatted2:
                if r[1] not in groups:
                        groups[r[1]] = []
                groups[r[1]].append(r[0])

        colors = ['red', 'blue', 'green', 'orange', 'purple', 'pink']
        labels = []
        num_days = (datetime.now() - rows2TimeFormatted[0]).days
        for i, (user_id, dates) in enumerate(groups.items()):
                plt.hist(dates, bins=num_days, color=colors[i % len(colors)], alpha=0.5, label='User ' + str(user_id), stacked=True)
                labels.append('User ' + str(user_id))

        # Add labels and legend
        plt.xlabel('Date')
        plt.ylabel('Tasks Completed')
        plt.title('Stacked Histogram')
        plt.gcf().autofmt_xdate()
        plt.legend(labels)

        # Show the plot
        plt.savefig("static/images/output_histogram" + uuidImage + ".png")
        plt.switch_backend('Agg')

        if (num_days > 365):
                num_days = 365
        last_year = datetime.now() - dt.timedelta(days = num_days)

        # Filter the data based on the date range
        last_year_data = [date for date in rows2TimeFormatted if date >= last_year]

        # Plot the histogram
        plt.hist(last_year_data, bins = num_days)
        plt.gcf().autofmt_xdate()
        plt.title("Histogram of Last Year's Entries")
        plt.xlabel("Date")
        plt.ylabel("Tasks Completed")
        plt.savefig("static/images/output_histogram_lastYear" + uuidImage + ".png")


        today = dt.date.today()
        # last_month = today.replace(day=1) - dt.timedelta(days=1)
        last_28_days = today - dt.timedelta(days=27)
        # one_month_ago = last_month.replace(day=1) 

        # filter rows2TimeFormatted to include only dates from last month
        # last_month_entries = [d for d in rows2TimeFormatted if one_month_ago <= d.date() <= last_month]
        last_28_days_entries = [d for d in rows2TimeFormatted if last_28_days <= d.date() <= today]

        # plot the histogram of last month's entries
        plt.switch_backend('Agg')
        plt.hist(last_28_days_entries, bins=28)
        plt.gcf().autofmt_xdate()
        plt.title("Histogram of Completed Tasks in Last Four Weeks")
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

        tI = (len(mostRecentTasks_new))
        tGI = (len(mostRecentTaskGroups_new))
        ePI = (len(mostRecentEnd_new))
        fI = (len(mostRecentFunctions_new))

        endPointIdTaskCounter = defaultdict(int)
        taskGroupIdTaskCounter = defaultdict(int)
        taskGroupIdTimeStampMap = defaultdict(str)
        functionIdTaskCounter = defaultdict(int)

        cursor.execute(query_endpoint_uuid)
        for row in cursor.fetchall():
                endpoint_uuid, frequency = row
                endPointIdTaskCounter[endpoint_uuid] = frequency

        cursor.execute(query_task_group_uuid)
        for row in cursor.fetchall():
                task_group_uuid, frequency = row
                taskGroupIdTaskCounter[task_group_uuid] = frequency

                # Check if the task_group_uuid is not already in the taskGroupIdTimeStampMap
                if taskGroupIdTimeStampMap[task_group_uuid] == "":
                        # Get the first asctime appearance for the task_group_uuid
                        cursor.execute("SELECT asctime FROM new_awslog2 WHERE task_group_uuid=? ORDER BY asctime LIMIT 1", (task_group_uuid,))
                        first_asctime_row = cursor.fetchone()
                        if first_asctime_row:
                                first_asctime = first_asctime_row[0]
                                taskGroupIdTimeStampMap[task_group_uuid] = first_asctime

        cursor.execute(query_function_uuid)
        for row in cursor.fetchall():
                function_uuid, frequency = row
                functionIdTaskCounter[function_uuid] = frequency

        cursor.execute(query_user_id)
        for row in cursor.fetchall():
                user_id, frequency = row

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
        imageRT = os.path.join(app.config['UPLOAD FOLDER'], 'runtime_scatterplot' + uuidImage + '.png')
        imageQT = os.path.join(app.config['UPLOAD FOLDER'], 'queuetime_scatterplot' + uuidImage + '.png')
        imageRT2 = os.path.join(app.config['UPLOAD FOLDER'], 'runtime_histogram' + uuidImage + '.png')
        imageQT2 = os.path.join(app.config['UPLOAD FOLDER'], 'queuetime_histogram' + uuidImage + '.png')

        for x in range(5):
                newTGIx[x] = str(taskGroupIdTaskCounter[newTGIx[x]]) + " tasks at " + taskGroupIdTimeStampMap[newTGIx[x]]
                mostRecentTaskGroups_new[x] = str(taskGroupIdTaskCounter[mostRecentTaskGroups_new[x][0]]) + " tasks at " + taskGroupIdTimeStampMap[mostRecentTaskGroups_new[x][0]]
                mostRecentFunctions_new[x] = mostRecentFunctions_new[x][0]
                if (x < len(newEPIx)):
                        if (endPoints_dict[newEPIx[x]] != None):
                                newEPIx[x] = endPoints_dict[newEPIx[x]]
                if (x < len(mostRecentEnd_new)):
                        mostRecentEnd_new[x] = mostRecentEnd_new[x][0]
                        if (endPoints_dict[mostRecentEnd_new[x]] != None):
                                mostRecentEnd_new[x] = endPoints_dict[mostRecentEnd_new[x]]

        # print(datetime.now())
        return render_template("index.html", rt2 = imageRT2, qt2 = imageQT2, time = validity, tIS = tI, tGIS = tGI, ePIS = ePI, fIS = fI, histogram = pic1, cumulative = pic2, eP = pic3, tG = pic4, func = pic5, popTaskGroups = newTGIx, popFuncGroups = newFx, popEndGroups = newEPIx, mRT = mostRecentTaskGroups_new, mRE = mostRecentEnd_new, mRF = mostRecentFunctions_new, picSix = pic6, picSeven = pic7, rt = imageRT, qt = imageQT)

#start here

@app.route("/", methods=['POST'])
def createUserInfo():
        user = request.form['userID']
        connection = sqlite3.connect("funcx.sqlite3")
        cursor = connection.cursor()
        sql = """
                select * from awslog where json_extract(entry, "$.task_uuid") is not null;

        """
        sql2 = """
                select json_extract(entry, "$.asctime") from awslog
                where json_extract(entry, "$.message") = "received"
                and json_extract(entry, "$.task_uuid") is not null
                order by json_extract(entry, "$.asctime");

        """

        sqlRecent = """
                select * from awslog
                where json_extract(entry, "$.message") = "received"
                and json_extract(entry, "$.task_uuid") is not null
                and json_extract(entry, "$.user_id") = """ + user + """
                order by json_extract(entry, "$.asctime");
        """

        testUser = """
                select distinct json_extract(entry, "$.endpoint_name") from awslog
                where json_extract(entry, "$.user_id") = """ + user + """
                order by json_extract(entry, "$.asctime");
        """

        testQueryUser = cursor.execute(testUser).fetchall()
        # print(testQueryUser)

        sql3 = 'select * from awslog where json_extract(entry, "$.user_id") = ' + user + ' and json_extract(entry, "$.task_uuid") is not null;'

        sql4 = 'select json_extract(entry, "$.asctime") from awslog where json_extract(entry, "$.message") = "received" and json_extract(entry, "$.task_uuid") is not null and json_extract(entry, "$.user_id") = ' + user + ' order by json_extract(entry, "$.asctime");'

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
                if (json_object["task_uuid"] not in mostRecentTasks):
                        mostRecentTasks.append(json_object["task_uuid"][0])
                if (json_object["function_uuid"] not in mostRecentFunctions):
                        mostRecentFunctions.append(json_object["function_uuid"][0])
                if (json_object["endpoint_uuid"] not in mostRecentEnd):
                        mostRecentEnd.append(json_object["endpoint_uuid"][0])
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
                taskIdSetUser.add(json_object["task_uuid"])
                taskGroupIdSetUser.add(json_object["task_group_uuid"])
                endPointIdSetUser.add(json_object["endpoint_uuid"])
                functionIdSetUser.add(json_object["function_uuid"])
        tIU = (len(taskIdSetUser))
        tGIU = (len(taskGroupIdSetUser))
        ePIU = (len(endPointIdSetUser))
        fIU = (len(functionIdSetUser))

        userEndPointIdTaskCounter = defaultdict(int)
        userTaskGroupIdTaskCounter = defaultdict(int)
        userFunctionIdTaskCounter = defaultdict(int)
        
        for x in range(len(rowsUser)):    
                json_object = json.loads(rowsUser[x][0])
                userEndPointIdTaskCounter[json_object["endpoint_uuid"]] += 1
                userTaskGroupIdTaskCounter[json_object["task_group_uuid"]] += 1
                userFunctionIdTaskCounter[json_object["function_uuid"]] += 1
                

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

