import os
import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder, commonteamroster, playergamelog
from nba_api.stats.static import teams, players
from datetime import datetime
from pathlib import Path
import time

# Create data directories
DATA_DIR = Path(__file__).parent.parent / 'data'
RAW_DIR = DATA_DIR / 'raw'
PROCESSED_DIR = DATA_DIR / 'processed'

for directory in [RAW_DIR, PROCESSED_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Add delay between API calls to avoid rate limiting
DELAY = 0.6  # seconds

def get_teams():
    """Fetch all NBA teams."""
    print("Fetching NBA teams...")
    nba_teams = teams.get_teams()
    teams_df = pd.DataFrame(nba_teams)
    
    # Save raw data
    teams_df.to_csv(RAW_DIR / 'nba_teams_raw.csv', index=False)
    
    # Process and save clean data
    teams_clean = teams_df[[
        'id', 'abbreviation', 'nickname', 'city', 'full_name', 'state', 'year_founded'
    ]].copy()
    
    teams_clean.rename(columns={
        'id': 'team_id',
        'abbreviation': 'abbr',
        'nickname': 'name',
        'full_name': 'full_name',
        'city': 'city',
        'state': 'state',
        'year_founded': 'founded'
    }, inplace=True)
    
    teams_clean.to_csv(PROCESSED_DIR / 'teams.csv', index=False)
    print(f"Saved {len(teams_clean)} teams to {PROCESSED_DIR / 'teams.csv'}")
    return teams_clean

def get_players():
    """Fetch all NBA players."""
    print("Fetching NBA players...")
    nba_players = players.get_players()
    players_df = pd.DataFrame(nba_players)
    
    # Save raw data
    players_df.to_csv(RAW_DIR / 'nba_players_raw.csv', index=False)
    
    # Process and save clean data
    players_clean = players_df[[
        'id', 'full_name', 'first_name', 'last_name', 'is_active'
    ]].copy()
    
    players_clean.rename(columns={
        'id': 'player_id',
        'full_name': 'full_name',
        'first_name': 'first_name',
        'last_name': 'last_name',
        'is_active': 'is_active'
    }, inplace=True)
    
    # Add current team information (simplified - in a real app, you'd want to get this from a roster)
    players_clean['current_team_id'] = None
    players_clean['current_team_abbr'] = None
    
    players_clean.to_csv(PROCESSED_DIR / 'players.csv', index=False)
    print(f"Saved {len(players_clean)} players to {PROCESSED_DIR / 'players.csv'}")
    return players_clean

def get_games(seasons=None):
    """Fetch NBA games for specific seasons."""
    if seasons is None:
        # Default to current season
        current_year = datetime.now().year
        seasons = [current_year - 1]  # Previous season
    
    all_games = []
    
    # Convert seasons to the format expected by the API (e.g., '2022-23' for 2022-23 season)
    for season in seasons:
        season_str = f"{season}-{str(season+1)[-2:]}"
        print(f"Fetching games for {season_str} season...")
        
        # Get all games for the season
        # Note: The NBA API doesn't support direct season filtering in LeagueGameFinder
        # So we'll get all games and filter by season later
        gamefinder = leaguegamefinder.LeagueGameFinder(
            season_type_nullable='Regular Season'
        )
        
        # Add delay to avoid rate limiting
        time.sleep(DELAY)
        
        games = gamefinder.get_data_frames()[0]
        
        # Filter for the specific season
        games = games[games['SEASON_ID'].str.endswith(str(season + 1)[2:])]
        
        if not games.empty:
            games['SEASON'] = f"{season}-{str(season+1)[-2:]}"
            all_games.append(games)
    
    if all_games:
        games_df = pd.concat(all_games, ignore_index=True)
        
        # Save raw data
        games_df.to_csv(RAW_DIR / 'nba_games_raw.csv', index=False)
        
        # Process and save clean data
        games_clean = games_df[[
            'GAME_ID', 'GAME_DATE', 'SEASON', 'MATCHUP', 'TEAM_ID', 'TEAM_ABBREVIATION',
            'TEAM_NAME', 'WL', 'PTS', 'FG_PCT', 'FT_PCT', 'FG3_PCT', 'AST', 'REB', 'TOV'
        ]].copy()
        
        games_clean.rename(columns={
            'GAME_ID': 'game_id',
            'GAME_DATE': 'game_date',
            'SEASON': 'season',
            'MATCHUP': 'matchup',
            'TEAM_ID': 'team_id',
            'TEAM_ABBREVIATION': 'team_abbr',
            'TEAM_NAME': 'team_name',
            'WL': 'win_loss',
            'PTS': 'points',
            'FG_PCT': 'fg_pct',
            'FT_PCT': 'ft_pct',
            'FG3_PCT': 'fg3_pct',
            'AST': 'assists',
            'REB': 'rebounds',
            'TOV': 'turnovers'
        }, inplace=True)
        
        # Convert date to datetime
        games_clean['game_date'] = pd.to_datetime(games_clean['game_date'])
        
        # Add a flag for home/away
        games_clean['is_home'] = games_clean['matchup'].str.contains('vs').astype(int)
        
        # Extract opponent team abbreviation
        games_clean['opponent_abbr'] = games_clean['matchup'].str[-3:]
        
        games_clean.to_csv(PROCESSED_DIR / 'games.csv', index=False)
        print(f"Saved {len(games_clean)} games to {PROCESSED_DIR / 'games.csv'}")
        return games_clean
    
    return pd.DataFrame()

def get_team_rosters(season=None):
    """Fetch rosters for all teams for a specific season."""
    if season is None:
        season = datetime.now().year
    
    # Get all teams
    nba_teams = teams.get_teams()
    all_rosters = []
    
    print(f"Fetching rosters for the {season}-{season+1} season...")
    
    for team in nba_teams:
        team_id = team['id']
        team_abbr = team['abbreviation']
        
        print(f"  - Fetching roster for {team_abbr}...")
        
        try:
            roster = commonteamroster.CommonTeamRoster(
                team_id=team_id,
                season=season
            )
            
            # Add delay to avoid rate limiting
            time.sleep(DELAY)
            
            roster_df = roster.get_data_frames()[0]
            
            if not roster_df.empty:
                roster_df['TEAM_ID'] = team_id
                roster_df['TEAM_ABBR'] = team_abbr
                all_rosters.append(roster_df)
                
        except Exception as e:
            print(f"    Error fetching roster for {team_abbr}: {e}")
    
    if all_rosters:
        rosters_df = pd.concat(all_rosters, ignore_index=True)
        
        # Save raw data
        rosters_df.to_csv(RAW_DIR / 'nba_rosters_raw.csv', index=False)
        
        # Process and save clean data
        # Define the columns we want to keep
        columns_to_keep = [
            'TeamID', 'PLAYER_ID', 'PLAYER', 'NICKNAME', 'NUM', 'POSITION',
            'HEIGHT', 'WEIGHT', 'BIRTH_DATE', 'AGE', 'EXP', 'SCHOOL'
        ]
        
        # Only include columns that exist in the DataFrame
        available_columns = [col for col in columns_to_keep if col in rosters_df.columns]
        
        # Create a copy with only the available columns
        rosters_clean = rosters_df[available_columns].copy()
        
        # Define the column mapping
        column_mapping = {
            'TeamID': 'team_id',
            'PLAYER_ID': 'player_id',
            'PLAYER': 'player_name',
            'NICKNAME': 'nickname',
            'NUM': 'jersey_number',
            'POSITION': 'position',
            'HEIGHT': 'height',
            'WEIGHT': 'weight',
            'BIRTH_DATE': 'birth_date',
            'AGE': 'age',
            'EXP': 'years_experience',
            'SCHOOL': 'college'
        }
        
        # Only include columns that exist in the DataFrame
        column_mapping = {k: v for k, v in column_mapping.items() if k in rosters_clean.columns}
        
        # Rename the columns
        rosters_clean.rename(columns=column_mapping, inplace=True)
        
        rosters_clean.to_csv(PROCESSED_DIR / 'rosters.csv', index=False)
        print(f"Saved rosters for {len(all_rosters)} teams to {PROCESSED_DIR / 'rosters.csv'}")
        return rosters_clean
    
    return pd.DataFrame()

def main():
    """Main function to fetch all data."""
    print("Starting NBA data ingestion...")
    
    # Get current season (e.g., 2023 for 2023-24 season)
    current_year = datetime.now().year
    
    # Fetch data
    teams_df = get_teams()
    players_df = get_players()
    
    # Get games for the last 3 seasons
    seasons = list(range(current_year - 3, current_year + 1))
    games_df = get_games(seasons=seasons)
    
    # Get rosters for the current season
    rosters_df = get_team_rosters(season=current_year)
    
    print("\nData ingestion complete!")
    print(f"- Teams: {len(teams_df)}")
    print(f"- Players: {len(players_df)}")
    print(f"- Games: {len(games_df) if games_df is not None else 0}")
    print(f"- Rosters: {len(rosters_df) if rosters_df is not None else 0} players")


if __name__ == "__main__":
    main()
