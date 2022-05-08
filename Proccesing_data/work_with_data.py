import spacy
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import CountVectorizer
from pprint import pprint
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 1000)


def main():
    # df = pd.read_csv('clear_train.csv', index_col=[0])
    # df = df.dropna(how='any', axis=0)
    # print(df[50:100])
    test = pd.read_csv('clear_test.csv', index_col=[0])
    target = pd.read_csv('perfect_submission.csv', index_col=[0])
    train = pd.read_csv('clear_train.csv', index_col=[0])
    test['target'] = target['target']
    test = test.dropna(how='any', axis=0)
    df = pd.concat([train, test])
    df['target'] = df['target'].apply(lambda x: int(x))
    df.to_csv('all_train.csv')
    # 64 строка


if __name__ == '__main__':
    main()