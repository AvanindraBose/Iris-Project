import pandas as pd
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from training.train_utils import MODEL_FILE_PATH,MODEL_DIR_PATH
import joblib
import os

data = load_iris()
df = pd.DataFrame(
    data= data.data,
    columns= data.feature_names
)
df['target'] = data.target
df["species"] = df["target"].map(
    dict(enumerate(data.target_names))
)
df.drop_duplicates(inplace=True)
df = df.rename(columns = {
    'sepal length (cm)': 'sepal_length',
    'sepal width (cm)': 'sepal_width',
    'petal length (cm)': 'petal_length',
    'petal width (cm)': 'petal_width'
})

X = df.drop(columns=['target','species'])
y = df['target']

X_train,X_test,y_train,y_test = train_test_split(X,y, test_size=0.2,random_state=42)
rf = RandomForestClassifier()
rf.fit(X_train,y_train)

os.makedirs(MODEL_DIR_PATH,exist_ok=True)
joblib.dump(rf,MODEL_FILE_PATH)