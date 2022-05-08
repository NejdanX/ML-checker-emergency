import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import BernoulliNB
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import classification_report
import pickle


pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 1000)


def top_n_words(vectorizer, X, n):
    idx = np.ravel(X.sum(axis=0).argsort(axis=1))[::-1][:n]
    return np.array(vectorizer.get_feature_names())[idx].tolist()


def main():
    train = pd.read_csv('clear_train.csv', index_col=[0])
    # test_df = pd.read_csv('clear_test.csv', index_col=[0])
    # new_df = pd.read_csv('test.csv')
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(train['cleared_text'])
    y = train['target']
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.3, random_state=1)
    # print(top_n_words(vectorizer, X, 20))
    clf = BernoulliNB(alpha=0.1)

    clf.fit(X_train, y_train)
    print("[{}] Accuracy: train = {}, test = {}".format(
        clf.__class__.__name__,
        clf.score(X_train, y_train),
        clf.score(X_val, y_val)))
    with open('../static/models/NBall_model.pkl', 'wb') as f:
        pickle.dump(clf, f)
    # load data
    # with with open('NB_model.pkl', 'rb') as f:
    #     clf = pickle.load(f)
    recall = cross_val_score(clf, X, y, cv=5, scoring='recall')
    print('Recall', np.mean(recall), recall)
    precision = cross_val_score(clf, X, y, cv=5, scoring='precision')
    print('Precision', np.mean(precision), precision)
    f1 = cross_val_score(clf, X, y, cv=5, scoring='f1')
    print('F1', np.mean(f1), f1)
    print(classification_report(y_val, clf.predict(X_val), target_names=['Non-disaster', 'Disaster']))
    # print(clf.predict(vectorizer.transform(['оборудование сгореть'])))
    print(clf.predict_proba((vectorizer.transform(['пожар огонь']))))
    # test_df = test_df.fillna('')
    # predictions = [clf.predict(vectorizer.transform([text]))[0] if text else 0 for text in test_df['cleared_text']]
    # test_df['target'] = predictions
    # test_df['id'] = new_df['id']
    # test_df = test_df[['id', 'target']]
    # test_df = test_df.set_index('id')
    # test_df.to_csv('successful.csv')


if __name__ == '__main__':
    main()