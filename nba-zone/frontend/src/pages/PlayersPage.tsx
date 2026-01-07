import { useState, useEffect } from 'react'
import { Container, Typography, Grid, Card, CardContent, Avatar, Box, TextField, MenuItem, Chip, CircularProgress } from '@mui/material'
import api, { PlayerStats } from '../api'

const positions = ['All', 'G', 'F', 'C', 'G-F', 'F-C', 'F-G', 'C-F']
const teams = ['All', 'BOS', 'OKC', 'CLE', 'NYK', 'MIL', 'MIA', 'DEN', 'DAL', 'MIN', 'PHX']

function PlayersPage() {
  const [players, setPlayers] = useState<PlayerStats[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [position, setPosition] = useState('All')
  const [team, setTeam] = useState('All')

  useEffect(() => {
    const fetchPlayers = async () => {
      setLoading(true)
      try {
        const data = await api.getPlayerStats()
        // Sort by PPG descending
        data.sort((a, b) => b.ppg - a.ppg)
        setPlayers(data)
      } catch (error) {
        console.error('Failed to fetch players:', error)
        setPlayers([])
      } finally {
        setLoading(false)
      }
    }
    fetchPlayers()
  }, [])

  const filteredPlayers = players.filter((player) => {
    const matchesSearch = player.name.toLowerCase().includes(search.toLowerCase())
    const matchesPosition = position === 'All' || player.position.includes(position)
    const matchesTeam = team === 'All' || player.team_abbr === team
    return matchesSearch && matchesPosition && matchesTeam
  })

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Typography variant="h3" sx={{ mb: 4, fontWeight: 700, color: 'white' }}>
        NBA Players
      </Typography>

      <Box sx={{ display: 'flex', gap: 2, mb: 4, flexWrap: 'wrap' }}>
        <TextField
          label="Search players"
          variant="outlined"
          size="small"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          sx={{ width: 250 }}
        />
        <TextField
          select
          label="Team"
          value={team}
          onChange={(e) => setTeam(e.target.value)}
          size="small"
          sx={{ width: 150 }}
        >
          {teams.map((t) => (
            <MenuItem key={t} value={t}>{t === 'All' ? 'All Teams' : t}</MenuItem>
          ))}
        </TextField>
        <TextField
          select
          label="Position"
          value={position}
          onChange={(e) => setPosition(e.target.value)}
          size="small"
          sx={{ width: 150 }}
        >
          {positions.map((pos) => (
            <MenuItem key={pos} value={pos}>{pos === 'All' ? 'All Positions' : pos}</MenuItem>
          ))}
        </TextField>
      </Box>

      <Typography variant="body2" sx={{ mb: 2, color: 'rgba(255,255,255,0.6)' }}>
        Showing {filteredPlayers.length} of {players.length} players
      </Typography>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Grid container spacing={3}>
          {filteredPlayers.map((player) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={player.player_id}>
              <Card sx={{ 
                bgcolor: 'background.paper', 
                border: '1px solid rgba(255,255,255,0.1)',
                cursor: 'pointer',
                '&:hover': { borderColor: 'primary.main' }
              }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Avatar
                      src={`https://cdn.nba.com/headshots/nba/latest/1040x760/${player.player_id}.png`}
                      alt={player.name}
                      sx={{ width: 80, height: 80, mr: 2, bgcolor: 'grey.800' }}
                    >
                      {player.name.split(' ').map(n => n[0]).join('')}
                    </Avatar>
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 600, color: 'white', lineHeight: 1.2 }}>
                        {player.name}
                      </Typography>
                      <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)' }}>
                        #{player.jersey} | {player.height} | {player.weight} lbs
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                        <Chip label={player.team_abbr} size="small" color="primary" />
                        <Chip label={player.position} size="small" variant="outlined" />
                      </Box>
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

export default PlayersPage
