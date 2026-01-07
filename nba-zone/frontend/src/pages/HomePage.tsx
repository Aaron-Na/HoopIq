import { Box, Container, Typography, Grid, Card, CardContent, Button } from '@mui/material'
import { Link } from 'react-router-dom'
import GroupsIcon from '@mui/icons-material/Groups'
import PersonIcon from '@mui/icons-material/Person'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import SportsBasketballIcon from '@mui/icons-material/SportsBasketball'

const features = [
  {
    icon: <GroupsIcon sx={{ fontSize: 48 }} />,
    title: 'Team Analytics',
    description: 'Comprehensive team statistics, standings, and performance metrics across all 30 NBA teams.',
    link: '/teams',
    color: '#1d428a',
  },
  {
    icon: <PersonIcon sx={{ fontSize: 48 }} />,
    title: 'Player Stats',
    description: 'Detailed player statistics including points, rebounds, assists, and advanced metrics.',
    link: '/players',
    color: '#c8102e',
  },
  {
    icon: <TrendingUpIcon sx={{ fontSize: 48 }} />,
    title: 'Game Predictions',
    description: 'ML-powered predictions for upcoming games based on historical performance data.',
    link: '/predictions',
    color: '#00a651',
  },
]

function HomePage() {
  return (
    <Box>
      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #1d428a 0%, #0d2240 100%)',
          py: 10,
          textAlign: 'center',
        }}
      >
        <Container maxWidth="md">
          <SportsBasketballIcon sx={{ fontSize: 80, color: 'secondary.main', mb: 2 }} />
          <Typography variant="h2" sx={{ fontWeight: 700, mb: 2, color: 'white' }}>
            HoopIQ
          </Typography>
          <Typography variant="h5" sx={{ color: 'rgba(255,255,255,0.8)', mb: 4 }}>
            Your Ultimate NBA Analytics Platform
          </Typography>
          <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.7)', maxWidth: 600, mx: 'auto', mb: 4 }}>
            Dive deep into NBA statistics, explore team and player performance, 
            and get ML-powered game predictions all in one place.
          </Typography>
          <Button
            component={Link}
            to="/predictions"
            variant="contained"
            color="secondary"
            size="large"
            sx={{ px: 4, py: 1.5 }}
          >
            View Predictions
          </Button>
        </Container>
      </Box>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Typography variant="h3" sx={{ textAlign: 'center', mb: 6, color: 'white' }}>
          Explore Features
        </Typography>
        <Grid container spacing={4}>
          {features.map((feature) => (
            <Grid item xs={12} md={4} key={feature.title}>
              <Card
                sx={{
                  height: '100%',
                  bgcolor: 'background.paper',
                  border: '1px solid rgba(255,255,255,0.1)',
                }}
              >
                <CardContent sx={{ p: 4, textAlign: 'center' }}>
                  <Box sx={{ color: feature.color, mb: 2 }}>{feature.icon}</Box>
                  <Typography variant="h5" sx={{ mb: 2, fontWeight: 600, color: 'white' }}>
                    {feature.title}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', mb: 3 }}>
                    {feature.description}
                  </Typography>
                  <Button
                    component={Link}
                    to={feature.link}
                    variant="outlined"
                    sx={{ borderColor: feature.color, color: feature.color }}
                  >
                    Explore
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Stats Section */}
      <Box sx={{ bgcolor: 'background.paper', py: 6 }}>
        <Container maxWidth="lg">
          <Grid container spacing={4} justifyContent="center">
            {[
              { value: '30', label: 'NBA Teams' },
              { value: '450+', label: 'Active Players' },
              { value: '82', label: 'Games Per Season' },
              { value: '75+', label: 'Years of Data' },
            ].map((stat) => (
              <Grid item xs={6} md={3} key={stat.label}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h3" sx={{ fontWeight: 700, color: 'secondary.main' }}>
                    {stat.value}
                  </Typography>
                  <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                    {stat.label}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>
    </Box>
  )
}

export default HomePage
