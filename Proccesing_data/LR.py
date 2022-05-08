from sklearn.linear_model import LogisticRegression
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import BernoulliNB
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import classification_report
import pickle


train = pd.read_csv('clear_train.csv', index_col=[0])
test = pd.read_csv('clear_test.csv', index_col=[0])
vectorizer = TfidfVectorizer()
features_train = vectorizer.fit_transform(train['cleared_text'])
y_t = train['target']
X_train, X_val, y_train, y_val = train_test_split(features_train, y_t, test_size=0.3, random_state=1)
logreg = LogisticRegression(max_iter=2000, random_state=1).fit(X_train, y_train)


print("[{}] Accuracy: train = {}, test = {}".format(
        logreg.__class__.__name__,
        logreg.score(X_train, y_train),
        logreg.score(X_val, y_val)))

recall = cross_val_score(logreg, features_train, y_t, cv=5, scoring='recall')
print('Recall', np.mean(recall), recall)
precision = cross_val_score(logreg, features_train, y_t, cv=5, scoring='precision')
print('Precision', np.mean(precision), precision)
f1 = cross_val_score(logreg, features_train, y_t, cv=5, scoring='f1')
print('F1', np.mean(f1), f1)
print(classification_report(y_val, logreg.predict(X_val), target_names=['Non-disaster', 'Disaster']))
print(logreg.predict_proba((vectorizer.transform(['Здание в огне']))))