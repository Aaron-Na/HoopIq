"""
Train NBA Game Prediction Model using scikit-learn.

This script implements a supervised machine learning pipeline for binary classification:
- Input: Team statistics (features)
- Output: Probability of home team winning (binary: 0 or 1)

Machine Learning Concepts Used:
1. Feature Engineering: Converting raw stats into predictive features
2. Train/Test Split: Evaluating model on unseen data to detect overfitting
3. Cross-Validation: K-fold CV for robust performance estimation
4. Model Selection: Comparing multiple algorithms to find the best
5. Feature Scaling: StandardScaler normalizes features for gradient-based models
6. Model Persistence: Saving trained model to disk with joblib

Models Evaluated:
- Logistic Regression: Linear model, fast, interpretable, good baseline
- Random Forest: Ensemble of decision trees, handles non-linear relationships
- Gradient Boosting: Sequential ensemble, often highest accuracy

Evaluation Metrics:
- Accuracy: % of correct predictions (can be misleading for imbalanced data)
- AUC-ROC: Area Under ROC Curve, measures ranking quality (0.5 = random, 1.0 = perfect)
- Cross-Validation: Average accuracy across K folds (reduces variance in estimate)

Author: HoopIQ Team
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
import joblib
from pathlib import Path

# Directory paths for model storage and data access
MODEL_DIR = Path(__file__).parent / 'models'
DATA_DIR = Path(__file__).parent.parent / 'data' / 'processed'

# Create models directory if it doesn't exist
# exist_ok=True prevents error if directory already exists
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Feature columns used for prediction (must match feature engineering output)
# These are the 11 features our model expects:
# - 4 home team stats (win%, ppg, opp_ppg, point_diff)
# - 4 away team stats (same metrics)
# - 3 differential features (home - away for key metrics)
FEATURE_COLS = [
    'home_win_pct', 'home_ppg', 'home_opp_ppg', 'home_point_diff',
    'away_win_pct', 'away_ppg', 'away_opp_ppg', 'away_point_diff',
    'win_pct_diff', 'ppg_diff', 'point_diff_diff'
]


def load_features():
    """Load processed game features."""
    features_path = DATA_DIR / 'game_features.csv'
    if not features_path.exists():
        print("Features file not found. Running feature engineering...")
        from feature_engineering import prepare_training_data
        return prepare_training_data()
    return pd.read_csv(features_path)


def train_models(X_train, X_test, y_train, y_test):
    """
    Train and evaluate multiple ML models using the same train/test split.
    
    This implements a model comparison strategy where we:
    1. Train each model on the same training data
    2. Evaluate on the same test data
    3. Perform cross-validation for robust estimates
    
    Parameters:
        X_train: Training features, shape (n_train_samples, n_features)
        X_test: Test features, shape (n_test_samples, n_features)
        y_train: Training labels, shape (n_train_samples,)
        y_test: Test labels, shape (n_test_samples,)
    
    Returns:
        dict: Model name -> {model, accuracy, auc, cv_mean, cv_std}
    """
    # Dictionary of models to evaluate
    # random_state=42 ensures reproducibility (same random splits each run)
    models = {
        # Logistic Regression: P(y=1|x) = sigmoid(w·x + b)
        # max_iter=1000 allows convergence for complex datasets
        'logistic_regression': LogisticRegression(max_iter=1000, random_state=42),
        
        # Random Forest: Ensemble of 100 decision trees
        # max_depth=10 prevents overfitting (limits tree complexity)
        # Each tree trained on bootstrap sample (bagging)
        'random_forest': RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42),
        
        # Gradient Boosting: Sequential ensemble that corrects previous errors
        # Each tree fits the residual errors of the ensemble so far
        # Generally achieves highest accuracy but slower to train
        'gradient_boosting': GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
    }
    
    results = {}
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        
        # fit() learns the model parameters from training data
        # For LogisticRegression: learns weights w and bias b
        # For tree ensembles: learns tree structures and split thresholds
        model.fit(X_train, y_train)
        
        # Generate predictions on test set
        y_pred = model.predict(X_test)  # Hard predictions: 0 or 1
        y_prob = model.predict_proba(X_test)[:, 1]  # Soft predictions: P(home_win)
        
        # Calculate evaluation metrics
        # Accuracy = (TP + TN) / (TP + TN + FP + FN)
        accuracy = accuracy_score(y_test, y_pred)
        
        # AUC-ROC: Area under Receiver Operating Characteristic curve
        # Measures how well model ranks positive examples above negative
        # 0.5 = random guessing, 1.0 = perfect ranking
        auc = roc_auc_score(y_test, y_prob)
        
        # K-Fold Cross-Validation (K=5)
        # Splits training data into 5 folds, trains on 4, validates on 1
        # Repeats 5 times, each fold used as validation once
        # Returns array of 5 accuracy scores
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
        
        results[name] = {
            'model': model,
            'accuracy': accuracy,
            'auc': auc,
            'cv_mean': cv_scores.mean(),  # Average CV accuracy
            'cv_std': cv_scores.std()     # Standard deviation (measures stability)
        }
        
        print(f"  Accuracy: {accuracy:.4f}")
        print(f"  AUC: {auc:.4f}")
        print(f"  CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    
    return results


def select_best_model(results):
    """Select the best model based on AUC score."""
    best_name = max(results, key=lambda x: results[x]['auc'])
    return best_name, results[best_name]['model']


def save_model(model, scaler, name='game_predictor'):
    """Save trained model and scaler."""
    model_path = MODEL_DIR / f'{name}.joblib'
    scaler_path = MODEL_DIR / f'{name}_scaler.joblib'
    
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    
    print(f"\nModel saved to {model_path}")
    print(f"Scaler saved to {scaler_path}")


def main():
    print("=" * 50)
    print("NBA Game Prediction Model Training")
    print("=" * 50)
    
    # Load data
    print("\nLoading features...")
    df = load_features()
    print(f"Loaded {len(df)} games with features")
    
    # Prepare features and target
    X = df[FEATURE_COLS].values
    y = df['home_win'].values
    
    # Handle any NaN values
    X = np.nan_to_num(X, nan=0.0)
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Split data (time-based would be better, but using random for simplicity)
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )
    
    print(f"\nTraining set: {len(X_train)} games")
    print(f"Test set: {len(X_test)} games")
    print(f"Home win rate in training: {y_train.mean():.2%}")
    
    # Train models
    results = train_models(X_train, X_test, y_train, y_test)
    
    # Select best model
    best_name, best_model = select_best_model(results)
    print(f"\n{'=' * 50}")
    print(f"Best model: {best_name}")
    print(f"Test Accuracy: {results[best_name]['accuracy']:.4f}")
    print(f"Test AUC: {results[best_name]['auc']:.4f}")
    
    # Save best model
    save_model(best_model, scaler)
    
    # Print feature importance for tree-based models
    if hasattr(best_model, 'feature_importances_'):
        print("\nFeature Importance:")
        importance = pd.DataFrame({
            'feature': FEATURE_COLS,
            'importance': best_model.feature_importances_
        }).sort_values('importance', ascending=False)
        print(importance.to_string(index=False))
    
    return best_model, scaler


if __name__ == "__main__":
    main()
