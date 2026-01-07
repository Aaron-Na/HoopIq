import { useState, useEffect } from 'react'
import { Container, Typography, Grid, Card, CardContent, CardMedia, Box, TextField, MenuItem, CircularProgress } from '@mui/material'
import { api, Team } from '../api'

// Fallback data if API is unavailable
const fallbackTeams: Team[] = [
  { id: 1, name: 'Lakers', city: 'Los Angeles', abbreviation: 'LAL', conference: 'West', division: 'Pacific', logo: 'https://cdn.nba.com/logos/nba/1610612747/primary/L/logo.svg', founded: 1947, championships: 17 },
  { id: 2, name: 'Celtics', city: 'Boston', abbreviation: 'BOS', conference: 'East', division: 'Atlantic', logo: 'https://cdn.nba.com/logos/nba/1610612738/primary/L/logo.svg', founded: 1946, championships: 18 },
  { id: 3, name: 'Warriors', city: 'Golden State', abbreviation: 'GSW', conference: 'West', division: 'Pacific', logo: 'https://cdn.nba.com/logos/nba/1610612744/primary/L/logo.svg', founded: 1946, championships: 7 },
  { id: 4, name: 'Bulls', city: 'Chicago', abbreviation: 'CHI', conference: 'East', division: 'Central', logo: 'https://cdn.nba.com/logos/nba/1610612741/primary/L/logo.svg', founded: 1966, championships: 6 },
  { id: 5, name: 'Heat', city: 'Miami', abbreviation: 'MIA', conference: 'East', division: 'Southeast', logo: 'https://cdn.nba.com/logos/nba/1610612748/primary/L/logo.svg', founded: 1988, championships: 3 },
  { id: 6, name: 'Nuggets', city: 'Denver', abbreviation: 'DEN', conference: 'West', division: 'Northwest', logo: 'https://cdn.nba.com/logos/nba/1610612743/primary/L/logo.svg', founded: 1967, championships: 1 },
]

function TeamsPage() {
  const [teams, setTeams] = useState<Team[]>(fallbackTeams)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [conference, setConference] = useState('All')

  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const data = await api.getTeams()
        setTeams(data)
      } catch (error) {
        console.error('Failed to fetch teams, using fallback data:', error)
        setTeams(fallbackTeams)
      } finally {
        setLoading(false)
      }
    }
    fetchTeams()
  }, [])

  const filteredTeams = teams.filter((team) => {
    const matchesSearch = team.name.toLowerCase().includes(search.toLowerCase()) ||
                          team.city.toLowerCase().includes(search.toLowerCase()) ||
                          team.abbreviation.toLowerCase().includes(search.toLowerCase())
    const matchesConference = conference === 'All' || team.conference === conference
    return matchesSearch && matchesConference
  })

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Typography variant="h3" sx={{ mb: 4, fontWeight: 700, color: 'white' }}>
        NBA Teams
      </Typography>

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      )}

      <Box sx={{ display: 'flex', gap: 2, mb: 4 }}>
        <TextField
          label="Search teams"
          variant="outlined"
          size="small"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          sx={{ width: 250 }}
        />
        <TextField
          select
          label="Conference"
          value={conference}
          onChange={(e) => setConference(e.target.value)}
          size="small"
          sx={{ width: 150 }}
        >
          <MenuItem value="All">All</MenuItem>
          <MenuItem value="East">Eastern</MenuItem>
          <MenuItem value="West">Western</MenuItem>
        </TextField>
      </Box>

      <Grid container spacing={3}>
        {filteredTeams.map((team) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={team.id}>
            <Card sx={{ 
              bgcolor: 'background.paper', 
              border: '1px solid rgba(255,255,255,0.1)',
              cursor: 'pointer',
            }}>
              <CardMedia
                component="img"
                image={team.logo}
                alt={team.name}
                sx={{ 
                  height: 140, 
                  objectFit: 'contain', 
                  p: 3,
                  bgcolor: 'rgba(255,255,255,0.05)',
                }}
              />
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 600, color: 'white' }}>
                  {team.city} {team.name}
                </Typography>
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)' }}>
                  {team.conference}ern Conference • {team.division}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  )
}

export default TeamsPage
