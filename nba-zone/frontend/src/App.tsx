import { Routes, Route } from 'react-router-dom'
import { Box } from '@mui/material'
import Navbar from './components/Navbar'
import HomePage from './pages/HomePage'
import TeamsPage from './pages/TeamsPage'
import PlayersPage from './pages/PlayersPage'
import PredictionsPage from './pages/PredictionsPage'

function App() {
  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <Navbar />
      <Box component="main" sx={{ pt: 2 }}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/teams" element={<TeamsPage />} />
          <Route path="/players" element={<PlayersPage />} />
          <Route path="/predictions" element={<PredictionsPage />} />
        </Routes>
      </Box>
    </Box>
  )
}

export default App
