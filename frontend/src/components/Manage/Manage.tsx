import React from 'react';
import {
  Box,
  Typography,
  Container,
  Button,
} from '@mui/material';
import { Dashboard, ExitToApp } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import ManageItem from './ManageItem.tsx';

const Manage: React.FC = () => {
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      const response = await fetch('/api/v1/auth/logout', {
        method: 'POST',
        credentials: 'include',
      });

      if (response.ok) {
        navigate('/login');
      } else {
        console.error('Logout failed');
      }
    } catch (error) {
      console.error('Logout error:', error);
      // Navigate to login anyway on error
      navigate('/login');
    }
  };

  const handleGetData = async () => {
    try {
      const response = await fetch('/api/v1/manage/data', {
        method: 'GET',
        credentials: 'include',
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Manage Data:', data);
      } else {
        console.error('Failed to fetch manage data');
      }
    } catch (error) {
      console.error('Error fetching manage data:', error);
    }
  }

  const handleDeleteData = async () => {
    try {
      const response = await fetch('/api/v1/manage/data', {
        method: 'DELETE',
        credentials: 'include',
        body: JSON.stringify({ name: 'asd' }),
        headers: { 'Content-Type': 'application/json' },
      });

      if (response.ok) {
        console.log('Data deleted successfully');
      } else {
        console.error('Failed to delete data');
      }
    } catch (error) {
      console.error('Error deleting data:', error);
    }
  }

  return (
    <>
      {/* Full-width header */}
      <Box
        sx={{
          width: '100%',
          backgroundColor: 'red',
          py: 2,
          mb: 4,
        }}
      >
        <Container>
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexDirection: { xs: 'column', sm: 'row' },
              gap: { xs: 2, sm: 0 },
            }}
          >
            <Typography variant="h3" component="h1" gutterBottom>
              BackChannel
            </Typography>
            <Button
              variant="outlined"
              startIcon={<ExitToApp />}
              onClick={handleLogout}
              sx={{ height: 'fit-content' }}
            >
              Logout
            </Button>
          </Box>
        </Container>
      </Box>

      <Container>

        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: {
              xs: '1fr',
              sm: 'repeat(2, 1fr)',
              md: 'repeat(3, 1fr)',
            },
            gap: 3,
            mb: 4,
          }}
        >
          <ManageItem
            title="System Overview"
            description="Monitor system status and performance metrics"
            icon={<Dashboard sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />}
            onClick={() => handleGetData()}
          />
          <Button
            variant="outlined"
            color="error"
            onClick={() => handleDeleteData()}
          >
            Delete Data
          </Button>
        </Box>
      </Container>
    </>
  );
};

export default Manage;
