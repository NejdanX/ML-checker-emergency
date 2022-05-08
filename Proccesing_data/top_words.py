# Counting the number of words
from collections import Counter
# Plotting functions
import matplotlib.pyplot as plt
import pandas as pd


train = pd.read_csv('clear_train.csv', index_col=[0])

# Getting the most frequent words
d1 = train.loc[train['target'] == 1, 'cleared_text'].tolist()
d0 = train.loc[train['target'] == 0, 'cleared_text'].tolist()
d1_text = ' '.join(d1).split()
d0_text = ' '.join(d0).split()
topd1 = Counter(d1_text)
topd0 = Counter(d0_text)
topd1 = topd1.most_common(20)
topd0 = topd0.most_common(20)
plt.bar(range(len(topd1)), [val[1] for val in topd1], align='center')
plt.xticks(range(len(topd1)), [val[0] for val in topd1])
plt.xticks(rotation=70)
plt.title('Disaster tweets')
plt.show()
plt.bar(range(len(topd0)), [val[1] for val in topd0], align='center')
plt.xticks(range(len(topd0)), [val[0] for val in topd0])
plt.xticks(rotation=70)
plt.title('Not disaster tweets')
plt.show()