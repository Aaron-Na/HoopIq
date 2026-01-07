export interface Team {
  id: number
  name: string
  city: string
  abbreviation: string
  conference: 'East' | 'West'
  division: string
  logo: string
  primaryColor: string
  secondaryColor: string
}

export interface Player {
  id: number
  firstName: string
  lastName: string
  team: string
  position: string
  jersey: number
  height: string
  weight: string
  college: string
  country: string
  ppg: number
  rpg: number
  apg: number
  image: string
}

export interface Game {
  id: number
  date: string
  homeTeam: Team
  awayTeam: Team
  homeScore?: number
  awayScore?: number
  status: 'scheduled' | 'live' | 'final'
}

export interface Prediction {
  gameId: number
  homeTeam: string
  awayTeam: string
  homeWinProbability: number
  awayWinProbability: number
  predictedWinner: string
  confidence: number
}
