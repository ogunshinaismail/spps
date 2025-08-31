import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, VotingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import pickle as pl
import os
from datetime import datetime
import time

# Use script's directory for robust file path handling
base_path = os.path.abspath(os.getcwd())

def model():
    # Load data
    data_path = f'{base_path}/app/ml/results.csv'
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found")
        exit(1)
    
    try:
        results = pd.read_csv(data_path).drop(columns=['total_score', 'weight', 'attendance', 'study_time'])
    except Exception as e:
        print(f"Error loading data: {e}")
        exit(1)

    # Check for required column
    if 'gpa' not in results.columns:
        print("Error: 'gpa' column not found in results.csv")
        exit(1)

    # Handle missing values
    if results.isnull().sum().any():
        print("Warning: Missing values detected. Filling with mean...")
        results = results.fillna(results.mean(numeric_only=True))

    print("Data preview:")
    print(results.head())

    print('View Correlation:')
    print(results.corr())
    # exit(1)

    # Split features and target
    X = results.drop(columns=['gpa'])
    y = results['gpa']
    print("X shape:", X.shape, "y shape:", y.shape)

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=1)

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Save scaler
    with open(f'{base_path}/api/scaler.pkl', 'wb') as f:
        pl.dump(scaler, f)

    # Expanded hyperparameter grid
    param_grid = {
        'rf__n_estimators': [100, 200, 300],
        'rf__max_depth': [None, 10, 20],
        'rf__min_samples_split': [2, 5, 10],
        'dt__max_depth': [None, 5, 10],
        'dt__min_samples_split': [2, 5, 10],
        'svr__C': [0.1, 1, 10],
        'svr__kernel': ['rbf'],
        'svr__gamma': ['scale', 'auto']
    }

    # Define ensemble
    ensemble = VotingRegressor(
        estimators=[
            ('rf', RandomForestRegressor()),
            ('lr', LinearRegression()),
            ('dt', DecisionTreeRegressor()),
            ('svr', SVR())
        ]
    )

    # Grid search with regression-appropriate scoring
    grid_search = GridSearchCV(
        ensemble, param_grid, cv=5, scoring='neg_mean_squared_error', n_jobs=-1, verbose=2
    )
    # grid_search = RandomizedSearchCV(ensemble, param_grid, n_iter=50, cv=5, scoring='neg_mean_squared_error', n_jobs=-1, verbose=2, random_state=42)

    # Fit grid search
    grid_search.fit(X_train_scaled, y_train)

    print("Best parameters:", grid_search.best_params_)
    print("Best cross-validation MSE:", -grid_search.best_score_)

    # Train final model
    model = grid_search.best_estimator_
    model.fit(X_train_scaled, y_train)

    # Save model
    with open(f'{base_path}/api/results.pkl', 'wb') as f:
        pl.dump(model, f)

    # Evaluate model
    y_pred = model.predict(X_test_scaled)
    print("Test MSE:", mean_squared_error(y_test, y_pred))
    print("Test MAE:", mean_absolute_error(y_test, y_pred))
    print("Test R²:", r2_score(y_test, y_pred))

if __name__ == "__main__":
    start_time = time.time()
    print(f"Starting training at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")
    model()
    training_time = (time.time() - start_time) / 60
    print(f"Training completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Training time: {training_time:.2f} minutes")