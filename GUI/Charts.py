from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib.pyplot as plt
import numpy as np
import itertools


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, fig):
        self.fig = fig
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)

    def plot_confusion_matrix(self, cm, classes,
                              normalize=False,
                              title='Confusion matrix',
                              cmap=plt.get_cmap('Blues')):
        self.axes.imshow(cm, interpolation='nearest', cmap=cmap)
        self.axes.set_title(title, fontsize=12)
        tick_marks = np.arange(len(classes))
        self.axes.set_xticks(tick_marks)
        self.axes.set_yticks(tick_marks)
        self.axes.set_xticklabels(classes, fontsize=10)
        self.axes.set_yticklabels(classes, fontsize=10)
        thresh = cm.max() / 2.
        for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
            self.axes.text(j, i, format(cm[i, j]),
                           horizontalalignment="center",
                           color="white" if cm[i, j] > thresh else "black")
