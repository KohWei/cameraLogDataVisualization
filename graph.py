from flask import Flask, render_template
import pandas as pd
import plotly.express as px
import plotly.io as pio
import gdown

app = Flask(__name__)


url = 'https://drive.google.com/uc?export=download&id=1JezkyEFiGsRoqGj-9-vnY23no6Rn5vxZ'

# Download the file
gdown.download(url, 'Textual.csv', quiet=False)

# Load your data
data = pd.read_csv('Textual.csv')

# Ensure 'Datetime' column is in datetime format
data['Datetime'] = pd.to_datetime(data['Datetime'])

# Separate into Hour, Minute, and Second columns
data['Date'] = data['Datetime'].dt.date
data['Hour'] = data['Datetime'].dt.hour

totalErrorCount = (data['ErrorType'] == 'Error').sum()
totalWarning = (data['ErrorType'] == 'Warning').sum()

# Drop unwanted columns, e.g., 'Time' column
data = data.drop(['Datetime', 'ErrorType', 'ErrorCode'], axis=1)

# Filter data for specific ViewIDs (camera IDs)
viewID = [3001, 3002, 3003, 3004]
filteredID = data[data['ViewID'].isin(viewID)]

# Filter rows where the ErrorDescription contains 'video frame missing'
cameraDownData = filteredID[filteredID['ErrorDescription'].str.contains("video frame missing", case=False, na=False)]


@app.route('/')
def dashboard():
    ## First Graph
    totalError = (
        cameraDownData.groupby('ViewID')
        .size()
        .reset_index(name='ErrorCount')
    )

    # Create the Plotly bar chart
    plot = px.bar(
        totalError,
        x='ViewID',
        y='ErrorCount',
        text='ErrorCount',  # Display error counts on the bars
        title='Total Error Frequency for Each Camera (Video Frame Missing)',
        labels={'ViewID': 'Camera ID', 'ErrorCount': 'Total Number of Errors'},
        color='ViewID',  # Color by ViewID for distinction
    )

    # Customize layout for readability
    plot.update_layout(
        title=dict(x=0.5),  # Center the title
        xaxis=dict(
            title='Camera ID',
            tickmode='array',  # Use specific ticks
            tickvals=viewID,  # Set the ViewIDs as tick values
        ),
        yaxis=dict(title='Total Number of Errors'),
        template='plotly_dark',
    )

    # Convert the plot to HTML div for embedding in the template
    graph_html = pio.to_html(plot, full_html=False)

    ## Second Graph
    # Group by ViewID and Date to count occurrences
    downTimeCounts = (
        cameraDownData.groupby(['ViewID', 'Date'])
        .size()
        .reset_index(name='DowntimeCount')
    )

    # Plot using Plotly
    plot = px.line(
        downTimeCounts,
        x='Date',
        y='DowntimeCount',
        color='ViewID',
        title='Camera Downtime Analysis (Video Frame Missing)',
        labels={'DowntimeCount': 'Downtime Events', 'Date': 'Date'},
        markers=True,
    )

    # Customize layout for readability
    plot.update_layout(
        title=dict(x=0.5),  # Center title
        xaxis=dict(title='Date', tickformat='%Y-%m-%d'),
        yaxis=dict(title='Number of Downtime Events'),
        legend_title='Camera ID',
        template='plotly_dark',
    )

    # Convert the plot to HTML div for embedding in the template
    graph2_html = pio.to_html(plot, full_html=False)

    # Group by 'Hour' and 'ViewID' to count occurrences
    thirdGraph = (
        cameraDownData.
        groupby(['Hour', 'ViewID']).
        size().reset_index(name='ErrorCount')
    )

    # Plot using Plotly as a line chart
    plot = px.line(
        thirdGraph,
        x='Hour',
        y='ErrorCount',
        color='ViewID',
        title='Video Frame Missing Errors by Hour for Different Cameras',
        labels={'ErrorCount': 'Number of Errors', 'Hour': 'Hour of the Day'},
    )

    # Customize layout for readability
    plot.update_layout(
        title=dict(x=0.5),  # Center title
        xaxis=dict(title='Hour of the Day'),
        yaxis=dict(title='Number of Errors'),
        legend_title='Camera ID',
        template='plotly_dark',
    )
    # Convert the plot to HTML div for embedding in the template
    graph3_html = pio.to_html(plot, full_html=False)

    return render_template('index.html', graph_html=graph_html, graph2_html=graph2_html, graph3_html=graph3_html,
                           totalErrorCount=totalErrorCount, totalWarning=totalWarning)


if __name__ == '__main__':
    app.run(debug=True)
