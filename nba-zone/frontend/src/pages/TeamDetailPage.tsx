import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Container, Typography, Grid, Card, CardContent, Avatar, Box, Chip, CircularProgress, Button, Paper } from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import api, { PlayerStats } from '../api'

// Team info mapping
const teamInfo: Record<string, { name: string; city: string; logo: string; conference: string; color: string }> = {
  BOS: { name: 'Celtics', city: 'Boston', logo: 'https://cdn.nba.com/logos/nba/1610612738/primary/L/logo.svg', conference: 'East', color: '#007A33' },
  OKC: { name: 'Thunder', city: 'Oklahoma City', logo: 'https://cdn.nba.com/logos/nba/1610612760/primary/L/logo.svg', conference: 'West', color: '#007AC1' },
  CLE: { name: 'Cavaliers', city: 'Cleveland', logo: 'https://cdn.nba.com/logos/nba/1610612739/primary/L/logo.svg', conference: 'East', color: '#860038' },
  NYK: { name: 'Knicks', city: 'New York', logo: 'https://cdn.nba.com/logos/nba/1610612752/primary/L/logo.svg', conference: 'East', color: '#006BB6' },
  MIL: { name: 'Bucks', city: 'Milwaukee', logo: 'https://cdn.nba.com/logos/nba/1610612749/primary/L/logo.svg', conference: 'East', color: '#00471B' },
  MIA: { name: 'Heat', city: 'Miami', logo: 'https://cdn.nba.com/logos/nba/1610612748/primary/L/logo.svg', conference: 'East', color: '#98002E' },
  DEN: { name: 'Nuggets', city: 'Denver', logo: 'https://cdn.nba.com/logos/nba/1610612743/primary/L/logo.svg', conference: 'West', color: '#0E2240' },
  DAL: { name: 'Mavericks', city: 'Dallas', logo: 'https://cdn.nba.com/logos/nba/1610612742/primary/L/logo.svg', conference: 'West', color: '#00538C' },
  MIN: { name: 'Timberwolves', city: 'Minnesota', logo: 'https://cdn.nba.com/logos/nba/1610612750/primary/L/logo.svg', conference: 'West', color: '#0C2340' },
  PHX: { name: 'Suns', city: 'Phoenix', logo: 'https://cdn.nba.com/logos/nba/1610612756/primary/L/logo.svg', conference: 'West', color: '#1D1160' },
}

function TeamDetailPage() {
  const { teamAbbr } = useParams<{ teamAbbr: string }>()
  const navigate = useNavigate()
  const [players, setPlayers] = useState<PlayerStats[]>([])
  const [loading, setLoading] = useState(true)

  const team = teamAbbr ? teamInfo[teamAbbr.toUpperCase()] : null

  useEffect(() => {
    const fetchPlayers = async () => {
      if (!teamAbbr) return
      setLoading(true)
      try {
        const data = await api.getPlayersByTeam(teamAbbr.toUpperCase())
        // Sort by PPG descending
        data.sort((a, b) => b.ppg - a.ppg)
        setPlayers(data)
      } catch (error) {
        console.error('Failed to fetch team players:', error)
        setPlayers([])
      } finally {
        setLoading(false)
      }
    }
    fetchPlayers()
  }, [teamAbbr])

  if (!team) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Typography variant="h4" sx={{ color: 'white' }}>Team not found</Typography>
        <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/teams')} sx={{ mt: 2 }}>
          Back to Teams
        </Button>
      </Container>
    )
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Button 
        startIcon={<ArrowBackIcon />} 
        onClick={() => navigate('/teams')}
        sx={{ mb: 3, color: 'rgba(255,255,255,0.7)' }}
      >
        Back to Teams
      </Button>

      {/* Team Header */}
      <Paper 
        sx={{ 
          p: 4, 
          mb: 4, 
          bgcolor: 'background.paper',
          border: '1px solid rgba(255,255,255,0.1)',
          borderLeft: `4px solid ${team.color}`,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
          <Box
            component="img"
            src={team.logo}
            alt={team.name}
            sx={{ width: 120, height: 120, objectFit: 'contain' }}
          />
          <Box>
            <Typography variant="h3" sx={{ fontWeight: 700, color: 'white' }}>
              {team.city} {team.name}
            </Typography>
            <Typography variant="h6" sx={{ color: 'rgba(255,255,255,0.6)' }}>
              {team.conference}ern Conference
            </Typography>
            <Chip 
              label={`${players.length} Players`} 
              sx={{ mt: 1, bgcolor: team.color, color: 'white' }} 
            />
          </Box>
        </Box>
      </Paper>

      {/* Roster */}
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 600, color: 'white' }}>
        Roster
      </Typography>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      ) : players.length === 0 ? (
        <Typography sx={{ color: 'rgba(255,255,255,0.6)' }}>No players found for this team.</Typography>
      ) : (
        <Grid container spacing={3}>
          {players.map((player) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={player.player_id}>
              <Card sx={{ 
                bgcolor: 'background.paper', 
                border: '1px solid rgba(255,255,255,0.1)',
                '&:hover': { borderColor: team.color }
              }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Avatar
                      src={`https://cdn.nba.com/headshots/nba/latest/1040x760/${player.player_id}.png`}
                      alt={player.name}
                      sx={{ width: 70, height: 70, mr: 2, bgcolor: 'grey.800' }}
                    >
                      {player.name.split(' ').map(n => n[0]).join('')}
                    </Avatar>
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 600, color: 'white', lineHeight: 1.2, fontSize: '1rem' }}>
                        {player.name}
                      </Typography>
                      <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)' }}>
                        #{player.jersey} | {player.position}
                      </Typography>
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                        {player.height} | {player.weight} lbs
                      </Typography>
                    </Box>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-around', pt: 2, borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h6" sx={{ color: 'secondary.main', fontWeight: 700 }}>{player.ppg}</Typography>
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)' }}>PPG</Typography>
                    </Box>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h6" sx={{ color: 'secondary.main', fontWeight: 700 }}>{player.rpg}</Typography>
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)' }}>RPG</Typography>
                    </Box>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h6" sx={{ color: 'secondary.main', fontWeight: 700 }}>{player.apg}</Typography>
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)' }}>APG</Typography>
                    </Box>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-around', pt: 1 }}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="body2" sx={{ color: 'success.main', fontWeight: 600 }}>{player.spg}</Typography>
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>SPG</Typography>
                    </Box>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="body2" sx={{ color: 'success.main', fontWeight: 600 }}>{player.bpg}</Typography>
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>BPG</Typography>
                    </Box>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="body2" sx={{ color: 'info.main', fontWeight: 600 }}>{player.fg_pct}%</Typography>
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>FG%</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  )
}

export default TeamDetailPage
