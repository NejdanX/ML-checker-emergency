import spacy
import pandas as pd
from WorkWithData.translate_dataset import translate_text
import os.path
i = 0

nlp = spacy.load('en_core_web_sm')
STOP_WORDS = nlp.Defaults.stop_words
STOP_WORDS.remove('not')


def tokenize_text(text):
    global i
    i += 1
    print(i)
    doc = nlp(text)
    return [token.text for token in doc if not token.is_punct]


def lemmatization(token):
    return token.lemma_


def is_stop_word(token):
    return token in STOP_WORDS


def vectorize(tokens):
    pass


def main():
    df = pd.read_csv('train.csv')
    df = df.drop(labels=['keyword', 'location'], axis=1)
    if os.path.exists('russian_train.csv'):
        pass
    else:
        russian_text = [translate_text(' '.join(tokenize_text(text))) for text in df.iloc[:, 1]]
        new_df = pd.DataFrame({'russian_text': russian_text, 'target': df['target']})
        new_df.to_csv('russian_train.csv')


if __name__ == '__main__':
    main()