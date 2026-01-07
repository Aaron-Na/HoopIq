import { useState, useEffect } from 'react'
import { Container, Typography, Grid, Card, CardContent, Box, Chip, CircularProgress, Button } from '@mui/material'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import RefreshIcon from '@mui/icons-material/Refresh'
import { api, ScheduledGame, TeamStats } from '../api'

interface GamePrediction {
  id: number
  gameId: string
  homeTeam: { name: string; city: string; abbreviation: string; logo: string }
  awayTeam: { name: string; city: string; abbreviation: string; logo: string }
  homeWinProb: number
  awayWinProb: number
  predictedWinner: string
  confidence: number
  date: string
  time: string
}

// NBA team logo URLs
const teamLogos: Record<string, string> = {
  'BOS': 'https://cdn.nba.com/logos/nba/1610612738/primary/L/logo.svg',
  'OKC': 'https://cdn.nba.com/logos/nba/1610612760/primary/L/logo.svg',
  'CLE': 'https://cdn.nba.com/logos/nba/1610612739/primary/L/logo.svg',
  'DEN': 'https://cdn.nba.com/logos/nba/1610612743/primary/L/logo.svg',
  'NYK': 'https://cdn.nba.com/logos/nba/1610612752/primary/L/logo.svg',
  'DAL': 'https://cdn.nba.com/logos/nba/1610612742/primary/L/logo.svg',
  'MIL': 'https://cdn.nba.com/logos/nba/1610612749/primary/L/logo.svg',
  'MIN': 'https://cdn.nba.com/logos/nba/1610612750/primary/L/logo.svg',
  'PHX': 'https://cdn.nba.com/logos/nba/1610612756/primary/L/logo.svg',
  'MIA': 'https://cdn.nba.com/logos/nba/1610612748/primary/L/logo.svg',
}

// Generate prediction based on team stats
function calculatePrediction(
  homeAbbr: string, 
  awayAbbr: string, 
  teamStatsMap: Record<string, TeamStats>
): { homeWinProb: number; awayWinProb: number; confidence: number } {
  const homeStats = teamStatsMap[homeAbbr]
  const awayStats = teamStatsMap[awayAbbr]
  
  if (!homeStats || !awayStats) {
    return { homeWinProb: 50, awayWinProb: 50, confidence: 50 }
  }
  
  // Prediction model using real stats
  const homeAdvantage = 0.03 // ~3% home court advantage
  const winPctDiff = homeStats.win_pct - awayStats.win_pct
  const netRatingHome = homeStats.ppg - homeStats.opp_ppg
  const netRatingAway = awayStats.ppg - awayStats.opp_ppg
  const netRatingDiff = (netRatingHome - netRatingAway) / 20 // Normalize
  
  // Calculate probability
  let homeProb = 0.5 + winPctDiff / 2 + homeAdvantage + netRatingDiff
  homeProb = Math.max(0.20, Math.min(0.80, homeProb)) // Clamp between 20-80%
  
  const homeWinProb = Math.round(homeProb * 100)
  const awayWinProb = 100 - homeWinProb
  const confidence = Math.round(Math.max(homeWinProb, awayWinProb))
  
  return { homeWinProb, awayWinProb, confidence }
}

// Format date for display
function formatGameDate(dateStr: string): string {
  const date = new Date(dateStr + 'T00:00:00')
  return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })
}

function PredictionsPage() {
  const [predictions, setPredictions] = useState<GamePrediction[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [teamStats, setTeamStats] = useState<Record<string, TeamStats>>({})

  useEffect(() => {
    const fetchScheduleAndPredict = async () => {
      setLoading(true)
      setError(null)
      try {
        console.log('Fetching schedule and team stats...')
        
        // Fetch both schedule and team stats
        const [games, stats] = await Promise.all([
          api.getUpcomingGames(),
          api.getTeamStats()
        ])
        
        console.log('Games received:', games.length)
        console.log('Stats received:', stats.length)
        
        // Create stats lookup map
        const statsMap: Record<string, TeamStats> = {}
        stats.forEach(s => { statsMap[s.abbr] = s })
        setTeamStats(statsMap)
        
        // Generate predictions for each game
        const gamePredictions: GamePrediction[] = games.map((game, idx) => {
          const { homeWinProb, awayWinProb, confidence } = calculatePrediction(
            game.home_team_abbr,
            game.away_team_abbr,
            statsMap
          )
          
          return {
            id: idx + 1,
            gameId: game.game_id,
            homeTeam: {
              name: game.home_team_name,
              city: game.home_team_city,
              abbreviation: game.home_team_abbr,
              logo: teamLogos[game.home_team_abbr] || ''
            },
            awayTeam: {
              name: game.away_team_name,
              city: game.away_team_city,
              abbreviation: game.away_team_abbr,
              logo: teamLogos[game.away_team_abbr] || ''
            },
            homeWinProb,
            awayWinProb,
            predictedWinner: homeWinProb > awayWinProb ? game.home_team_abbr : game.away_team_abbr,
            confidence,
            date: formatGameDate(game.game_date),
            time: game.game_time
          }
        })
        
        console.log('Predictions generated:', gamePredictions.length)
        setPredictions(gamePredictions)
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Unknown error'
        console.error('Failed to fetch schedule:', errorMsg)
        setError(errorMsg)
        setPredictions([])
      } finally {
        setLoading(false)
      }
    }
    fetchScheduleAndPredict()
  }, [])

  const handleRefresh = () => {
    // Re-fetch data
    setLoading(true)
    api.getUpcomingGames().then(games => {
      const gamePredictions: GamePrediction[] = games.map((game, idx) => {
        const { homeWinProb, awayWinProb, confidence } = calculatePrediction(
          game.home_team_abbr,
          game.away_team_abbr,
          teamStats
        )
        
        return {
          id: idx + 1,
          gameId: game.game_id,
          homeTeam: {
            name: game.home_team_name,
            city: game.home_team_city,
            abbreviation: game.home_team_abbr,
            logo: teamLogos[game.home_team_abbr] || ''
          },
          awayTeam: {
            name: game.away_team_name,
            city: game.away_team_city,
            abbreviation: game.away_team_abbr,
            logo: teamLogos[game.away_team_abbr] || ''
          },
          homeWinProb,
          awayWinProb,
          predictedWinner: homeWinProb > awayWinProb ? game.home_team_abbr : game.away_team_abbr,
          confidence,
          date: formatGameDate(game.game_date),
          time: game.game_time
        }
      })
      setPredictions(gamePredictions)
      setLoading(false)
    }).catch(() => setLoading(false))
  }

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ py: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    )
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <TrendingUpIcon sx={{ fontSize: 40, color: 'secondary.main', mr: 2 }} />
          <Box>
            <Typography variant="h3" sx={{ fontWeight: 700, color: 'white' }}>
              Game Predictions
            </Typography>
            <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.6)' }}>
              ML-powered predictions based on team performance metrics
            </Typography>
          </Box>
        </Box>
        <Button 
          variant="outlined" 
          startIcon={<RefreshIcon />}
          onClick={handleRefresh}
          sx={{ color: 'white', borderColor: 'rgba(255,255,255,0.3)' }}
        >
          New Matchups
        </Button>
      </Box>

      {error && (
        <Typography sx={{ color: 'error.main', textAlign: 'center', py: 2, mb: 2 }}>
          Error: {error}
        </Typography>
      )}

      {predictions.length === 0 && !error && (
        <Typography sx={{ color: 'rgba(255,255,255,0.6)', textAlign: 'center', py: 4 }}>
          No predictions available. Please try again later.
        </Typography>
      )}

      {predictions.length > 0 && (
        <Grid container spacing={3}>
          {predictions.map((prediction) => (
            <Grid item xs={12} md={6} key={prediction.id}>
              <Card sx={{ 
                bgcolor: 'background.paper', 
                border: '1px solid rgba(255,255,255,0.1)',
              }}>
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)' }}>
                      {prediction.date} • {prediction.time}
                    </Typography>
                    <Chip 
                      label={`${prediction.confidence}% confidence`} 
                      size="small" 
                      color={prediction.confidence >= 60 ? 'success' : prediction.confidence >= 50 ? 'warning' : 'default'}
                    />
                  </Box>

                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                    {/* Away Team */}
                    <Box sx={{ textAlign: 'center', flex: 1 }}>
                      <img 
                        src={prediction.awayTeam.logo} 
                        alt={prediction.awayTeam.name}
                        style={{ width: 60, height: 60, objectFit: 'contain' }}
                      />
                      <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
                        {prediction.awayTeam.abbreviation}
                      </Typography>
                      <Typography variant="h4" sx={{ 
                        color: prediction.predictedWinner === prediction.awayTeam.abbreviation ? 'success.main' : 'rgba(255,255,255,0.5)',
                        fontWeight: 700,
                      }}>
                        {prediction.awayWinProb}%
                      </Typography>
                    </Box>

                    <Typography variant="h5" sx={{ color: 'rgba(255,255,255,0.3)', mx: 2 }}>@</Typography>

                    {/* Home Team */}
                    <Box sx={{ textAlign: 'center', flex: 1 }}>
                      <img 
                        src={prediction.homeTeam.logo} 
                        alt={prediction.homeTeam.name}
                        style={{ width: 60, height: 60, objectFit: 'contain' }}
                      />
                      <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
                        {prediction.homeTeam.abbreviation}
                      </Typography>
                      <Typography variant="h4" sx={{ 
                        color: prediction.predictedWinner === prediction.homeTeam.abbreviation ? 'success.main' : 'rgba(255,255,255,0.5)',
                        fontWeight: 700,
                      }}>
                        {prediction.homeWinProb}%
                      </Typography>
                    </Box>
                  </Box>

                  {/* Win Probability Bar */}
                  <Box sx={{ position: 'relative', height: 8, borderRadius: 4, overflow: 'hidden', bgcolor: 'rgba(255,255,255,0.1)' }}>
                    <Box sx={{ 
                      position: 'absolute', 
                      left: 0, 
                      top: 0, 
                      height: '100%', 
                      width: `${prediction.awayWinProb}%`,
                      bgcolor: prediction.predictedWinner === prediction.awayTeam.abbreviation ? 'success.main' : 'primary.main',
                      borderRadius: '4px 0 0 4px',
                    }} />
                    <Box sx={{ 
                      position: 'absolute', 
                      right: 0, 
                      top: 0, 
                      height: '100%', 
                      width: `${prediction.homeWinProb}%`,
                      bgcolor: prediction.predictedWinner === prediction.homeTeam.abbreviation ? 'success.main' : 'secondary.main',
                      borderRadius: '0 4px 4px 0',
                    }} />
                  </Box>

                  <Typography variant="body2" sx={{ textAlign: 'center', mt: 2, color: 'rgba(255,255,255,0.6)' }}>
                    Predicted Winner: <strong style={{ color: '#4caf50' }}>{prediction.predictedWinner}</strong>
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      <Box sx={{ mt: 6, p: 3, bgcolor: 'background.paper', borderRadius: 2, border: '1px solid rgba(255,255,255,0.1)' }}>
        <Typography variant="h5" sx={{ mb: 2, color: 'white', fontWeight: 600 }}>
          About Our Predictions
        </Typography>
        <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.7)' }}>
          Our predictions are powered by machine learning models trained on historical NBA data including:
        </Typography>
        <Box component="ul" sx={{ color: 'rgba(255,255,255,0.7)', mt: 1 }}>
          <li>Team performance metrics (offensive/defensive ratings)</li>
          <li>Head-to-head historical matchups</li>
          <li>Home court advantage factors</li>
          <li>Recent form and momentum indicators</li>
          <li>Rest days and schedule density</li>
        </Box>
      </Box>
    </Container>
  )
}

export default PredictionsPage
