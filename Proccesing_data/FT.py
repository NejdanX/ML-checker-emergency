import fasttext
import pandas as pd
import numpy as np
import csv
from preprocessing import clear_message
import operator

'''Without pretrained vectors'''
df = pd.read_csv('clear_train.csv', index_col=[0])
test = pd.read_csv('clear_test.csv', index_col=[0])
sub = pd.read_csv('perfect_submission.csv')
test = test['cleared_text']
sub = sub['target'].apply(lambda x: '__label__DISASTER' if x else '__label__NON-DISASTER')
print(sub)
print(test)
test = pd.DataFrame(zip(sub, test))
test.dropna(how='any', axis=0)
test = test.rename(columns={0: 'target', 1: 'cleared_text'})
print(test)
df = df[['target', 'cleared_text']]
df['target'] = df['target'].apply(lambda x: '__label__DISASTER' if x else '__label__NON-DISASTER')
# df.to_csv('train.txt',
#           index=False,
#           sep=' ',
#           header=None,
#           quoting=csv.QUOTE_NONE,
#           quotechar="",
#           escapechar=" ")

# test.to_csv('test.txt',
#           index=False,
#           sep=' ',
#           header=None,
#           quoting=csv.QUOTE_NONE,
#           quotechar="",
#           escapechar=" ")
# model = fasttext.load_model('best_fasttext.bin')
# text = clear_message('Привет!')
# print(model.predict(text, k=2))
# print(model.test('test.txt'))
fasttext_embeddings = fasttext.load_model('cc.ru.300.bin')


def build_vocab(X):
    tweets = X.apply(lambda s: str(s).split()).values

    vocab = {}

    for tweet in tweets:
        for word in tweet:
            try:
                vocab[word] += 1
            except KeyError:
                vocab[word] = 1
    return vocab


def check_embeddings_coverage(X, embeddings):
    vocab = build_vocab(X)

    covered = {}
    oov = {}
    n_covered = 0
    n_oov = 0

    for word in vocab:
        try:
            covered[word] = embeddings[word]
            n_covered += vocab[word]
        except:
            oov[word] = vocab[word]
            n_oov += vocab[word]

    vocab_coverage = len(covered) / len(vocab)
    text_coverage = (n_covered / (n_covered + n_oov))

    sorted_oov = sorted(oov.items(), key=operator.itemgetter(1))[::-1]
    return sorted_oov, vocab_coverage, text_coverage


train_fasttext_oov, train_fasttext_vocab_coverage, train_fasttext_text_coverage = check_embeddings_coverage(
    df['cleared_text'], fasttext_embeddings)
test_fasttext_oov, test_fasttext_vocab_coverage, test_fasttext_text_coverage = check_embeddings_coverage(
    test['cleared_text'], fasttext_embeddings)
print('FastText Embeddings cover {:.2%} of vocabulary and {:.2%} of text in Training Set'.format(
    train_fasttext_vocab_coverage, train_fasttext_text_coverage))
print(
    'FastText Embeddings cover {:.2%} of vocabulary and {:.2%} of text in Test Set'.format(test_fasttext_vocab_coverage,
                                                                                           test_fasttext_text_coverage))