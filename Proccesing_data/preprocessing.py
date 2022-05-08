import spacy
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud

pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 1000)
nlp = spacy.load('ru_core_news_sm')
STOP_WORDS = nlp.Defaults.stop_words


def remove_URL(text):
    url = re.compile(r'https?://\S+|www\.\S+')
    return url.sub(r'', text)


def remove_html(text):
    html = re.compile(r'<.*?>+')
    return html.sub(r'', text)


def remove_appeal(text):
    appeal = re.compile(r'@\w+')
    return appeal.sub(r'', text)


def remove_emoji(text):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)


def only_russian_words(text):
    r = re.compile("[A-Za-z]+")
    return r.sub(r'', text)


def tokenize_text(text):
    doc = nlp(text)
    return [lemmatization(token).lower() for token in doc if not token.is_punct and ' ' not in token.text
            and 'Û' not in token.text and not is_stop_word(token.text.lower())]


def lemmatization(token):
    return token.lemma_


def is_stop_word(token):
    return token in STOP_WORDS


def clear_message(message):
    return ' '.join(tokenize_text(only_russian_words(remove_appeal(remove_emoji(remove_html(remove_URL(message)))))))


def clear_data(train, test):

    train.rename(columns={'russian_text': 'text'}, inplace=True)
    train['text'] = train['text'].apply(lambda text: remove_URL(text)).apply(lambda text: remove_appeal(text))
    train['text'] = train['text'].apply(lambda text: remove_html(text)).apply(lambda text: only_russian_words(text))
    train['text'] = train['text'].apply(lambda text: remove_emoji(text)).apply(lambda x: re.sub('\[.*?\]', '', x))
    train['text'] = train['text'].apply(lambda x: re.sub('\w*\d\w*', '', x))
    train['cleared_text'] = [' '.join(tokenize_text(text)) if tokenize_text(text) else np.nan for text in train['text']]
    train = train.dropna(how='any', axis=0)
    train = train[['text', 'cleared_text', 'target']]

    test.rename(columns={'russian_text': 'text'}, inplace=True)
    test['text'] = test['text'].apply(lambda text: remove_URL(text)).apply(lambda text: remove_appeal(text))
    test['text'] = test['text'].apply(lambda text: remove_html(text)).apply(lambda text: only_russian_words(text))
    test['text'] = test['text'].apply(lambda text: remove_emoji(text)).apply(lambda x: re.sub('\[.*?\]', '', x))
    test['text'] = test['text'].apply(lambda x: re.sub('\w*\d\w*', '', x))
    test['cleared_text'] = [' '.join(tokenize_text(text)) if tokenize_text(text) else np.nan for text in test['text']]
    return train, test


def cloud_words(disaster_tweets, non_disaster_tweets):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=[16, 8])
    wordcloud1 = WordCloud(background_color='white',
                           width=600,
                           height=400).generate(" ".join(disaster_tweets))
    ax1.imshow(wordcloud1)
    ax1.axis('off')
    ax1.set_title('Disaster Tweets', fontsize=40)

    wordcloud2 = WordCloud(background_color='white',
                           width=600,
                           height=400).generate(" ".join(non_disaster_tweets))
    ax2.imshow(wordcloud2)
    ax2.axis('off')
    ax2.set_title('Non Disaster Tweets', fontsize=40)


def main():
    train = pd.read_csv('clear_train.csv.', index_col=[0])
    test = pd.read_csv('Proccesing_data/clear_test.csv', index_col=[0])

    # train, test = clear_data(train, test)
    # train.to_csv('clear_train.csv')
    # test.to_csv('clear_test.csv')
    disaster_tweets = train[train['target'] == 1]['cleared_text']
    non_disaster_tweets = train[train['target'] == 0]['cleared_text']
    cloud_words(disaster_tweets, non_disaster_tweets)


if __name__ == '__main__':
    main()