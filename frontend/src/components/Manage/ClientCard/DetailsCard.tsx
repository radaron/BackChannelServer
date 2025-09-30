import {
  Button,
  CardContent,
  Typography,
  Box,
  Chip,
  Divider,
  Badge,
} from '@mui/material';
import { Computer, Memory, Storage, Thermostat, AccessTime } from '@mui/icons-material';
import type { ClientData } from '../../../services/manageService';

interface DetailsCardProps {
  client: ClientData;
  isFlipped: boolean;
  onDelete: (name: string) => void;
  handleConnection: () => void;
  handleDisconnect: () => void;
  isConnected: boolean;
}

const DetailsCard: React.FC<DetailsCardProps> = ({ client, isFlipped, onDelete, handleConnection, handleDisconnect, isConnected }) => {

  const isClientActive = () => {
    const now = Date.now() / 1000;
    const timeSinceLastPoll = now - client.polledTime;
    return timeSinceLastPoll < 60;
  };

  const formatUptime = (seconds?: number) => {
    if (!seconds) return 'N/A';
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  };

  return (
      <>
        <CardContent sx={{ flexGrow: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Computer sx={{ fontSize: 32, color: 'primary.main', mr: 1 }} />
            <Typography variant="h6" component="div">
              {client.name}
              </Typography>
            </Box>

            <Divider sx={{ mb: 2 }} />

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <AccessTime sx={{ fontSize: 18, mr: 0.5, color: 'text.secondary' }} />
                  <Typography variant="body2" color="text.secondary">
                    Uptime:
                  </Typography>
                </Box>
                <Chip label={formatUptime(client.uptime)} size="small" color="info" />
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Memory sx={{ fontSize: 18, mr: 0.5, color: 'text.secondary' }} />
                  <Typography variant="body2" color="text.secondary">
                    CPU:
                  </Typography>
                </Box>
                <Chip
                  label={client.cpuUsage !== undefined ? `${client.cpuUsage}%` : 'N/A'}
                  size="small"
                  color={client.cpuUsage && client.cpuUsage > 80 ? 'error' : 'default'}
                />
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Memory sx={{ fontSize: 18, mr: 0.5, color: 'text.secondary' }} />
                  <Typography variant="body2" color="text.secondary">
                    Memory:
                  </Typography>
                </Box>
                <Chip
                  label={client.memoryUsage !== undefined ? `${client.memoryUsage}%` : 'N/A'}
                  size="small"
                  color={client.memoryUsage && client.memoryUsage > 80 ? 'error' : 'default'}
                />
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Storage sx={{ fontSize: 18, mr: 0.5, color: 'text.secondary' }} />
                  <Typography variant="body2" color="text.secondary">
                    Disk:
                  </Typography>
                </Box>
                <Chip
                  label={client.diskUsage !== undefined ? `${client.diskUsage}%` : 'N/A'}
                  size="small"
                  color={client.diskUsage && client.diskUsage > 80 ? 'warning' : 'default'}
                />
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Thermostat sx={{ fontSize: 18, mr: 0.5, color: 'text.secondary' }} />
                  <Typography variant="body2" color="text.secondary">
                    Temp:
                  </Typography>
                </Box>
                <Chip
                  label={client.temperature !== undefined ? `${client.temperature}°C` : 'N/A'}
                  size="small"
                  color={client.temperature && client.temperature > 70 ? 'error' : 'default'}
                />
              </Box>
            </Box>

            <Divider sx={{ my: 2 }} />

            <Box sx={{ display: isFlipped ? 'none' : 'flex', alignItems: 'center', gap: 1 }}>
              <Badge
                variant="dot"
                sx={{
                  '& .MuiBadge-badge': {
                    backgroundColor: isClientActive() ? '#44b700' : '#f44336',
                    boxShadow: isClientActive()
                      ? '0 0 0 2px rgba(68, 183, 0, 0.2)'
                      : '0 0 0 2px rgba(244, 67, 54, 0.2)',
                    width: 12,
                    height: 12,
                    borderRadius: '50%',
                  },
                }}
              >
                <Box sx={{ width: 8 }} />
              </Badge>
              <Typography
                variant="body2"
                sx={{
                  fontWeight: 600,
                  color: isClientActive() ? 'success.main' : 'error.main'
                }}
              >
                {isClientActive() ? 'Active' : 'Inactive'}
              </Typography>
            </Box>
          </CardContent>

          <Box sx={{ p: 2, pt: 0, display: 'flex', gap: 1, flexDirection: 'column' }}>
            <Button
              variant="contained"
              onClick={handleConnection}
              disabled={isConnected}
              fullWidth
              size="small"
            >
              {isConnected ? 'Connected' : 'Connect'}
            </Button>

            <Button
              variant="outlined"
              onClick={() => onDelete(client.name)}
              color="error"
              fullWidth
              size="small"
            >
              Delete
            </Button>
          </Box>
      </>
  );
};

export default DetailsCard;
