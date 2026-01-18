import pandas as pd
import mlflow
import mlflow.sklearn

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

from hyperopt import hp, Trials, fmin, tpe, STATUS_OK

# ----------------------------
# Data preparation
# ----------------------------
data = load_iris()

df = pd.DataFrame(data.data, columns=data.feature_names)
df["target"] = data.target

df = df.rename(columns={
    "sepal length (cm)": "sepal_length",
    "sepal width (cm)": "sepal_width",
    "petal length (cm)": "petal_length",
    "petal width (cm)": "petal_width"
})

X = df.drop(columns=["target"])
y = df["target"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ----------------------------
# Hyperopt search space
# ----------------------------
spaces = {
    "n_estimators": hp.choice("n_estimators", list(range(100, 1000, 100))),
    "max_depth": hp.choice("max_depth", list(range(1, 20))),
    "min_samples_split": hp.choice("min_samples_split", list(range(2, 10))),
    "min_samples_leaf": hp.choice("min_samples_leaf", list(range(1, 5))),
}

# ----------------------------
# Objective function
# ----------------------------
def objective(params):

    with mlflow.start_run(nested=True):

        model = RandomForestClassifier(
            **params,
            random_state=42,
            n_jobs=-1
        )

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)

        mlflow.log_params(params)
        mlflow.log_metric("accuracy", accuracy)

        return {
            "loss": -accuracy,
            "status": STATUS_OK,
            "model": model
        }

# ----------------------------
# MLflow run
# ----------------------------
mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("Hyperopt Using MLflow")

trials = Trials()

with mlflow.start_run(run_name="Iris Hyperparameter Tuning"):

    fmin(
        fn=objective,
        space=spaces,
        algo=tpe.suggest,
        max_evals=100,
        trials=trials
    )

    # ----------------------------
    # Extract best model
    # ----------------------------
    best_trial = min(trials.results, key=lambda x: x["loss"])
    best_model = best_trial["model"]
    best_accuracy = -best_trial["loss"]

    mlflow.log_metric("best_accuracy", best_accuracy)

    # ----------------------------
    # Log best model ONLY
    # ----------------------------
    mlflow.sklearn.log_model(
        sk_model=best_model,
        artifact_path="model",
        registered_model_name="IrisRandomForest"
    )

