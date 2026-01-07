import { Link, useLocation } from 'react-router-dom'
import { AppBar, Toolbar, Typography, Button, Box, Container } from '@mui/material'
import SportsBasketballIcon from '@mui/icons-material/SportsBasketball'

const navItems = [
  { label: 'Home', path: '/' },
  { label: 'Teams', path: '/teams' },
  { label: 'Players', path: '/players' },
  { label: 'Predictions', path: '/predictions' },
]

function Navbar() {
  const location = useLocation()

  return (
    <AppBar position="sticky" sx={{ bgcolor: 'background.paper', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
      <Container maxWidth="xl">
        <Toolbar disableGutters>
          <SportsBasketballIcon sx={{ mr: 1, color: 'secondary.main', fontSize: 32 }} />
          <Typography
            variant="h5"
            component={Link}
            to="/"
            sx={{
              fontWeight: 700,
              color: 'white',
              textDecoration: 'none',
              mr: 4,
            }}
          >
            HoopIQ
          </Typography>

          <Box sx={{ flexGrow: 1, display: 'flex', gap: 1 }}>
            {navItems.map((item) => (
              <Button
                key={item.path}
                component={Link}
                to={item.path}
                sx={{
                  color: location.pathname === item.path ? 'secondary.main' : 'white',
                  fontWeight: location.pathname === item.path ? 600 : 400,
                  '&:hover': { color: 'secondary.light' },
                }}
              >
                {item.label}
              </Button>
            ))}
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  )
}

export default Navbar
