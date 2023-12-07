import csv
from flask import Flask, render_template, jsonify

app = Flask(__name__)


# 这是读取csv文件的方法
def read_csv():
    csv_data = []
    with open('static/amazon-reviews.csv', 'r') as f:
        csv_file = csv.DictReader(f)
        for data in csv_file:
            csv_data.append(data)
    return csv_data


@app.route('/dashBoard')
def dashBoard():
    return render_template('dashBoard.html')

@app.route('/cityInfo')
def cityInfo():
    return render_template('cityInfo.html')

@app.route('/readCSVFile', methods=['GET'])
def readCSVFile():
    csv_data = read_csv()
    return jsonify(csv_data)

# 读取城市信息
@app.route('/readCityInfo/<city>')
def readCityInfo(city):
    with open('static/us-cities.csv', 'r') as f:
        info = csv.DictReader(f)
        for i in info:
            if i['city'] == city:
                return render_template('cityInfo.html', **i)
        return None

if __name__ == '__main__':
    app.run()
