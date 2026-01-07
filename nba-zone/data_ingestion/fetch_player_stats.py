"""
Fetch player stats for top 10 NBA teams using nba_api
"""
import pandas as pd
import time
from pathlib import Path
from nba_api.stats.endpoints import commonteamroster, playercareerstats
from nba_api.stats.static import teams

# Top 10 teams
TOP_10_TEAMS = {
    'BOS': 'Boston Celtics',
    'OKC': 'Oklahoma City Thunder', 
    'CLE': 'Cleveland Cavaliers',
    'NYK': 'New York Knicks',
    'MIL': 'Milwaukee Bucks',
    'MIA': 'Miami Heat',
    'DEN': 'Denver Nuggets',
    'DAL': 'Dallas Mavericks',
    'MIN': 'Minnesota Timberwolves',
    'PHX': 'Phoenix Suns'
}

# Data directories
DATA_DIR = Path(__file__).parent.parent / 'data'
PLAYERS_DIR = DATA_DIR / 'players'
PLAYERS_DIR.mkdir(parents=True, exist_ok=True)

def get_team_id(abbr: str) -> int:
    """Get team ID from abbreviation"""
    all_teams = teams.get_teams()
    for team in all_teams:
        if team['abbreviation'] == abbr:
            return team['id']
    return None

def fetch_team_roster(team_id: int, season: str = '2024-25') -> pd.DataFrame:
    """Fetch roster for a team"""
    try:
        roster = commonteamroster.CommonTeamRoster(team_id=team_id, season=season)
        df = roster.get_data_frames()[0]
        return df
    except Exception as e:
        print(f"Error fetching roster for team {team_id}: {e}")
        return pd.DataFrame()

def fetch_player_career_stats(player_id: int) -> dict:
    """Fetch career stats for a player, return current season stats"""
    try:
        career = playercareerstats.PlayerCareerStats(player_id=player_id)
        df = career.get_data_frames()[0]  # SeasonTotalsRegularSeason
        
        # Get most recent season
        if len(df) > 0:
            latest = df.iloc[-1]
            games = latest.get('GP', 0)
            if games > 0:
                return {
                    'season': latest.get('SEASON_ID', 'N/A'),
                    'team_abbr': latest.get('TEAM_ABBREVIATION', 'N/A'),
                    'games_played': int(games),
                    'games_started': int(latest.get('GS', 0)),
                    'minutes': round(latest.get('MIN', 0) / games, 1) if games > 0 else 0,
                    'ppg': round(latest.get('PTS', 0) / games, 1) if games > 0 else 0,
                    'rpg': round(latest.get('REB', 0) / games, 1) if games > 0 else 0,
                    'apg': round(latest.get('AST', 0) / games, 1) if games > 0 else 0,
                    'spg': round(latest.get('STL', 0) / games, 1) if games > 0 else 0,
                    'bpg': round(latest.get('BLK', 0) / games, 1) if games > 0 else 0,
                    'fg_pct': round(latest.get('FG_PCT', 0) * 100, 1),
                    'fg3_pct': round(latest.get('FG3_PCT', 0) * 100, 1),
                    'ft_pct': round(latest.get('FT_PCT', 0) * 100, 1),
                    'turnovers': round(latest.get('TOV', 0) / games, 1) if games > 0 else 0,
                }
        return None
    except Exception as e:
        print(f"Error fetching stats for player {player_id}: {e}")
        return None

def fetch_all_player_stats():
    """Fetch player stats for all top 10 teams"""
    all_players = []
    
    for abbr, team_name in TOP_10_TEAMS.items():
        print(f"\nFetching roster for {team_name} ({abbr})...")
        team_id = get_team_id(abbr)
        
        if not team_id:
            print(f"  Could not find team ID for {abbr}")
            continue
        
        # Fetch roster
        roster = fetch_team_roster(team_id)
        time.sleep(0.6)  # Rate limiting
        
        if roster.empty:
            print(f"  No roster data for {team_name}")
            continue
        
        print(f"  Found {len(roster)} players")
        
        # Fetch stats for each player
        for _, player in roster.iterrows():
            player_id = player.get('PLAYER_ID')
            player_name = player.get('PLAYER', 'Unknown')
            position = player.get('POSITION', 'N/A')
            jersey = player.get('NUM', 'N/A')
            height = player.get('HEIGHT', 'N/A')
            weight = player.get('WEIGHT', 'N/A')
            age = player.get('AGE', 'N/A')
            exp = player.get('EXP', 'R')  # R for Rookie
            
            print(f"    Fetching stats for {player_name}...")
            stats = fetch_player_career_stats(player_id)
            time.sleep(0.6)  # Rate limiting
            
            player_data = {
                'player_id': player_id,
                'name': player_name,
                'team_abbr': abbr,
                'team_name': team_name,
                'position': position,
                'jersey': jersey,
                'height': height,
                'weight': weight,
                'age': age,
                'experience': exp if exp != 'R' else '0',
            }
            
            if stats:
                player_data.update(stats)
            else:
                # Default stats for players without data
                player_data.update({
                    'season': '2024-25',
                    'games_played': 0,
                    'games_started': 0,
                    'minutes': 0,
                    'ppg': 0,
                    'rpg': 0,
                    'apg': 0,
                    'spg': 0,
                    'bpg': 0,
                    'fg_pct': 0,
                    'fg3_pct': 0,
                    'ft_pct': 0,
                    'turnovers': 0,
                })
            
            all_players.append(player_data)
    
    return pd.DataFrame(all_players)

def main():
    print("=" * 60)
    print("Fetching Player Stats for Top 10 NBA Teams")
    print("=" * 60)
    
    # Fetch all player stats
    df = fetch_all_player_stats()
    
    if df.empty:
        print("\nNo player data fetched!")
        return
    
    print(f"\n{'=' * 60}")
    print(f"Total players fetched: {len(df)}")
    
    # Save to CSV
    csv_path = PLAYERS_DIR / 'top10_player_stats.csv'
    df.to_csv(csv_path, index=False)
    print(f"Saved to: {csv_path}")
    
    # Save to JSON for backend
    json_path = PLAYERS_DIR / 'top10_player_stats.json'
    df.to_json(json_path, orient='records', indent=2)
    print(f"Saved to: {json_path}")
    
    # Print summary by team
    print(f"\n{'=' * 60}")
    print("Players per team:")
    for abbr in TOP_10_TEAMS.keys():
        team_players = df[df['team_abbr'] == abbr]
        if not team_players.empty:
            top_scorer = team_players.loc[team_players['ppg'].idxmax()]
            print(f"  {abbr}: {len(team_players)} players | Top scorer: {top_scorer['name']} ({top_scorer['ppg']} PPG)")

if __name__ == '__main__':
    main()
