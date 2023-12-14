import csv
from collections import Counter

from flask import Flask, render_template, jsonify, request

app = Flask(__name__)


# 这是读取csv文件的方法
def read_csv():
    csv_data = []
    with open('static/amazon-reviews.csv', 'r') as f:
        csv_file = csv.DictReader(f)
        for data in csv_file:
            csv_data.append(data)
    return csv_data


# 这是读取城市信息的方法
def read_city():
    city_data = []
    with open('static/us-cities.csv', 'r') as f:
        csv_file = csv.DictReader(f)
        for data in csv_file:
            city_data.append(data)
    return city_data


# 这是写入csv文件的方法
def write_csv(filename, data):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

@app.route('/word')
def word():
    return render_template('word.html')

@app.route('/popular_words', methods=['GET'])
def popular_words():
    # 读取城市信息
    city_data = read_city()
    # 读取评论数据
    reviews_data = read_csv()
    city = request.args.get('city')
    limit = request.args.get('limit', type=int, default=10)

    # 筛选符合城市条件的评论
    if city:
        filtered_reviews = [review for review in reviews_data if review['city'] == city]
    else:
        filtered_reviews = reviews_data

    # 统计单词出现频率
    word_counts = Counter()
    for review in filtered_reviews:
        words = review['review'].split()
        word_counts.update(words)

    # 获取最常见的单词
    common_words = word_counts.most_common(limit)

    # 构建响应
    response = [{"term": word, "popularity": count} for word, count in common_words]
    return jsonify(response)


@app.route('/popular_words2', methods=['GET'])
def popular_words2():
    # 读取城市信息
    city_data = read_city()
    # 读取评论数据
    reviews_data = read_csv()
    city = request.args.get('city')
    limit = request.args.get('limit', type=int, default=10)
    city_population = {city['city']: int(city['population']) for city in city_data}

    # 筛选符合城市条件的评论
    if city:
        filtered_reviews = [review for review in reviews_data if review['city'] == city]
    else:
        filtered_reviews = reviews_data

    # 计算单词热度
    word_popularity = {}
    for review in filtered_reviews:
        words = review['review'].split()
        review_city = review['city']
        for word in words:
            if word not in word_popularity:
                word_popularity[word] = {'cities': set(), 'popularity': 0}
            if review_city not in word_popularity[word]['cities']:
                word_popularity[word]['cities'].add(review_city)
                word_popularity[word]['popularity'] += city_population.get(review_city, 0)

    # 获取最受欢迎的单词
    popular_words = sorted(word_popularity.items(), key=lambda x: x[1]['popularity'], reverse=True)
    popular_words = popular_words[:limit]

    # 构建响应
    response = [{"term": word, "popularity": info['popularity']} for word, info in popular_words]
    return jsonify(response)


# 替换单词
@app.route('/substitute_words', methods=['POST'])
def substitute_words():
    request_data = request.get_json()
    original_word = request_data.get('word')
    new_word = request_data.get('substitute')

    reviews_data = read_csv()
    affected_reviews = 0

    for review in reviews_data:
        if original_word in review['review']:
            review['review'] = review['review'].replace(original_word, new_word)
            affected_reviews += 1

    write_csv('static/amazon-reviews.csv', reviews_data)

    return jsonify({"affected_reviews": affected_reviews})


if __name__ == '__main__':
    app.run()
