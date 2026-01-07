"""
Prediction service for NBA game outcomes.
Loads trained model and provides prediction functions.
"""

import numpy as np
import joblib
from pathlib import Path

MODEL_DIR = Path(__file__).parent / 'models'

# Feature columns (must match training)
FEATURE_COLS = [
    'home_win_pct', 'home_ppg', 'home_opp_ppg', 'home_point_diff',
    'away_win_pct', 'away_ppg', 'away_opp_ppg', 'away_point_diff',
    'win_pct_diff', 'ppg_diff', 'point_diff_diff'
]


class GamePredictor:
    """NBA Game Prediction Model."""
    
    def __init__(self, model_name='game_predictor'):
        self.model_path = MODEL_DIR / f'{model_name}.joblib'
        self.scaler_path = MODEL_DIR / f'{model_name}_scaler.joblib'
        self.model = None
        self.scaler = None
        self._load_model()
    
    def _load_model(self):
        """Load trained model and scaler."""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found at {self.model_path}. Train the model first.")
        
        self.model = joblib.load(self.model_path)
        self.scaler = joblib.load(self.scaler_path)
        print(f"Loaded model from {self.model_path}")
    
    def predict(self, home_stats: dict, away_stats: dict) -> dict:
        """
        Predict game outcome given team statistics.
        
        Args:
            home_stats: dict with keys: win_pct, ppg, opp_ppg, point_diff
            away_stats: dict with keys: win_pct, ppg, opp_ppg, point_diff
        
        Returns:
            dict with prediction results
        """
        # Create feature vector
        features = np.array([[
            home_stats['win_pct'],
            home_stats['ppg'],
            home_stats['opp_ppg'],
            home_stats['point_diff'],
            away_stats['win_pct'],
            away_stats['ppg'],
            away_stats['opp_ppg'],
            away_stats['point_diff'],
            home_stats['win_pct'] - away_stats['win_pct'],
            home_stats['ppg'] - away_stats['ppg'],
            home_stats['point_diff'] - away_stats['point_diff'],
        ]])
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Get prediction and probabilities
        prediction = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]
        
        home_win_prob = probabilities[1] * 100
        away_win_prob = probabilities[0] * 100
        
        return {
            'home_win_probability': round(home_win_prob, 1),
            'away_win_probability': round(away_win_prob, 1),
            'predicted_winner': 'home' if prediction == 1 else 'away',
            'confidence': round(max(home_win_prob, away_win_prob), 1)
        }


def predict_game(home_team_stats: dict, away_team_stats: dict) -> dict:
    """
    Convenience function to predict a single game.
    
    Example:
        home_stats = {'win_pct': 0.65, 'ppg': 115.2, 'opp_ppg': 108.5, 'point_diff': 6.7}
        away_stats = {'win_pct': 0.55, 'ppg': 110.8, 'opp_ppg': 109.2, 'point_diff': 1.6}
        result = predict_game(home_stats, away_stats)
    """
    predictor = GamePredictor()
    return predictor.predict(home_team_stats, away_team_stats)


if __name__ == "__main__":
    # Example prediction
    print("Example Game Prediction")
    print("=" * 40)
    
    # Lakers vs Celtics example
    home_stats = {
        'win_pct': 0.58,
        'ppg': 117.2,
        'opp_ppg': 115.5,
        'point_diff': 1.7
    }
    
    away_stats = {
        'win_pct': 0.65,
        'ppg': 120.1,
        'opp_ppg': 110.8,
        'point_diff': 9.3
    }
    
    try:
        result = predict_game(home_stats, away_stats)
        print(f"\nHome Team Win Probability: {result['home_win_probability']}%")
        print(f"Away Team Win Probability: {result['away_win_probability']}%")
        print(f"Predicted Winner: {result['predicted_winner'].upper()}")
        print(f"Confidence: {result['confidence']}%")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run train_model.py first to train the model.")
