from lib2to3.pytree import LeafPattern
#import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score
from sklearn.mixture import GaussianMixture

iris = sns.load_dataset('iris')
print(iris.head())

#sns.pairplot(iris, hue='species', height=1.5)
#plt.show()

# extract feature matrix and target array
x_iris = iris.drop('species', axis=1)
print("x_iris shape:", x_iris.shape)
y_iris = iris['species']
print("y_iris shape:", y_iris.shape)

# split train and test
x_train, x_test, y_train, y_test = train_test_split(x_iris, y_iris, random_state=1)

# choose model - Gaussian Naive Bayes supervised learnig
model = GaussianNB()
# fit model to data
model.fit(x_train, y_train)
# predict on new data
y_model = model.predict(x_test)
print(y_model)

# how close was the model?
print("accuracy score:", accuracy_score(y_test, y_model))

# unsupervised learning - GMM

u_model = GaussianMixture(n_components=3, covariance_type='full')
u_model.fit(x_iris) # y is not specified!
y_gmm = model.predict(x_iris)
print(y_gmm)
print("accuracy score:", accuracy_score(y_iris, y_gmm))

#iris['cluster'] = y_gmm
#sns.lmplot("PCA1", "PCA2", data=iris, hue='species', col='cluster', fit_reg=False)
#plt.show()