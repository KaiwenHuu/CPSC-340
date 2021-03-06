import os
import pickle
import gzip
import argparse
import numpy as np
import math
import matplotlib.pyplot as plt

from sklearn.preprocessing import LabelBinarizer

from knn import KNN
import utils
import linear_model
import svm
import cnn
import nn


def load_dataset(filename):
    with open(os.path.join('..', 'data', filename), 'rb') as f:
        return pickle.load(f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--question', required=True)

    io_args = parser.parse_args()
    question = io_args.question

    if question == "knn":
        with gzip.open(os.path.join('..', 'data', 'mnist.pkl.gz'), 'rb') as f:
            train_set, valid_set, test_set = pickle.load(f, encoding="latin1")

        X, y = train_set
        Xtest, ytest = test_set
        binarizer = LabelBinarizer()

        Y = binarizer.fit_transform(y)

        N, D1 = X.shape  # X is a N by D1 matrix
        T, D2 = Xtest.shape  # Xtest is a T by D2 matrix

        K = np.arange(1, 10)
        test_errors = []

        for k in K:
            model = KNN(k)
            model.fit(X, y)
            i = 0
            test_error = []
            while i < Xtest.shape[0]:
                j = i + 1000
                temp = Xtest[i:j]
                pred = model.predict(temp)
                temp_e = np.mean(pred != ytest[i:j])
                test_error = np.append(test_error, temp_e)
                i = j
            e = np.mean(test_error)
            test_errors = np.append(test_errors, e)
            print("for k =", k, "test error %.4f" % e)
        plt.plot(K, test_errors, label="validation error")
        plt.title("KNN")
        plt.xlabel("K")
        plt.ylabel("Error")
        fname = os.path.join("..", "figs", "knn.pdf")
        plt.savefig(fname)
        print("\nFigure saved as '%s" % fname)


    elif question == "linear":
        with gzip.open(os.path.join('..', 'data', 'mnist.pkl.gz'), 'rb') as f:
            train_set, valid_set, test_set = pickle.load(f, encoding="latin1")
        X, y = train_set
        Xtest, ytest = test_set

        X = np.float32(X)
        y = np.float32(y)
        Xtest = np.float32(Xtest)
        ytest = np.float32(ytest)

        binarizer = LabelBinarizer()
        Y = binarizer.fit_transform(y)
        y_int = np.int32(y)

        lams = [2, 1.75, 1.5, 1.25, 1]
        test_error = []
        train_error = []

        train_bias = np.ones((X.shape[0], 1))
        test_bias = np.ones((Xtest.shape[0], 1))
        X = np.hstack((train_bias, X))
        Xtest = np.hstack((test_bias, Xtest))

        for lammy in lams:
            model = linear_model.softmaxClassifier(lammy=lammy, epochs=10, alpha=1, batch=5000)
            model.fit(X, y, Y)
            pred = model.predict(Xtest)
            e = utils.classification_error(ytest, pred)
            print("at lambda ", lammy, "validation error is ", e)
            test_error = np.append(test_error, e)
            pred = model.predict(X)
            e = utils.classification_error(y, pred)
            print("at lambda ", lammy, "train error is ", e)
            train_error = np.append(train_error, e)

        plt.plot(lams, test_error, label="validation error")
        plt.plot(lams, train_error, label="training error")
        plt.title("Multi-Class Linear Classifier")
        plt.xlabel("Lambda")
        plt.ylabel("Error")
        fname = os.path.join("..", "figs", "linear.pdf")
        plt.savefig(fname)
        print("\nFigure saved as '%s" % fname)


    elif question == "svm":
        with gzip.open(os.path.join('..', 'data', 'mnist.pkl.gz'), 'rb') as f:
            train_set, valid_set, test_set = pickle.load(f, encoding="latin1")
        X, y = train_set
        Xtest, ytest = test_set
        X = np.float32(X)
        y = np.float32(y)
        Xtest = np.float32(Xtest)
        ytest = np.float32(ytest)

        binarizer = LabelBinarizer()
        Y = binarizer.fit_transform(y)

        lams = [2, 1.75, 1.5, 1.25, 1]
        test_error = []
        train_error = []

        train_bias = np.ones((X.shape[0], 1))
        test_bias = np.ones((Xtest.shape[0], 1))
        X = np.hstack((train_bias, X))
        Xtest = np.hstack((test_bias, Xtest))

        for lammy in lams:
            model = svm.multiSVM(lammy=lammy, epochs=50, alpha=1, batch=5000)
            model.fit(X, y)
            pred = model.predict(Xtest)
            e = utils.classification_error(ytest, pred)
            print("at lambda ", lammy, "validation error is ", e)
            test_error = np.append(test_error, e)
            pred = model.predict(X)
            e = utils.classification_error(y, pred)
            print("at lambda ", lammy, "train error is ", e)
            train_error = np.append(train_error, e)

        plt.plot(lams, test_error, label="validation error")
        plt.plot(lams, train_error, label="training error")
        plt.title("Multi-Class SVM")
        plt.xlabel("Lambda")
        plt.ylabel("Error")
        fname = os.path.join("..", "figs", "svm.pdf")
        plt.savefig(fname)
        print("\nFigure saved as '%s" % fname)


    elif question == "mlp":
        with gzip.open(os.path.join('..', 'data', 'mnist.pkl.gz'), 'rb') as f:
            train_set, valid_set, test_set = pickle.load(f, encoding="latin1")
        X, y = train_set
        Xtest, ytest = test_set

        binarizer = LabelBinarizer()
        Y = binarizer.fit_transform(y)

        y = y.reshape(len(y), 1)
        ytest = ytest.reshape(len(ytest), 1)

        image_pixels = X.shape[1]
        k = len(np.unique(y))
        alpha = 0.01
        epochs = 20
        hidden_layer_size = [10, 100, 250, 500, 750]
        test_errors = []
        train_errors = []

        for h in hidden_layer_size:
            model = nn.NN(no_of_in_nodes=image_pixels, no_of_out_nodes=k, no_of_hidden_nodes=h, learning_rate=alpha,
                          bias=None)
            weights = model.fit(X, Y, epochs=epochs, intermediate_results=True)
            for i in range(epochs):
                print("epoch: ", i)
                model.wih = weights[i][0]
                model.who = weights[i][1]
                corrects, wrongs = model.evaluate(X, y)
                train_error = 1 - corrects / (corrects + wrongs)
                print("train error: ", train_error)
                corrects, wrongs = model.evaluate(Xtest, ytest)
                test_error = 1 - corrects / (corrects + wrongs)
                print("test error: ", test_error)
            test_errors = np.append(test_errors, test_error)
            train_errors = np.append(train_errors, train_error)
        plt.plot(hidden_layer_size, test_errors, label="validation error")
        plt.plot(hidden_layer_size, train_errors, label="training error")
        plt.title("Neural Network for One Hidden Layer")
        plt.xlabel("Hidden Layer Size")
        plt.ylabel("Error")
        fname = os.path.join("..", "figs", "mlp.pdf")
        plt.savefig(fname)
        print("\nFigure saved as '%s" % fname)

    elif question == "cnn":
        with gzip.open(os.path.join('..', 'data', 'mnist.pkl.gz'), 'rb') as f:
            train_set, valid_set, test_set = pickle.load(f, encoding="latin1")
        X, y = train_set
        Xtest, ytest = test_set

        binarizer = LabelBinarizer()
        Y = binarizer.fit_transform(y)

        y = y.reshape(len(y), 1)
        ytest = ytest.reshape(len(ytest), 1)

        model = cnn.CNN()
        model.fit(X, y)
        pred = model.predict(Xtest)
        error = utils.classification_error(pred, ytest)
        print("test error = %.4f" % error)

    else:
        print("Unknown question: %s" % question)
