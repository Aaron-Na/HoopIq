"""
Flask API for serving NBA game predictions.
This service can be called by the Spring Boot backend.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import joblib
from pathlib import Path

# Initialize Flask application
# Flask is a lightweight WSGI (Web Server Gateway Interface) framework
# It handles routing HTTP requests to Python functions
app = Flask(__name__)

# Enable CORS (Cross-Origin Resource Sharing)
# This allows the React frontend (running on localhost:3000) to make
# requests to this API (running on localhost:5000)
# Without CORS, browsers block cross-origin requests for security
CORS(app)

# Path configuration using pathlib for cross-platform compatibility
# __file__ is the current script's path; .parent gets the directory
MODEL_DIR = Path(__file__).parent / 'models'
DATA_DIR = Path(__file__).parent.parent / 'data' / 'processed'

# Global variables for model state (module-level singletons)
# These are loaded once at startup and reused for all requests
# This avoids expensive disk I/O on every prediction request
model = None      # sklearn model object (LogisticRegression)
scaler = None     # sklearn StandardScaler for feature normalization
team_stats_cache = {}  # In-memory cache: team_abbr -> stats dict (O(1) lookup)


def load_team_stats():
    """
    Load team statistics from CSV into an in-memory hash map for O(1) lookups.
    
    This function populates the global team_stats_cache dictionary, which maps
    team abbreviations (e.g., 'BOS', 'LAL') to their statistical profiles.
    
    Data Structure:
        team_stats_cache = {
            'BOS': {'abbreviation': 'BOS', 'win_pct': 0.70, 'ppg': 118.5, ...},
            'NYK': {'abbreviation': 'NYK', 'win_pct': 0.62, 'ppg': 115.2, ...},
            ...
        }
    
    Time Complexity: O(n) where n = number of teams
    Space Complexity: O(n) for the cache
    """
    global team_stats_cache  # Declare intent to modify global variable
    stats_path = DATA_DIR / 'top10_team_stats.csv'
    
    if stats_path.exists():
        import pandas as pd
        df = pd.read_csv(stats_path)  # Load CSV into DataFrame (tabular data structure)
        
        # Iterate through DataFrame rows and build cache
        # iterrows() returns (index, Series) tuples
        for _, row in df.iterrows():
            # Create a dictionary for each team with relevant stats
            # point_diff (point differential) is a key predictor of team strength
            team_stats_cache[row['abbr']] = {
                'abbreviation': row['abbr'],
                'win_pct': row['win_pct'],      # Win percentage (0.0 to 1.0)
                'ppg': row['ppg'],              # Points per game (offensive strength)
                'opp_ppg': row['opp_ppg'],      # Opponent PPG (defensive strength)
                'point_diff': row['ppg'] - row['opp_ppg']  # Net rating proxy
            }
        print(f"Loaded stats for {len(team_stats_cache)} teams")


def load_model():
    """
    Load the trained ML model and feature scaler from disk.
    
    Machine Learning Pipeline:
    1. Features are extracted from team statistics
    2. Scaler normalizes features to zero mean, unit variance (StandardScaler)
    3. Model (LogisticRegression) outputs probability of home team winning
    
    Why use joblib?
    - joblib is optimized for serializing numpy arrays (used by sklearn)
    - More efficient than pickle for large numerical data
    - Preserves the exact model state from training
    
    Returns:
        bool: True if model loaded successfully, False otherwise
    """
    global model, scaler  # Modify global state
    
    model_path = MODEL_DIR / 'game_predictor.joblib'
    scaler_path = MODEL_DIR / 'game_predictor_scaler.joblib'
    
    # Check if both files exist before attempting to load
    # Both are required: model for predictions, scaler for feature normalization
    if model_path.exists() and scaler_path.exists():
        # joblib.load() deserializes the Python object from disk
        # This reconstructs the exact sklearn model with trained weights
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
    Main prediction endpoint - predicts the outcome of an NBA game.
    
    HTTP Method: POST
    Content-Type: application/json
    
    Request Body Formats:
        1. Simple: {"home_team": "BOS", "away_team": "NYK"}
        2. Full:   {"home_team": {...stats...}, "away_team": {...stats...}}
    
    Response:
        {
            "home_team": "BOS",
            "away_team": "NYK", 
            "home_win_probability": 62.5,
            "away_win_probability": 37.5,
            "predicted_winner": "BOS",
            "confidence": 62.5,
            "model_used": "ml_model" | "heuristic"
        }
    
    Algorithm:
        If ML model is loaded:
            1. Extract 11 features from team stats
            2. Normalize features using StandardScaler
            3. Pass through LogisticRegression.predict_proba()
        Else (fallback heuristic):
            1. Calculate base probability from win percentage difference
            2. Add 3% home court advantage
            3. Clamp result between 20-80%
    """
    try:
        # Parse JSON request body
        # Flask's request.get_json() automatically deserializes JSON to Python dict
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract team data from request (could be string or dict)
        home_team = data.get('home_team', {})
        away_team = data.get('away_team', {})
        
        # Handle simple string format (just abbreviations like "BOS")
        # If string, look up full stats from cache; if not found, use defaults
        # This is a form of the Null Object pattern - provide sensible defaults
        if isinstance(home_team, str):
            home_team = team_stats_cache.get(home_team, {'abbreviation': home_team, 'win_pct': 0.5, 'ppg': 110, 'opp_ppg': 110, 'point_diff': 0})
        if isinstance(away_team, str):
            away_team = team_stats_cache.get(away_team, {'abbreviation': away_team, 'win_pct': 0.5, 'ppg': 110, 'opp_ppg': 110, 'point_diff': 0})
        
        # Extract stats with defaults using dict.get() for safe access
        # Default values represent a league-average team
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
            # ============ ML MODEL PREDICTION ============
            # Create feature vector as 2D numpy array (required by sklearn)
            # Shape: (1, 11) - 1 sample with 11 features
            # Features include: raw stats + derived differential features
            features = np.array([[
                home_stats['win_pct'],       # Feature 0: Home win %
                home_stats['ppg'],           # Feature 1: Home PPG
                home_stats['opp_ppg'],       # Feature 2: Home defensive rating
                home_stats['point_diff'],    # Feature 3: Home net rating
                away_stats['win_pct'],       # Feature 4: Away win %
                away_stats['ppg'],           # Feature 5: Away PPG
                away_stats['opp_ppg'],       # Feature 6: Away defensive rating
                away_stats['point_diff'],    # Feature 7: Away net rating
                # Derived features (differences capture relative strength)
                home_stats['win_pct'] - away_stats['win_pct'],      # Feature 8
                home_stats['ppg'] - away_stats['ppg'],              # Feature 9
                home_stats['point_diff'] - away_stats['point_diff'], # Feature 10
            ]])
            
            # StandardScaler.transform(): z = (x - mean) / std
            # This normalizes features to have mean=0, variance=1
            # Critical for LogisticRegression which is sensitive to feature scales
            features_scaled = scaler.transform(features)
            
            # predict_proba() returns array of shape (n_samples, n_classes)
            # For binary classification: [[P(class=0), P(class=1)]]
            # class 0 = away win, class 1 = home win
            probabilities = model.predict_proba(features_scaled)[0]
            
            # Convert to percentages (0-100 scale)
            home_win_prob = probabilities[1] * 100  # P(home wins)
            away_win_prob = probabilities[0] * 100  # P(away wins)
        else:
            # ============ HEURISTIC FALLBACK ============
            # Used when ML model is not available
            # Based on empirical NBA research on home court advantage
            home_advantage = 0.03  # ~3% home court advantage (NBA average)
            
            # Linear interpolation between win percentages
            # If teams have equal win%, base_prob = 0.5 + 0.03 = 0.53 (slight home edge)
            base_prob = 0.5 + (home_stats['win_pct'] - away_stats['win_pct']) / 2 + home_advantage
            
            # Clamp probability to reasonable range [0.2, 0.8]
            # Prevents extreme predictions (no team has <20% or >80% chance)
            # max(0.2, min(0.8, x)) is equivalent to: clamp(x, 0.2, 0.8)
            base_prob = max(0.2, min(0.8, base_prob))
            
            home_win_prob = base_prob * 100
            away_win_prob = (1 - base_prob) * 100  # Probabilities must sum to 100%
        
        # Determine predicted winner (team with higher probability)
        # Ternary operator: value_if_true if condition else value_if_false
        predicted_winner = home_team.get('abbreviation', 'HOME') if home_win_prob > away_win_prob else away_team.get('abbreviation', 'AWAY')
        
        # Confidence = probability of predicted winner (always >= 50%)
        confidence = max(home_win_prob, away_win_prob)
        
        # Return JSON response with prediction results
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
        # Return 500 Internal Server Error with error message
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
