import os
import json
import pandas as pd
import requests
from datetime import datetime
from pathlib import Path

# Create data directories
DATA_DIR = Path(__file__).parent.parent / 'data'
RAW_DIR = DATA_DIR / 'raw'
PROCESSED_DIR = DATA_DIR / 'processed'

for directory in [RAW_DIR, PROCESSED_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# NBA API endpoints
NBA_API_BASE = 'https://www.balldontlie.io/api/v1'
TEAMS_ENDPOINT = f"{NBA_API_BASE}/teams"
PLAYERS_ENDPOINT = f"{NBA_API_BASE}/players"
GAMES_ENDPOINT = f"{NBA_API_BASE}/games"


def fetch_data(url, params=None):
    """Generic function to fetch data from the API with error handling."""
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return None


def fetch_teams():
    """Fetch all NBA teams."""
    print("Fetching NBA teams...")
    data = fetch_data(TEAMS_ENDPOINT)
    if data and 'data' in data:
        df = pd.DataFrame(data['data'])
        # Save raw data
        df.to_csv(RAW_DIR / 'nba_teams_raw.csv', index=False)
        
        # Process and save clean data
        teams_df = df[['id', 'abbreviation', 'city', 'conference', 'division', 'full_name', 'name']]
        teams_df.rename(columns={
            'id': 'team_id',
            'abbreviation': 'abbr',
            'full_name': 'full_name',
            'name': 'short_name',
            'city': 'city',
            'conference': 'conference',
            'division': 'division'
        }, inplace=True)
        
        teams_df.to_csv(PROCESSED_DIR / 'teams.csv', index=False)
        print(f"Saved {len(teams_df)} teams to {PROCESSED_DIR / 'teams.csv'}")
        return teams_df
    return pd.DataFrame()


def fetch_players(per_page=100):
    """Fetch all NBA players with pagination."""
    print("Fetching NBA players...")
    all_players = []
    page = 0
    total_pages = 1  # Will be updated after first request
    
    while page < total_pages:
        page += 1
        params = {'per_page': per_page, 'page': page}
        data = fetch_data(PLAYERS_ENDPOINT, params=params)
        
        if not data or 'data' not in data:
            break
            
        all_players.extend(data['data'])
        total_pages = data['meta']['total_pages']
        print(f"Fetched page {page}/{total_pages} - {len(all_players)} players")
    
    if all_players:
        df = pd.DataFrame(all_players)
        # Save raw data
        df.to_csv(RAW_DIR / 'nba_players_raw.csv', index=False)
        
        # Process and save clean data
        players_df = pd.json_normalize(all_players)
        
        # Flatten the team data
        team_cols = ['team.id', 'team.abbreviation', 'team.city', 'team.conference', 
                    'team.division', 'team.full_name', 'team.name']
        
        # Ensure all team columns exist
        for col in team_cols:
            if col not in players_df.columns:
                players_df[col] = None
        
        # Rename columns
        players_df.rename(columns={
            'id': 'player_id',
            'first_name': 'first_name',
            'last_name': 'last_name',
            'position': 'position',
            'height_feet': 'height_ft',
            'height_inches': 'height_in',
            'weight_pounds': 'weight_lb',
            'team.id': 'team_id',
            'team.abbreviation': 'team_abbr',
            'team.city': 'team_city',
            'team.conference': 'team_conference',
            'team.division': 'team_division',
            'team.full_name': 'team_name',
            'team.name': 'team_short_name'
        }, inplace=True)
        
        # Select and reorder columns
        player_cols = [
            'player_id', 'first_name', 'last_name', 'position',
            'height_ft', 'height_in', 'weight_lb', 'team_id',
            'team_abbr', 'team_name', 'team_city', 'team_conference', 'team_division'
        ]
        players_df = players_df[player_cols]
        
        # Save to CSV
        players_df.to_csv(PROCESSED_DIR / 'players.csv', index=False)
        print(f"Saved {len(players_df)} players to {PROCESSED_DIR / 'players.csv'}")
        return players_df
    
    return pd.DataFrame()


def fetch_games(seasons=None, per_page=100):
    """Fetch NBA games for specific seasons."""
    if seasons is None:
        # Default to current season
        current_year = datetime.now().year
        seasons = [current_year - 1]  # Previous season
    
    all_games = []
    
    for season in seasons:
        print(f"Fetching games for {season}-{season+1} season...")
        page = 0
        total_pages = 1
        
        while page < total_pages:
            page += 1
            params = {
                'seasons[]': [season],
                'per_page': per_page,
                'page': page
            }
            
            data = fetch_data(GAMES_ENDPOINT, params=params)
            
            if not data or 'data' not in data:
                break
                
            all_games.extend(data['data'])
            total_pages = data['meta']['total_pages']
            print(f"Fetched page {page}/{total_pages} - {len(all_games)} games")
    
    if all_games:
        df = pd.DataFrame(all_games)
        # Save raw data
        df.to_csv(RAW_DIR / 'nba_games_raw.csv', index=False)
        
        # Process and save clean data
        games_df = df[[
            'id', 'date', 'season', 'home_team_score', 'visitor_team_score',
            'home_team.id', 'home_team.abbreviation', 'home_team.city',
            'visitor_team.id', 'visitor_team.abbreviation', 'visitor_team.city',
            'status', 'time', 'period', 'postseason'
        ]].copy()
        
        # Rename columns
        games_df.rename(columns={
            'id': 'game_id',
            'date': 'game_date',
            'season': 'season',
            'home_team_score': 'home_team_score',
            'visitor_team_score': 'away_team_score',
            'home_team.id': 'home_team_id',
            'home_team.abbreviation': 'home_team_abbr',
            'home_team.city': 'home_team_city',
            'visitor_team.id': 'away_team_id',
            'visitor_team.abbreviation': 'away_team_abbr',
            'visitor_team.city': 'away_team_city',
            'status': 'game_status',
            'time': 'game_time',
            'period': 'period',
            'postseason': 'is_playoff_game'
        }, inplace=True)
        
        # Convert date to datetime
        games_df['game_date'] = pd.to_datetime(games_df['game_date'])
        
        # Add result column
        games_df['home_team_won'] = games_df['home_team_score'] > games_df['away_team_score']
        
        # Save to CSV
        games_df.to_csv(PROCESSED_DIR / 'games.csv', index=False)
        print(f"Saved {len(games_df)} games to {PROCESSED_DIR / 'games.csv'}")
        return games_df
    
    return pd.DataFrame()


def main():
    """Main function to fetch all data."""
    print("Starting NBA data ingestion...")
    
    # Fetch teams data
    teams_df = fetch_teams()
    
    # Fetch players data
    players_df = fetch_players()
    
    # Fetch games for the last 3 seasons
    current_year = datetime.now().year
    seasons = list(range(current_year - 3, current_year))
    games_df = fetch_games(seasons=seasons)
    
    print("\nData ingestion complete!")
    print(f"- Teams: {len(teams_df)}")
    print(f"- Players: {len(players_df)}")
    print(f"- Games: {len(games_df) if games_df is not None else 0}")


if __name__ == "__main__":
    main()
