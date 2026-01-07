import { useState } from 'react'
import { Container, Typography, Grid, Card, CardContent, Avatar, Box, TextField, MenuItem, Chip } from '@mui/material'

const players = [
  { id: 1, firstName: 'LeBron', lastName: 'James', team: 'LAL', position: 'SF', ppg: 25.7, rpg: 7.3, apg: 8.3, image: 'https://cdn.nba.com/headshots/nba/latest/1040x760/2544.png' },
  { id: 2, firstName: 'Stephen', lastName: 'Curry', team: 'GSW', position: 'PG', ppg: 29.4, rpg: 6.1, apg: 6.3, image: 'https://cdn.nba.com/headshots/nba/latest/1040x760/201939.png' },
  { id: 3, firstName: 'Kevin', lastName: 'Durant', team: 'PHX', position: 'SF', ppg: 29.1, rpg: 6.7, apg: 5.0, image: 'https://cdn.nba.com/headshots/nba/latest/1040x760/201142.png' },
  { id: 4, firstName: 'Giannis', lastName: 'Antetokounmpo', team: 'MIL', position: 'PF', ppg: 31.1, rpg: 11.8, apg: 5.7, image: 'https://cdn.nba.com/headshots/nba/latest/1040x760/203507.png' },
  { id: 5, firstName: 'Luka', lastName: 'Doncic', team: 'DAL', position: 'PG', ppg: 32.4, rpg: 8.6, apg: 8.0, image: 'https://cdn.nba.com/headshots/nba/latest/1040x760/1629029.png' },
  { id: 6, firstName: 'Nikola', lastName: 'Jokic', team: 'DEN', position: 'C', ppg: 24.5, rpg: 11.8, apg: 9.8, image: 'https://cdn.nba.com/headshots/nba/latest/1040x760/203999.png' },
  { id: 7, firstName: 'Joel', lastName: 'Embiid', team: 'PHI', position: 'C', ppg: 33.1, rpg: 10.2, apg: 4.2, image: 'https://cdn.nba.com/headshots/nba/latest/1040x760/203954.png' },
  { id: 8, firstName: 'Jayson', lastName: 'Tatum', team: 'BOS', position: 'SF', ppg: 30.1, rpg: 8.8, apg: 4.6, image: 'https://cdn.nba.com/headshots/nba/latest/1040x760/1628369.png' },
  { id: 9, firstName: 'Anthony', lastName: 'Davis', team: 'LAL', position: 'PF', ppg: 24.7, rpg: 12.6, apg: 3.5, image: 'https://cdn.nba.com/headshots/nba/latest/1040x760/203076.png' },
  { id: 10, firstName: 'Jimmy', lastName: 'Butler', team: 'MIA', position: 'SF', ppg: 22.9, rpg: 5.9, apg: 5.3, image: 'https://cdn.nba.com/headshots/nba/latest/1040x760/202710.png' },
  { id: 11, firstName: 'Devin', lastName: 'Booker', team: 'PHX', position: 'SG', ppg: 27.1, rpg: 4.5, apg: 6.9, image: 'https://cdn.nba.com/headshots/nba/latest/1040x760/1626164.png' },
  { id: 12, firstName: 'Ja', lastName: 'Morant', team: 'MEM', position: 'PG', ppg: 26.2, rpg: 5.9, apg: 8.1, image: 'https://cdn.nba.com/headshots/nba/latest/1040x760/1629630.png' },
]

const positions = ['All', 'PG', 'SG', 'SF', 'PF', 'C']

function PlayersPage() {
  const [search, setSearch] = useState('')
  const [position, setPosition] = useState('All')

  const filteredPlayers = players.filter((player) => {
    const matchesSearch = `${player.firstName} ${player.lastName}`.toLowerCase().includes(search.toLowerCase())
    const matchesPosition = position === 'All' || player.position === position
    return matchesSearch && matchesPosition
  })

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Typography variant="h3" sx={{ mb: 4, fontWeight: 700, color: 'white' }}>
        NBA Players
      </Typography>

      <Box sx={{ display: 'flex', gap: 2, mb: 4 }}>
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

      <Grid container spacing={3}>
        {filteredPlayers.map((player) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={player.id}>
            <Card sx={{ 
              bgcolor: 'background.paper', 
              border: '1px solid rgba(255,255,255,0.1)',
              cursor: 'pointer',
            }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Avatar
                    src={player.image}
                    alt={`${player.firstName} ${player.lastName}`}
                    sx={{ width: 80, height: 80, mr: 2 }}
                  />
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, color: 'white', lineHeight: 1.2 }}>
                      {player.firstName}
                    </Typography>
                    <Typography variant="h6" sx={{ fontWeight: 600, color: 'white', lineHeight: 1.2 }}>
                      {player.lastName}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                      <Chip label={player.team} size="small" color="primary" />
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
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  )
}

export default PlayersPage
