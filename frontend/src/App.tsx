import Login from './components/Login.tsx'
import Manage from './components/Manage/Manage.tsx'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'

// Create a custom theme with mobile-first responsive design
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  breakpoints: {
    values: {
      xs: 0,
      sm: 600,
      md: 900,
      lg: 1200,
      xl: 1536,
    },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          // Prevent zoom on input focus on iOS
          '@supports (-webkit-touch-callout: none)': {
            fontSize: '16px',
          },
        },
      },
    },
    MuiTextField: {
      defaultProps: {
        // Prevent zoom on mobile devices
        inputProps: {
          style: { fontSize: '16px' },
        },
      },
    },
  },
})

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/manage" element={<Manage />} />
            <Route path="/" element={<Navigate to="/login" replace />} />
          </Routes>
        </Router>
    </ThemeProvider>
  )
}

export default App
