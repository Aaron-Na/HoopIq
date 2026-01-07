"""
Feature engineering for NBA game prediction model.
Extracts relevant features from game and team data.
Uses the historical_games_top10.csv data fetched from nba_api.
"""

import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'data'
RAW_DIR = DATA_DIR / 'raw'
PROCESSED_DIR = DATA_DIR / 'processed'


def load_games_data():
    """Load historical games data for top 10 teams."""
    # First try the top 10 historical data
    games_path = PROCESSED_DIR / 'historical_games_top10.csv'
    if games_path.exists():
        return pd.read_csv(games_path)
    
    # Fallback to raw games
    games_path = RAW_DIR / 'nba_games_raw.csv'
    if not games_path.exists():
        raise FileNotFoundError(f"Games data not found. Run fetch_schedule.py first.")
    return pd.read_csv(games_path)


def load_teams_data():
    """Load teams data."""
    teams_path = PROCESSED_DIR / 'top10_team_stats.csv'
    if teams_path.exists():
        return pd.read_csv(teams_path)
    
    teams_path = RAW_DIR / 'nba_teams_raw.csv'
    if not teams_path.exists():
        raise FileNotFoundError(f"Teams data not found at {teams_path}")
    return pd.read_csv(teams_path)


def calculate_team_stats(games_df, team_abbr, before_date, n_games=10):
    """
    Calculate rolling team statistics for the last n games before a given date.
    Uses the historical_games_top10.csv format where each row is a team's game record.
    """
    team_games = games_df[
        (games_df['team_abbr'] == team_abbr) &
        (games_df['game_date'] < before_date)
    ].sort_values('game_date', ascending=False).head(n_games)
    
    if len(team_games) == 0:
        return None
    
    n = len(team_games)
    wins = team_games['win'].sum()
    ppg = team_games['points'].mean()
    # Estimate opponent PPG from plus_minus
    opp_ppg = ppg - team_games['plus_minus'].mean()
    
    stats = {
        'games_played': n,
        'win_pct': wins / n,
        'ppg': ppg,
        'opp_ppg': opp_ppg,
        'point_diff': ppg - opp_ppg,
        'fg_pct': team_games['fg_pct'].mean(),
        'fg3_pct': team_games['fg3_pct'].mean(),
        'assists': team_games['assists'].mean(),
        'rebounds': team_games['rebounds'].mean(),
    }
    
    return stats


def create_game_features(games_df):
    """
    Create features for each game for model training.
    Uses the historical_games_top10.csv format.
    """
    features = []
    
    # Sort by date
    games_df = games_df.copy()
    games_df['game_date'] = pd.to_datetime(games_df['game_date'])
    games_df = games_df.sort_values('game_date')
    
    # Get unique games (each game has 2 rows - one per team)
    # Filter to only home games to avoid duplicates
    home_games = games_df[games_df['is_home'] == 1].copy()
    
    print(f"Processing {len(home_games)} home game records...")
    
    for idx, game in home_games.iterrows():
        home_team_abbr = game['team_abbr']
        away_team_abbr = game['opponent_abbr']
        game_date = game['game_date']
        game_id = game['game_id']
        
        # Get team stats before this game
        home_stats = calculate_team_stats(games_df, home_team_abbr, game_date)
        away_stats = calculate_team_stats(games_df, away_team_abbr, game_date)
        
        if home_stats is None or away_stats is None:
            continue
        
        # Home win is already in the data
        home_win = game['win']
        
        feature_row = {
            'game_id': game_id,
            'game_date': game_date,
            'home_team_abbr': home_team_abbr,
            'away_team_abbr': away_team_abbr,
            # Home team features
            'home_win_pct': home_stats['win_pct'],
            'home_ppg': home_stats['ppg'],
            'home_opp_ppg': home_stats['opp_ppg'],
            'home_point_diff': home_stats['point_diff'],
            # Away team features
            'away_win_pct': away_stats['win_pct'],
            'away_ppg': away_stats['ppg'],
            'away_opp_ppg': away_stats['opp_ppg'],
            'away_point_diff': away_stats['point_diff'],
            # Differential features
            'win_pct_diff': home_stats['win_pct'] - away_stats['win_pct'],
            'ppg_diff': home_stats['ppg'] - away_stats['ppg'],
            'point_diff_diff': home_stats['point_diff'] - away_stats['point_diff'],
            # Target
            'home_win': home_win,
        }
        
        features.append(feature_row)
    
    print(f"Created features for {len(features)} games")
    return pd.DataFrame(features)


def prepare_training_data():
    """
    Load data and prepare features for model training.
    """
    print("Loading games data...")
    games_df = load_games_data()
    
    print("Creating features...")
    features_df = create_game_features(games_df)
    
    # Save processed features
    output_path = PROCESSED_DIR / 'game_features.csv'
    features_df.to_csv(output_path, index=False)
    print(f"Saved features to {output_path}")
    
    return features_df


if __name__ == "__main__":
    prepare_training_data()
