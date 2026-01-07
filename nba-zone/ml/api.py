"""
Flask API for serving NBA game predictions.
This service can be called by the Spring Boot backend.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import joblib
from pathlib import Path

app = Flask(__name__)
CORS(app)

MODEL_DIR = Path(__file__).parent / 'models'
DATA_DIR = Path(__file__).parent.parent / 'data' / 'processed'

# Global model and scaler
model = None
scaler = None
team_stats_cache = {}


def load_team_stats():
    """Load team stats from CSV for lookups."""
    global team_stats_cache
    stats_path = DATA_DIR / 'top10_team_stats.csv'
    if stats_path.exists():
        import pandas as pd
        df = pd.read_csv(stats_path)
        for _, row in df.iterrows():
            team_stats_cache[row['abbr']] = {
                'abbreviation': row['abbr'],
                'win_pct': row['win_pct'],
                'ppg': row['ppg'],
                'opp_ppg': row['opp_ppg'],
                'point_diff': row['ppg'] - row['opp_ppg']
            }
        print(f"Loaded stats for {len(team_stats_cache)} teams")


def load_model():
    """Load the trained model and scaler."""
    global model, scaler
    
    model_path = MODEL_DIR / 'game_predictor.joblib'
    scaler_path = MODEL_DIR / 'game_predictor_scaler.joblib'
    
    if model_path.exists() and scaler_path.exists():
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        print(f"Model loaded from {model_path}")
        return True
    else:
        print("Warning: Model not found. Predictions will use fallback logic.")
        return False


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None
    })


@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict game outcome.
    
    Accepts either:
    1. Simple format: {"home_team": "BOS", "away_team": "NYK"}
    2. Full format with stats objects
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        home_team = data.get('home_team', {})
        away_team = data.get('away_team', {})
        
        # Handle simple string format (just abbreviations)
        if isinstance(home_team, str):
            home_team = team_stats_cache.get(home_team, {'abbreviation': home_team, 'win_pct': 0.5, 'ppg': 110, 'opp_ppg': 110, 'point_diff': 0})
        if isinstance(away_team, str):
            away_team = team_stats_cache.get(away_team, {'abbreviation': away_team, 'win_pct': 0.5, 'ppg': 110, 'opp_ppg': 110, 'point_diff': 0})
        
        # Extract stats with defaults
        home_stats = {
            'win_pct': home_team.get('win_pct', 0.5),
            'ppg': home_team.get('ppg', 110),
            'opp_ppg': home_team.get('opp_ppg', 110),
            'point_diff': home_team.get('point_diff', 0)
        }
        
        away_stats = {
            'win_pct': away_team.get('win_pct', 0.5),
            'ppg': away_team.get('ppg', 110),
            'opp_ppg': away_team.get('opp_ppg', 110),
            'point_diff': away_team.get('point_diff', 0)
        }
        
        if model is not None and scaler is not None:
            # Use trained model
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
            
            features_scaled = scaler.transform(features)
            probabilities = model.predict_proba(features_scaled)[0]
            
            home_win_prob = probabilities[1] * 100
            away_win_prob = probabilities[0] * 100
        else:
            # Fallback: simple heuristic based on win percentage and home advantage
            home_advantage = 0.03  # ~3% home court advantage
            base_prob = 0.5 + (home_stats['win_pct'] - away_stats['win_pct']) / 2 + home_advantage
            base_prob = max(0.2, min(0.8, base_prob))  # Clamp between 20-80%
            
            home_win_prob = base_prob * 100
            away_win_prob = (1 - base_prob) * 100
        
        predicted_winner = home_team.get('abbreviation', 'HOME') if home_win_prob > away_win_prob else away_team.get('abbreviation', 'AWAY')
        confidence = max(home_win_prob, away_win_prob)
        
        return jsonify({
            'home_team': home_team.get('abbreviation', 'HOME'),
            'away_team': away_team.get('abbreviation', 'AWAY'),
            'home_win_probability': round(home_win_prob, 1),
            'away_win_probability': round(away_win_prob, 1),
            'predicted_winner': predicted_winner,
            'confidence': round(confidence, 1),
            'model_used': 'ml_model' if model is not None else 'heuristic'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/batch_predict', methods=['POST'])
def batch_predict():
    """Predict multiple games at once."""
    try:
        data = request.get_json()
        games = data.get('games', [])
        
        predictions = []
        for game in games:
            # Reuse single prediction logic
            result = predict_single(game.get('home_team', {}), game.get('away_team', {}))
            result['game_id'] = game.get('game_id')
            predictions.append(result)
        
        return jsonify({'predictions': predictions})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def predict_single(home_team, away_team):
    """Helper function for single prediction."""
    home_stats = {
        'win_pct': home_team.get('win_pct', 0.5),
        'ppg': home_team.get('ppg', 110),
        'opp_ppg': home_team.get('opp_ppg', 110),
        'point_diff': home_team.get('point_diff', 0)
    }
    
    away_stats = {
        'win_pct': away_team.get('win_pct', 0.5),
        'ppg': away_team.get('ppg', 110),
        'opp_ppg': away_team.get('opp_ppg', 110),
        'point_diff': away_team.get('point_diff', 0)
    }
    
    if model is not None and scaler is not None:
        features = np.array([[
            home_stats['win_pct'], home_stats['ppg'], home_stats['opp_ppg'], home_stats['point_diff'],
            away_stats['win_pct'], away_stats['ppg'], away_stats['opp_ppg'], away_stats['point_diff'],
            home_stats['win_pct'] - away_stats['win_pct'],
            home_stats['ppg'] - away_stats['ppg'],
            home_stats['point_diff'] - away_stats['point_diff'],
        ]])
        features_scaled = scaler.transform(features)
        probabilities = model.predict_proba(features_scaled)[0]
        home_win_prob = probabilities[1] * 100
        away_win_prob = probabilities[0] * 100
    else:
        home_advantage = 0.03
        base_prob = 0.5 + (home_stats['win_pct'] - away_stats['win_pct']) / 2 + home_advantage
        base_prob = max(0.2, min(0.8, base_prob))
        home_win_prob = base_prob * 100
        away_win_prob = (1 - base_prob) * 100
    
    return {
        'home_team': home_team.get('abbreviation', 'HOME'),
        'away_team': away_team.get('abbreviation', 'AWAY'),
        'home_win_probability': round(home_win_prob, 1),
        'away_win_probability': round(away_win_prob, 1),
        'predicted_winner': home_team.get('abbreviation', 'HOME') if home_win_prob > away_win_prob else away_team.get('abbreviation', 'AWAY'),
        'confidence': round(max(home_win_prob, away_win_prob), 1)
    }


if __name__ == '__main__':
    load_team_stats()
    load_model()
    print("\nStarting ML Prediction API on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)
