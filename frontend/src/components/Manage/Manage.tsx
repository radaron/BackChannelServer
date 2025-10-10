import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Container,
  Button,
  Snackbar,
  Alert,
  CircularProgress,
  AppBar,
  Toolbar,
  Chip,
  Avatar,
} from '@mui/material';
import { ExitToApp, Dashboard } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import ClientCard from './ClientCard/ClientCard.tsx';
import { authService, manageService, ApiError } from '../../services';
import type { ClientData } from '../../services/manageService';
import logo from '../../../android-chrome-192x192.png';

const Manage: React.FC = () => {
  const navigate = useNavigate();
  const [clients, setClients] = useState<ClientData[]>([]);
  const [loading, setLoading] = useState(true);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({
    open: false,
    message: '',
    severity: 'info',
  });

  const showSnackbar = (message: string, severity: 'success' | 'error' | 'info' | 'warning' = 'info') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const handleLogout = async () => {
    try {
      await authService.logout();
      navigate('/login');
    } catch {
      showSnackbar('Logout error. Redirecting to login...', 'error');
      navigate('/login');
    }
  };

  const fetchClients = useCallback(async () => {
    try {
      const data = await manageService.getClients();
      setClients(data);
    } catch (error) {
      if (error instanceof ApiError) {
        if (error.status === 401) {
          navigate('/login');
          return;
        }
        showSnackbar(`Failed to fetch clients: ${error.message}`, 'error');
      } else {
        showSnackbar('Error fetching clients', 'error');
      }
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  const handleDeleteClient = async (name: string) => {
    try {
      await manageService.deleteData(name);
      showSnackbar(`Client '${name}' deleted successfully`, 'success');
      fetchClients();
    } catch (error) {
      if (error instanceof ApiError) {
        showSnackbar(`Failed to delete client: ${error.message}`, 'error');
      } else {
        showSnackbar('Error deleting client', 'error');
      }
    }
  };

  useEffect(() => {
    fetchClients();

    const intervalId = setInterval(() => {
      fetchClients();
    }, 5000);

    return () => {
      clearInterval(intervalId);
    };
  }, [fetchClients]);

  return (
    <>
      {/* Modern AppBar Header */}
      <AppBar
        position="static"
        elevation={0}
        sx={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        }}
      >
        <Toolbar sx={{ py: { xs: 0.5, sm: 1 }, minHeight: { xs: '56px', sm: '64px' } }}>
          <Avatar
            src={logo}
            alt="BackChannel Logo"
            sx={{
              bgcolor: 'rgba(255, 255, 255, 0.2)',
              mr: { xs: 1, sm: 2 },
              width: { xs: 36, sm: 48 },
              height: { xs: 36, sm: 48 },
            }}
          />

          <Box sx={{ flexGrow: 1 }}>
            <Typography
              variant="h4"
              component="h1"
              sx={{
                fontWeight: 700,
                color: 'white',
                letterSpacing: '-0.5px',
                fontSize: { xs: '1.25rem', sm: '1.75rem', md: '2.125rem' },
              }}
            >
              BackChannel
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', gap: { xs: 0.5, sm: 1 }, alignItems: 'center' }}>
            <Chip
              icon={<Dashboard sx={{ color: 'white !important' }} />}
              label={`${clients.length} Client${clients.length !== 1 ? 's' : ''}`}
              sx={{
                bgcolor: 'rgba(255, 255, 255, 0.2)',
                color: 'white',
                fontWeight: 600,
                display: { xs: 'none', sm: 'flex' },
                fontSize: { xs: '0.75rem', sm: '0.8125rem' },
              }}
            />

            <Button
              variant="contained"
              startIcon={<ExitToApp sx={{ display: { xs: 'none', sm: 'block' } }} />}
              onClick={handleLogout}
              size="small"
              sx={{
                bgcolor: 'rgba(255, 255, 255, 0.9)',
                color: 'primary.main',
                fontWeight: 600,
                fontSize: { xs: '0.75rem', sm: '0.875rem' },
                px: { xs: 1.5, sm: 2 },
                '&:hover': {
                  bgcolor: 'white',
                },
              }}
            >
              Logout
            </Button>
          </Box>
        </Toolbar>
      </AppBar>

      <Container sx={{ mt: { xs: 2, sm: 4 } }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
            <CircularProgress size={60} />
          </Box>
        ) : clients.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No clients found
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Clients will appear here once they connect to the system.
            </Typography>
          </Box>
        ) : (
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: {
                xs: '1fr',
                sm: 'repeat(2, 1fr)',
                md: 'repeat(3, 1fr)',
                lg: 'repeat(4, 1fr)',
              },
              gap: 3,
              mb: 4,
            }}
          >
            {clients.map((client) => (
              <ClientCard
                key={client.name}
                client={client}
                onDelete={handleDeleteClient}
                showSnackbar={showSnackbar}
              />
            ))}
          </Box>
        )}
      </Container>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </>
  );
};

export default Manage;
