"""
Code to train a small chatbot, a copus is used which is a set of yaml files.
We use the sklearn library by creating a pipeline with TfidfVectorizer plus
a classifier which can be SVC, RandomForestClassifier or logistic regression.
The model is then saved with joblib to be loaded later.
"""
import joblib
import numpy as np
from nltk.data import find
from nltk.tokenize import word_tokenize

from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer



# Pipeline: TfidfVectorizer + Something
pipeline = Pipeline([
    ("vectorizer", TfidfVectorizer()),
    #("classifier", RandomForestClassifier(n_estimators=200, max_depth=50, class_weight="balanced")),
    #("classifier", LogisticRegression(C=1.0, solver='liblinear', max_iter=10000)),
    ("classifier", SVC(kernel='linear', C=1.0, probability=True)),
])

Data_train = np.load('/home/BOT/AISF-PISA-BOT/corpus/train_dataset.npz')
X_train = Data_train["X"]
y_train = Data_train["y"]

# Train the model
pipeline.fit(X_train, y_train)

# Save model
path = r'/home/BOT/AISF-PISA-BOT/mod.sav'
joblib.dump(pipeline, path)
