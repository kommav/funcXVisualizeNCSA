import matplotlib.pyplot as plt
import datetime as dt
from collections import defaultdict
import sqlite3
import parsl

# Initialize the Parsl dataflow execution environment
parsl.load()

# Define the Parsl dataflow task for creating a runtime scatter plot
@parsl.python_app
def create_runtime_scatterplot(runtimes, uuidImage):
    import matplotlib.pyplot as plt
    plt.switch_backend('Agg')
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

# Define the Parsl dataflow task for creating a queuetime scatter plot
@parsl.python_app
def create_queuetime_scatterplot(queuetimes, uuidImage):
    import matplotlib.pyplot as plt
    plt.switch_backend('Agg')
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

# Define the Parsl dataflow task for creating a runtime histogram
@parsl.python_app
def create_runtime_histogram(runtimes, uuidImage):
    import matplotlib.pyplot as plt
    plt.switch_backend('Agg')
    microseconds = [runtime.microseconds for runtime in runtimes]
    plt.hist(microseconds, bins=50)
    plt.gcf().autofmt_xdate()
    plt.title("Runtime Histogram")
    plt.xlabel("Microseconds")
    plt.ylabel("Tasks Completed")
    plt.savefig("static/images/runtime_histogram" + uuidImage + ".png")
    plt.clf()

# Define the Parsl dataflow task for creating a queuetime histogram
@parsl.python_app
def create_queuetime_histogram(queuetimes, uuidImage):
    import matplotlib.pyplot as plt
    plt.switch_backend('Agg')
    microseconds = [queuetime.microseconds for queuetime in queuetimes]
    plt.hist(microseconds, bins=50)
    plt.gcf().autofmt_xdate()
    plt.title("Queuetime Histogram")
    plt.xlabel("Microseconds")
    plt.ylabel("Tasks Completed")
    plt.savefig("static/images/queuetime_histogram" + uuidImage + ".png")
    plt.clf()

# Define the Parsl dataflow task for creating a stacked histogram
@parsl.python_app
def create_stacked_histogram(data, uuidImage):
    import matplotlib.pyplot as plt
    plt.switch_backend('Agg')
    rowsTimeFormatted = [datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S,%f') for row in data]
    groups = {}
    for row in data:
        if row[1] not in groups:
            groups[row[1]] = []
        groups[row[1]].append(datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S,%f'))
    colors = ['blue', 'green', 'orange', 'red', 'purple', 'pink']
    labels = list(groups.keys())
    plt.hist([groups[label] for label in labels], bins=50, stacked=True, color=colors[:len(labels)], label=labels)
    plt.legend()
    plt.gcf().autofmt_xdate()
    plt.title("Stacked Histogram")
    plt.xlabel("Date")
    plt.ylabel("Tasks Completed")
    plt.xticks([])
    plt.savefig("static/images/stacked_histogram" + uuidImage + ".png")
    plt.clf()

# Define the Parsl dataflow task for creating a runtime box plot
@parsl.python_app
def create_runtime_boxplot(runtimes, uuidImage):
    import matplotlib.pyplot as plt
    plt.switch_backend('Agg')
    data = [runtime[1] for runtime in runtimes]
    plt.boxplot(data)
    plt.title("Runtime Boxplot")
    plt.ylabel("Runtime (Microseconds)")
    plt.savefig("static/images/runtime_boxplot" + uuidImage + ".png")
    plt.clf()

# Define the Parsl dataflow task for creating a queuetime box plot
@parsl.python_app
def create_queuetime_boxplot(queuetimes, uuidImage):
    import matplotlib.pyplot as plt
    plt.switch_backend('Agg')
    data = [queuetime[1] for queuetime in queuetimes]
    plt.boxplot(data)
    plt.title("Queuetime Boxplot")
    plt.ylabel("Queuetime (Microseconds)")
    plt.savefig("static/images/queuetime_boxplot" + uuidImage + ".png")
    plt.clf()

# Define the Parsl dataflow task for creating a bar chart
@parsl.python_app
def create_bar_chart(data, uuidImage):
    import matplotlib.pyplot as plt
    plt.switch_backend('Agg')
    x_values = [entry[0] for entry in data]
    y_values = [entry[1] for entry in data]
    plt.bar(x_values, y_values)
    plt.title("Bar Chart")
    plt.xlabel("Category")
    plt.ylabel("Value")
    plt.xticks(rotation=45)
    plt.savefig("static/images/bar_chart" + uuidImage + ".png")
    plt.clf()

# Define the Parsl dataflow task for creating a pie chart
@parsl.python_app
def create_pie_chart(data, uuidImage):
    import matplotlib.pyplot as plt
    plt.switch_backend('Agg')
    labels = [entry[0] for entry in data]
    values = [entry[1] for entry in data]
    plt.pie(values, labels=labels, autopct='%1.1f%%')
    plt.title("Pie Chart")
    plt.savefig("static/images/pie_chart" + uuidImage + ".png")
    plt.clf()

# Generate a unique identifier for image filenames
uuidImage = dt.datetime.now().strftime("%Y%m%d%H%M%S")

# Create a Parsl dataflow future for each dataflow task
runtime_scatterplot_future = create_runtime_scatterplot(runtimes, uuidImage)
queuetime_scatterplot_future = create_queuetime_scatterplot(queuetimes, uuidImage)
runtime_histogram_future = create_runtime_histogram(runtimes, uuidImage)
queuetime_histogram_future = create_queuetime_histogram(queuetimes, uuidImage)
stacked_histogram_future = create_stacked_histogram(data, uuidImage)
runtime_boxplot_future = create_runtime_boxplot(runtimes, uuidImage)
queuetime_boxplot_future = create_queuetime_boxplot(queuetimes, uuidImage)
bar_chart_future = create_bar_chart(data, uuidImage)
pie_chart_future = create_pie_chart(data, uuidImage)

# Wait for all tasks to complete
parsl.wait_for_tasks()

# Retrieve the results of the Parsl dataflow tasks
runtime_scatterplot_future.result()
queuetime_scatterplot_future.result()
runtime_histogram_future.result()
queuetime_histogram_future.result()
stacked_histogram_future.result()
runtime_boxplot_future.result()
queuetime_boxplot_future.result()
bar_chart_future.result()
pie_chart_future.result()

# Cleanup the Parsl dataflow environment
parsl.cleanup()

# Print the image filenames for reference
print("Runtime Scatterplot: runtime_scatterplot" + uuidImage + ".png")
print("Queuetime Scatterplot: queuetime_scatterplot" + uuidImage + ".png")
print("Runtime Histogram: runtime_histogram" + uuidImage + ".png")
print("Queuetime Histogram: queuetime_histogram" + uuidImage + ".png")
print("Stacked Histogram: stacked_histogram" + uuidImage + ".png")
print("Runtime Boxplot: runtime_boxplot" + uuidImage + ".png")
print("Queuetime Boxplot: queuetime_boxplot" + uuidImage + ".png")
print("Bar Chart: bar_chart" + uuidImage + ".png")
print("Pie Chart: pie_chart" + uuidImage + ".png")
