"""
Fetch NBA 2025-2026 schedule for top 10 teams.
Uses nba_api to get upcoming games and team standings.
"""

import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder, scoreboardv2, teamgamelog, leaguestandings
from nba_api.stats.static import teams
from datetime import datetime, timedelta
from pathlib import Path
import time
import json

# Create data directories
DATA_DIR = Path(__file__).parent.parent / 'data'
RAW_DIR = DATA_DIR / 'raw'
PROCESSED_DIR = DATA_DIR / 'processed'
SCHEDULE_DIR = DATA_DIR / 'schedule'

for directory in [RAW_DIR, PROCESSED_DIR, SCHEDULE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

DELAY = 0.6  # seconds between API calls

# Top 10 teams for 2025-2026 season (based on current standings/projections)
TOP_10_TEAMS = [
    {'abbr': 'BOS', 'name': 'Celtics', 'city': 'Boston', 'conference': 'East'},
    {'abbr': 'OKC', 'name': 'Thunder', 'city': 'Oklahoma City', 'conference': 'West'},
    {'abbr': 'CLE', 'name': 'Cavaliers', 'city': 'Cleveland', 'conference': 'East'},
    {'abbr': 'DEN', 'name': 'Nuggets', 'city': 'Denver', 'conference': 'West'},
    {'abbr': 'NYK', 'name': 'Knicks', 'city': 'New York', 'conference': 'East'},
    {'abbr': 'DAL', 'name': 'Mavericks', 'city': 'Dallas', 'conference': 'West'},
    {'abbr': 'MIL', 'name': 'Bucks', 'city': 'Milwaukee', 'conference': 'East'},
    {'abbr': 'MIN', 'name': 'Timberwolves', 'city': 'Minnesota', 'conference': 'West'},
    {'abbr': 'PHX', 'name': 'Suns', 'city': 'Phoenix', 'conference': 'West'},
    {'abbr': 'MIA', 'name': 'Heat', 'city': 'Miami', 'conference': 'East'},
]

# Team ID mapping
def get_team_id_map():
    """Get mapping of team abbreviation to team ID."""
    nba_teams = teams.get_teams()
    return {team['abbreviation']: team['id'] for team in nba_teams}


def get_team_stats_2025():
    """
    Get current 2025-2026 season stats for top 10 teams.
    Returns win/loss records, PPG, opponent PPG, etc.
    """
    print("Fetching 2025-2026 season team stats...")
    
    team_id_map = get_team_id_map()
    team_stats = []
    
    for team_info in TOP_10_TEAMS:
        abbr = team_info['abbr']
        team_id = team_id_map.get(abbr)
        
        if not team_id:
            print(f"  Warning: Could not find team ID for {abbr}")
            continue
        
        print(f"  Fetching stats for {abbr}...")
        
        try:
            # Get team game log for current season
            gamelog = teamgamelog.TeamGameLog(
                team_id=team_id,
                season='2025-26',
                season_type_all_star='Regular Season'
            )
            time.sleep(DELAY)
            
            games_df = gamelog.get_data_frames()[0]
            
            if not games_df.empty:
                # Calculate stats
                wins = len(games_df[games_df['WL'] == 'W'])
                losses = len(games_df[games_df['WL'] == 'L'])
                ppg = games_df['PTS'].mean()
                opp_ppg = games_df['PTS'].mean() - games_df['PLUS_MINUS'].mean()  # Approximate
                fg_pct = games_df['FG_PCT'].mean()
                fg3_pct = games_df['FG3_PCT'].mean()
                reb = games_df['REB'].mean()
                ast = games_df['AST'].mean()
                
                team_stats.append({
                    'team_id': team_id,
                    'abbr': abbr,
                    'name': team_info['name'],
                    'city': team_info['city'],
                    'conference': team_info['conference'],
                    'wins': wins,
                    'losses': losses,
                    'win_pct': wins / (wins + losses) if (wins + losses) > 0 else 0.5,
                    'ppg': round(ppg, 1),
                    'opp_ppg': round(opp_ppg, 1),
                    'fg_pct': round(fg_pct * 100, 1),
                    'fg3_pct': round(fg3_pct * 100, 1),
                    'rpg': round(reb, 1),
                    'apg': round(ast, 1),
                    'games_played': len(games_df)
                })
                print(f"    {abbr}: {wins}-{losses}, PPG: {ppg:.1f}")
            else:
                # No games yet, use projected stats
                team_stats.append(get_projected_stats(team_info, team_id))
                
        except Exception as e:
            print(f"    Error fetching stats for {abbr}: {e}")
            # Use projected stats as fallback
            team_stats.append(get_projected_stats(team_info, team_id))
    
    # Save to CSV
    stats_df = pd.DataFrame(team_stats)
    stats_df.to_csv(PROCESSED_DIR / 'top10_team_stats.csv', index=False)
    print(f"\nSaved stats for {len(team_stats)} teams")
    
    return team_stats


def get_projected_stats(team_info, team_id):
    """Get projected stats for a team (used when real data unavailable)."""
    # Projected stats based on preseason expectations
    projections = {
        'BOS': {'win_pct': 0.70, 'ppg': 120.5, 'opp_ppg': 110.2},
        'OKC': {'win_pct': 0.68, 'ppg': 118.8, 'opp_ppg': 109.5},
        'CLE': {'win_pct': 0.66, 'ppg': 116.2, 'opp_ppg': 108.8},
        'DEN': {'win_pct': 0.64, 'ppg': 117.5, 'opp_ppg': 111.2},
        'NYK': {'win_pct': 0.62, 'ppg': 115.8, 'opp_ppg': 110.5},
        'DAL': {'win_pct': 0.60, 'ppg': 118.2, 'opp_ppg': 113.1},
        'MIL': {'win_pct': 0.58, 'ppg': 119.5, 'opp_ppg': 114.2},
        'MIN': {'win_pct': 0.56, 'ppg': 112.8, 'opp_ppg': 108.5},
        'PHX': {'win_pct': 0.55, 'ppg': 116.5, 'opp_ppg': 113.8},
        'MIA': {'win_pct': 0.54, 'ppg': 111.2, 'opp_ppg': 109.5},
    }
    
    proj = projections.get(team_info['abbr'], {'win_pct': 0.50, 'ppg': 110, 'opp_ppg': 110})
    
    return {
        'team_id': team_id,
        'abbr': team_info['abbr'],
        'name': team_info['name'],
        'city': team_info['city'],
        'conference': team_info['conference'],
        'wins': 0,
        'losses': 0,
        'win_pct': proj['win_pct'],
        'ppg': proj['ppg'],
        'opp_ppg': proj['opp_ppg'],
        'fg_pct': 47.5,
        'fg3_pct': 37.0,
        'rpg': 44.0,
        'apg': 26.0,
        'games_played': 0
    }


def get_recent_games(days_back=7):
    """Get recent games involving top 10 teams."""
    print(f"\nFetching games from the last {days_back} days...")
    
    team_id_map = get_team_id_map()
    top_team_ids = {team_id_map.get(t['abbr']) for t in TOP_10_TEAMS if team_id_map.get(t['abbr'])}
    
    all_games = []
    
    try:
        # Get games using LeagueGameFinder
        gamefinder = leaguegamefinder.LeagueGameFinder(
            season_nullable='2025-26',
            season_type_nullable='Regular Season',
            league_id_nullable='00'
        )
        time.sleep(DELAY)
        
        games_df = gamefinder.get_data_frames()[0]
        
        if not games_df.empty:
            # Filter for recent games
            games_df['GAME_DATE'] = pd.to_datetime(games_df['GAME_DATE'])
            cutoff_date = datetime.now() - timedelta(days=days_back)
            recent_games = games_df[games_df['GAME_DATE'] >= cutoff_date]
            
            # Filter for top 10 teams
            recent_games = recent_games[recent_games['TEAM_ID'].isin(top_team_ids)]
            
            print(f"  Found {len(recent_games)} recent game records for top 10 teams")
            
            # Save raw data
            recent_games.to_csv(RAW_DIR / 'recent_games_raw.csv', index=False)
            
            return recent_games
            
    except Exception as e:
        print(f"  Error fetching recent games: {e}")
    
    return pd.DataFrame()


def fetch_real_schedule_until_allstar():
    """
    Fetch REAL NBA schedule for games between top 10 teams
    from today until February 15, 2026 (All-Star break).
    Uses the NBA CDN schedule endpoint for future games.
    """
    import requests
    
    print("\nFetching REAL NBA schedule for top 10 teams until All-Star break (Feb 15)...")
    
    team_id_map = get_team_id_map()
    top_team_abbrs = {t['abbr'] for t in TOP_10_TEAMS}
    
    # Create mapping for team info lookup
    team_info_map = {t['abbr']: t for t in TOP_10_TEAMS}
    
    # Also create ID to abbr mapping
    id_to_abbr = {}
    for t in TOP_10_TEAMS:
        tid = team_id_map.get(t['abbr'])
        if tid:
            id_to_abbr[tid] = t['abbr']
    
    upcoming_games = []
    seen_game_ids = set()
    
    today = datetime.now()
    allstar_date = datetime(2026, 2, 15)
    
    print(f"  Date range: {today.strftime('%Y-%m-%d')} to {allstar_date.strftime('%Y-%m-%d')}")
    
    # Try to fetch from NBA schedule API
    try:
        # NBA schedule endpoint (this returns the full season schedule)
        schedule_url = "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.nba.com/'
        }
        
        print("  Fetching NBA schedule from CDN...")
        response = requests.get(schedule_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Parse the schedule
            game_dates = data.get('leagueSchedule', {}).get('gameDates', [])
            
            for game_date_obj in game_dates:
                date_str = game_date_obj.get('gameDate', '')
                
                # Parse date
                try:
                    game_date = datetime.strptime(date_str, '%m/%d/%Y %H:%M:%S')
                except:
                    try:
                        game_date = datetime.strptime(date_str.split()[0], '%m/%d/%Y')
                    except:
                        continue
                
                # Check date range
                if game_date.date() < today.date() or game_date.date() > allstar_date.date():
                    continue
                
                # Process games on this date
                games = game_date_obj.get('games', [])
                
                for game in games:
                    game_id = game.get('gameId', '')
                    
                    if game_id in seen_game_ids:
                        continue
                    
                    home_team = game.get('homeTeam', {})
                    away_team = game.get('awayTeam', {})
                    
                    home_abbr = home_team.get('teamTricode', '')
                    away_abbr = away_team.get('teamTricode', '')
                    
                    # Only include games where BOTH teams are in top 10
                    if home_abbr not in top_team_abbrs or away_abbr not in top_team_abbrs:
                        continue
                    
                    seen_game_ids.add(game_id)
                    
                    # Get game time
                    game_time_utc = game.get('gameDateTimeUTC', '')
                    game_time_et = game.get('gameTimeET', '7:30 PM ET')
                    if not game_time_et:
                        game_time_et = '7:30 PM ET'
                    
                    home_info = team_info_map.get(home_abbr, {'name': home_abbr, 'city': ''})
                    away_info = team_info_map.get(away_abbr, {'name': away_abbr, 'city': ''})
                    
                    upcoming_games.append({
                        'game_id': game_id,
                        'game_date': game_date.strftime('%Y-%m-%d'),
                        'game_time': game_time_et,
                        'home_team_id': team_id_map.get(home_abbr),
                        'home_team_abbr': home_abbr,
                        'home_team_name': home_info.get('name', home_abbr),
                        'home_team_city': home_info.get('city', ''),
                        'away_team_id': team_id_map.get(away_abbr),
                        'away_team_abbr': away_abbr,
                        'away_team_name': away_info.get('name', away_abbr),
                        'away_team_city': away_info.get('city', ''),
                        'status': 'Scheduled'
                    })
            
            print(f"  Found {len(upcoming_games)} games from NBA CDN")
        else:
            print(f"  CDN request failed with status {response.status_code}")
            
    except Exception as e:
        print(f"  Error fetching from CDN: {e}")
    
    # If CDN didn't work, try alternative approach with team schedules
    if len(upcoming_games) == 0:
        print("  Trying team schedule endpoints...")
        upcoming_games = fetch_team_schedules(today, allstar_date, top_team_abbrs, team_id_map, team_info_map)
    
    # Sort by date
    upcoming_games.sort(key=lambda x: x['game_date'])
    
    print(f"\n  Found {len(upcoming_games)} real games between top 10 teams until All-Star break")
    
    # Save schedule
    schedule_df = pd.DataFrame(upcoming_games)
    schedule_df.to_csv(SCHEDULE_DIR / 'upcoming_games.csv', index=False)
    
    with open(SCHEDULE_DIR / 'upcoming_games.json', 'w') as f:
        json.dump(upcoming_games, f, indent=2)
    
    print(f"Saved {len(upcoming_games)} upcoming games")
    
    # Print summary
    if upcoming_games:
        print("\n  Games by matchup:")
        matchup_counts = {}
        for game in upcoming_games:
            matchup = f"{game['away_team_abbr']} @ {game['home_team_abbr']}"
            matchup_counts[matchup] = matchup_counts.get(matchup, 0) + 1
        for matchup, count in sorted(matchup_counts.items()):
            print(f"    {matchup}: {count}")
    
    return upcoming_games


def fetch_team_schedules(start_date, end_date, top_team_abbrs, team_id_map, team_info_map):
    """
    Fetch schedule for each team individually from NBA CDN.
    """
    import requests
    
    upcoming_games = []
    seen_game_ids = set()
    
    for team_info in TOP_10_TEAMS:
        abbr = team_info['abbr']
        team_id = team_id_map.get(abbr)
        
        if not team_id:
            continue
        
        print(f"    Fetching schedule for {abbr}...")
        
        try:
            # Team schedule endpoint
            url = f"https://cdn.nba.com/static/json/staticData/scheduleLeagueV2_{team_id}.json"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                continue
            
            data = response.json()
            games = data.get('leagueSchedule', {}).get('gameDates', [])
            
            for game_date_obj in games:
                date_str = game_date_obj.get('gameDate', '')
                
                try:
                    game_date = datetime.strptime(date_str.split()[0], '%m/%d/%Y')
                except:
                    continue
                
                if game_date.date() < start_date.date() or game_date.date() > end_date.date():
                    continue
                
                for game in game_date_obj.get('games', []):
                    game_id = game.get('gameId', '')
                    
                    if game_id in seen_game_ids:
                        continue
                    
                    home_abbr = game.get('homeTeam', {}).get('teamTricode', '')
                    away_abbr = game.get('awayTeam', {}).get('teamTricode', '')
                    
                    if home_abbr not in top_team_abbrs or away_abbr not in top_team_abbrs:
                        continue
                    
                    seen_game_ids.add(game_id)
                    
                    home_info = team_info_map.get(home_abbr, {'name': home_abbr, 'city': ''})
                    away_info = team_info_map.get(away_abbr, {'name': away_abbr, 'city': ''})
                    
                    upcoming_games.append({
                        'game_id': game_id,
                        'game_date': game_date.strftime('%Y-%m-%d'),
                        'game_time': game.get('gameTimeET', '7:30 PM ET') or '7:30 PM ET',
                        'home_team_id': team_id_map.get(home_abbr),
                        'home_team_abbr': home_abbr,
                        'home_team_name': home_info.get('name', home_abbr),
                        'home_team_city': home_info.get('city', ''),
                        'away_team_id': team_id_map.get(away_abbr),
                        'away_team_abbr': away_abbr,
                        'away_team_name': away_info.get('name', away_abbr),
                        'away_team_city': away_info.get('city', ''),
                        'status': 'Scheduled'
                    })
            
            time.sleep(DELAY)
            
        except Exception as e:
            print(f"      Error: {e}")
    
    return upcoming_games


def fetch_schedule_from_gamefinder(start_date, end_date, top_team_abbrs, team_id_map, team_info_map):
    """
    Alternative method to fetch schedule using LeagueGameFinder.
    This gets games that have already been played in the current season.
    """
    print("  Fetching from LeagueGameFinder...")
    
    upcoming_games = []
    
    try:
        gamefinder = leaguegamefinder.LeagueGameFinder(
            season_nullable='2025-26',
            season_type_nullable='Regular Season',
            league_id_nullable='00'
        )
        time.sleep(DELAY)
        
        games_df = gamefinder.get_data_frames()[0]
        
        if games_df.empty:
            print("    No games found")
            return upcoming_games
        
        # Process games
        games_df['GAME_DATE'] = pd.to_datetime(games_df['GAME_DATE'])
        
        # Group by game_id to get both teams
        seen_game_ids = set()
        
        for _, game in games_df.iterrows():
            game_id = game['GAME_ID']
            
            if game_id in seen_game_ids:
                continue
            
            team_abbr = game['TEAM_ABBREVIATION']
            matchup = game['MATCHUP']
            game_date = game['GAME_DATE']
            
            # Check date range
            if game_date.date() < start_date.date() or game_date.date() > end_date.date():
                continue
            
            # Parse matchup
            is_home = 'vs.' in matchup
            if 'vs.' in matchup:
                opponent_abbr = matchup.split('vs.')[-1].strip()
            elif '@' in matchup:
                opponent_abbr = matchup.split('@')[-1].strip()
            else:
                continue
            
            # Only include games between top 10 teams
            if team_abbr not in top_team_abbrs or opponent_abbr not in top_team_abbrs:
                continue
            
            seen_game_ids.add(game_id)
            
            if is_home:
                home_abbr = team_abbr
                away_abbr = opponent_abbr
            else:
                home_abbr = opponent_abbr
                away_abbr = team_abbr
            
            home_info = team_info_map.get(home_abbr, {})
            away_info = team_info_map.get(away_abbr, {})
            
            upcoming_games.append({
                'game_id': game_id,
                'game_date': game_date.strftime('%Y-%m-%d'),
                'game_time': '7:30 PM ET',
                'home_team_id': team_id_map.get(home_abbr),
                'home_team_abbr': home_abbr,
                'home_team_name': home_info.get('name', home_abbr),
                'home_team_city': home_info.get('city', ''),
                'away_team_id': team_id_map.get(away_abbr),
                'away_team_abbr': away_abbr,
                'away_team_name': away_info.get('name', away_abbr),
                'away_team_city': away_info.get('city', ''),
                'status': 'Scheduled'
            })
        
        upcoming_games.sort(key=lambda x: x['game_date'])
        print(f"    Found {len(upcoming_games)} games from GameFinder")
        
    except Exception as e:
        print(f"    Error: {e}")
    
    return upcoming_games


def generate_upcoming_schedule():
    """
    Wrapper function that fetches real schedule.
    Falls back to generated schedule if API fails.
    """
    return fetch_real_schedule_until_allstar()


def get_historical_games_for_training(seasons=None):
    """
    Fetch historical games for ML training.
    Gets games from specified seasons for top 10 teams.
    """
    if seasons is None:
        seasons = ['2024-25', '2023-24', '2022-23']
    
    print(f"\nFetching historical games for ML training...")
    print(f"Seasons: {seasons}")
    
    team_id_map = get_team_id_map()
    top_team_ids = {team_id_map.get(t['abbr']) for t in TOP_10_TEAMS if team_id_map.get(t['abbr'])}
    
    all_games = []
    
    for season in seasons:
        print(f"\n  Fetching {season} season...")
        
        try:
            gamefinder = leaguegamefinder.LeagueGameFinder(
                season_nullable=season,
                season_type_nullable='Regular Season',
                league_id_nullable='00'
            )
            time.sleep(DELAY)
            
            games_df = gamefinder.get_data_frames()[0]
            
            if not games_df.empty:
                # Filter for top 10 teams
                team_games = games_df[games_df['TEAM_ID'].isin(top_team_ids)]
                team_games = team_games.copy()
                team_games['SEASON'] = season
                all_games.append(team_games)
                print(f"    Found {len(team_games)} game records")
                
        except Exception as e:
            print(f"    Error fetching {season}: {e}")
    
    if all_games:
        combined_df = pd.concat(all_games, ignore_index=True)
        
        # Process for ML training
        processed = combined_df[[
            'GAME_ID', 'GAME_DATE', 'SEASON', 'TEAM_ID', 'TEAM_ABBREVIATION',
            'MATCHUP', 'WL', 'PTS', 'FG_PCT', 'FT_PCT', 'FG3_PCT',
            'AST', 'REB', 'STL', 'BLK', 'TOV', 'PLUS_MINUS'
        ]].copy()
        
        processed.columns = [
            'game_id', 'game_date', 'season', 'team_id', 'team_abbr',
            'matchup', 'win_loss', 'points', 'fg_pct', 'ft_pct', 'fg3_pct',
            'assists', 'rebounds', 'steals', 'blocks', 'turnovers', 'plus_minus'
        ]
        
        # Add home/away flag
        processed['is_home'] = processed['matchup'].str.contains('vs.').astype(int)
        
        # Extract opponent
        processed['opponent_abbr'] = processed['matchup'].apply(
            lambda x: x.split(' ')[-1] if isinstance(x, str) else ''
        )
        
        # Convert win/loss to binary
        processed['win'] = (processed['win_loss'] == 'W').astype(int)
        
        # Save
        processed.to_csv(PROCESSED_DIR / 'historical_games_top10.csv', index=False)
        print(f"\nSaved {len(processed)} historical game records for training")
        
        return processed
    
    return pd.DataFrame()


def main():
    """Main function to fetch all schedule data."""
    print("=" * 60)
    print("NBA 2025-2026 Schedule Fetcher - Top 10 Teams")
    print("=" * 60)
    
    # 1. Get team stats
    team_stats = get_team_stats_2025()
    
    # 2. Get recent games
    recent_games = get_recent_games(days_back=14)
    
    # 3. Generate upcoming schedule
    upcoming = generate_upcoming_schedule()
    
    # 4. Get historical data for ML training
    historical = get_historical_games_for_training()
    
    print("\n" + "=" * 60)
    print("Schedule fetch complete!")
    print(f"- Team stats: {len(team_stats)} teams")
    print(f"- Recent games: {len(recent_games)} records")
    print(f"- Upcoming games: {len(upcoming)} games")
    print(f"- Historical games: {len(historical)} records")
    print("=" * 60)


if __name__ == "__main__":
    main()
