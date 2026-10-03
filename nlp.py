import os
import mysql.connector
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from collections import Counter
import yaml

# Resolve paths relative to this file so the app runs on any machine.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, 'helpers', 'config.yaml'), 'r') as stream:
    config = yaml.safe_load(stream)


class feedback_analytics:
    @staticmethod
    def analyze():
        db = mysql.connector.connect(
            host=config['DB_HOST'],
            user=config['DB_USER'],
            password=config['DB_PASSWORD'],
            database=config['DB_NAME']
        )
        cursor = db.cursor()
        cursor.execute('SELECT message FROM feedback')
        outs = cursor.fetchall()
        feedbacks = [item[0] for item in outs]

        sia = SentimentIntensityAnalyzer()

        sentiment_list = []
        for feedback in feedbacks:
            sentiment_score = sia.polarity_scores(feedback)
            sentiment_label = feedback_analytics.get_sentiment_label(sentiment_score)
            sentiment_list.append(sentiment_label)

        feedback_analytics.plot_pie_chart(sentiment_list)

    @staticmethod
    def get_sentiment_label(sentiment_score):
        compound_score = sentiment_score['compound']
        if compound_score >= 0.05:
            return 'Positive'
        elif compound_score <= -0.05:
            return 'Negative'
        else:
            return 'Neutral'

    @staticmethod
    def plot_pie_chart(sentiment):
        sentiment_counts = Counter(sentiment)
        pos_count = sentiment_counts['Positive']
        neg_count = sentiment_counts['Negative']
        neutral_count = sentiment_counts['Neutral']
        total_count = pos_count + neutral_count + neg_count

        labels = ['Positive feedbacks', 'Negative feedbacks', 'Neutral feedbacks']
        sizes = sentiment_counts.values()
        colors = ['green', 'red', 'gray']

        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
        plt.axis('equal')
        pie_chart = os.path.join(BASE_DIR, 'Static', 'sentiment.png')
        os.makedirs(os.path.dirname(pie_chart), exist_ok=True)
        plt.savefig(pie_chart)
        plt.close()
        return pie_chart
