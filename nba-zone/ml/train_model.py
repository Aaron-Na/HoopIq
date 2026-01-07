"""
Train NBA game prediction model using scikit-learn.
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

MODEL_DIR = Path(__file__).parent / 'models'
DATA_DIR = Path(__file__).parent.parent / 'data' / 'processed'

MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Feature columns used for prediction
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
    """Train and evaluate multiple models."""
    models = {
        'logistic_regression': LogisticRegression(max_iter=1000, random_state=42),
        'random_forest': RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42),
        'gradient_boosting': GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
    }
    
    results = {}
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train, y_train)
        
        # Predictions
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        
        # Metrics
        accuracy = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
        
        results[name] = {
            'model': model,
            'accuracy': accuracy,
            'auc': auc,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std()
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
