const API_BASE_URL = '/api';

export interface Team {
  id: number;
  name: string;
  city: string;
  abbreviation: string;
  conference: string;
  division: string;
  logo: string;
  founded: number;
  championships: number;
}

export interface Player {
  id: number;
  firstName: string;
  lastName: string;
  team: Team;
  position: string;
  jerseyNumber: number;
  height: string;
  weight: string;
  college: string;
  country: string;
  ppg: number;
  rpg: number;
  apg: number;
  imageUrl: string;
  isActive: boolean;
}

export interface Prediction {
  id: number;
  homeTeam: string;
  awayTeam: string;
  homeWinProbability: number;
  awayWinProbability: number;
  predictedWinner: string;
  confidence: number;
}

export interface ScheduledGame {
  game_id: string;
  game_date: string;
  game_time: string;
  home_team_id: number;
  home_team_abbr: string;
  home_team_name: string;
  home_team_city: string;
  away_team_id: number;
  away_team_abbr: string;
  away_team_name: string;
  away_team_city: string;
  status: string;
}

export interface TeamStats {
  team_id: number;
  abbr: string;
  name: string;
  city: string;
  conference: string;
  wins: number;
  losses: number;
  win_pct: number;
  ppg: number;
  opp_ppg: number;
  fg_pct: number;
  fg3_pct: number;
  rpg: number;
  apg: number;
  games_played: number;
}

export interface PlayerStats {
  player_id: number;
  name: string;
  team_abbr: string;
  team_name: string;
  position: string;
  jersey: string;
  height: string;
  weight: string;
  age: string;
  experience: string;
  season: string;
  games_played: number;
  games_started: number;
  minutes: number;
  ppg: number;
  rpg: number;
  apg: number;
  spg: number;
  bpg: number;
  fg_pct: number;
  fg3_pct: number;
  ft_pct: number;
  turnovers: number;
}

export const api = {
  // Teams
  async getTeams(conference?: string, search?: string): Promise<Team[]> {
    const params = new URLSearchParams();
    if (conference) params.append('conference', conference);
    if (search) params.append('search', search);
    
    const url = `${API_BASE_URL}/teams${params.toString() ? '?' + params.toString() : ''}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch teams');
    return response.json();
  },

  async getTeamById(id: number): Promise<Team> {
    const response = await fetch(`${API_BASE_URL}/teams/${id}`);
    if (!response.ok) throw new Error('Failed to fetch team');
    return response.json();
  },

  // Players
  async getPlayers(position?: string, search?: string, teamId?: number): Promise<Player[]> {
    const params = new URLSearchParams();
    if (position) params.append('position', position);
    if (search) params.append('search', search);
    if (teamId) params.append('teamId', teamId.toString());
    
    const url = `${API_BASE_URL}/players${params.toString() ? '?' + params.toString() : ''}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch players');
    return response.json();
  },

  async getPlayerById(id: number): Promise<Player> {
    const response = await fetch(`${API_BASE_URL}/players/${id}`);
    if (!response.ok) throw new Error('Failed to fetch player');
    return response.json();
  },

  // Predictions
  async getPredictions(): Promise<Prediction[]> {
    const response = await fetch(`${API_BASE_URL}/predictions`);
    if (!response.ok) throw new Error('Failed to fetch predictions');
    return response.json();
  },

  // Schedule
  async getUpcomingGames(): Promise<ScheduledGame[]> {
    const response = await fetch(`${API_BASE_URL}/schedule/upcoming`);
    if (!response.ok) throw new Error('Failed to fetch upcoming games');
    return response.json();
  },

  async getTeamStats(): Promise<TeamStats[]> {
    const response = await fetch(`${API_BASE_URL}/schedule/team-stats`);
    if (!response.ok) throw new Error('Failed to fetch team stats');
    return response.json();
  },

  // Player Stats
  async getPlayerStats(): Promise<PlayerStats[]> {
    const response = await fetch(`${API_BASE_URL}/schedule/players`);
    if (!response.ok) throw new Error('Failed to fetch player stats');
    return response.json();
  },

  async getPlayersByTeam(teamAbbr: string): Promise<PlayerStats[]> {
    const response = await fetch(`${API_BASE_URL}/schedule/players/${teamAbbr}`);
    if (!response.ok) throw new Error('Failed to fetch team players');
    return response.json();
  },
};

export default api;
