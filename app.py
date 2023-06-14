from flask import Flask, render_template, request
import pandas as pd
import datetime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            df = pd.read_csv(file)
            selected_columns = ['Learners Name', 'Institute Name', 'Course Title', 'Submission Date', 'Status']
            selected_data = df[selected_columns]

            current_date = datetime.datetime.now().date()
            previous_day = current_date - datetime.timedelta(days=1)
            cutoff_time = datetime.datetime.combine(previous_day, datetime.time(hour=21, minute=0))

            result = []
            for index, row in selected_data.iterrows():
                date_string = row['Submission Date']
                date_value = float(date_string)
                date_format = pd.to_datetime(date_value, unit='ms')

                if row['Status'] == 'pending' and date_format.to_pydatetime() < cutoff_time:
                    item = {
                        'LearnerName': row['Learners Name'],
                        'Institute Name': row['Institute Name'],
                        'Course Title': row['Course Title'],
                        'SubmissionDate': date_format.strftime('%Y-%m-%d %H:%M'),
                        'Status': row['Status']
                    }
                    result.append(item)

            return render_template('index.html', result=result)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
