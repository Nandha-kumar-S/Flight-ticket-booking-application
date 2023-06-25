import mysql.connector
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from collections import Counter

class feedback_analytics:
    @staticmethod
    def analyze():
        db = mysql.connector.connect(
            host='localhost',
            user='root',
            password='0000',
            database='flight_application'
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
        pie_chart = "C:\\Users\\suriy\\OneDrive\\Desktop\\Devrev\\Flask sample 2\\Static\\sentiment.png"
        plt.savefig(pie_chart)
        plt.close()
        return pie_chart
