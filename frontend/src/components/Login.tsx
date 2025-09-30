import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  Container,
  CircularProgress,
} from '@mui/material';
import { Lock } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { authService, ApiError } from '../services';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!password.trim()) {
      setError('Password is required');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const data = await authService.login(password);
      setSuccess(data.message);
      setPassword(''); // Clear the password field on success

      // Redirect to manage page on successful login
      console.log('Login successful:', data);

      // Add a small delay to show the success message before navigating
      setTimeout(() => {
        navigate('/manage');
      }, 1000);

    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 401) {
          setError('Incorrect password');
        } else {
          setError(err.message);
        }
      } else {
        setError(err instanceof Error ? err.message : 'An error occurred');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          marginTop: { xs: 4, sm: 8 },
          marginX: { xs: 2, sm: 0 },
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          minHeight: '100vh',
          justifyContent: { xs: 'flex-start', sm: 'center' },
          paddingTop: { xs: 2, sm: 0 },
        }}
      >
        <Card sx={{
          width: '100%',
          maxWidth: { xs: '100%', sm: 400 },
          boxShadow: { xs: 0, sm: 3 },
        }}>
          <CardContent sx={{
            p: { xs: 3, sm: 4 },
            '&:last-child': { pb: { xs: 3, sm: 4 } }
          }}>
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                mb: { xs: 2, sm: 3 },
              }}
            >
              <Lock sx={{
                fontSize: { xs: 35, sm: 40 },
                color: 'primary.main',
                mb: { xs: 1.5, sm: 2 }
              }} />
              <Typography
                component="h1"
                variant="h4"
                gutterBottom
                sx={{
                  fontSize: { xs: '1.75rem', sm: '2.125rem' }
                }}
              >
                Login
              </Typography>
            </Box>

            <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
              <TextField
                margin="normal"
                required
                fullWidth
                name="password"
                label="Password"
                type="password"
                id="password"
                autoComplete="current-password"
                autoFocus
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
                variant="outlined"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    fontSize: { xs: '16px', sm: '14px' },
                  },
                }}
              />

              {error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {error}
                </Alert>
              )}

              {success && (
                <Alert severity="success" sx={{ mt: 2 }}>
                  {success}
                </Alert>
              )}

              <Button
                type="submit"
                fullWidth
                variant="contained"
                disabled={loading || !password.trim()}
                sx={{
                  mt: { xs: 2.5, sm: 3 },
                  mb: 2,
                  height: { xs: 52, sm: 48 },
                  fontSize: { xs: '16px', sm: '14px' },
                  fontWeight: 'medium',
                }}
                startIcon={loading ? <CircularProgress size={20} /> : null}
              >
                {loading ? 'Logging in...' : 'Login'}
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
};

export default Login;