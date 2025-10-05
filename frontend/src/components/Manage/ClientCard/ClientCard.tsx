import { Card, Box } from '@mui/material';
import { useState } from 'react';
import type { ClientData } from '../../../services/manageService';
import { manageService } from '../../../services/manageService';
import { ApiError } from '../../../services/api';
import Terminal from './TerminalCard';
import DetailsCard from './DetailsCard';

const ClientCard: React.FC<{
  client: ClientData;
  onDelete: (name: string) => void;
  showSnackbar: (message: string, severity?: 'success' | 'error' | 'info' | 'warning') => void;
}> = ({ client, onDelete, showSnackbar }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [showTerminal, setShowTerminal] = useState(false);
  const [terminalMessages, setTerminalMessages] = useState<string[]>([]);

  const handleConnection = async () => {
    try {
      const data = await manageService.connect(client.name);
      if (data.forwarderId) {
        setTaskId(data.forwarderId);
        setTerminalMessages(prev => [...prev, `Connecting to ${client.name}...`]);
        setShowTerminal(true);
        startSSEConnection(data.forwarderId);
      }
    } catch {
      showSnackbar('Connection error occurred', 'error');
    }
  };

  const handleStopJob = async () => {
    if (!taskId) return;

    try {
      await manageService.deleteForwarder(taskId);
      setIsConnected(false);
      setTaskId(null);
    } catch (error) {
      console.log(error);
      if (error instanceof ApiError && error.status === 404) {
        showSnackbar('Forwarder not found or already stopped', 'info');
      } else {
        showSnackbar('Error stopping forwarder', 'error');
      }
    }
  };

  const startSSEConnection = (taskId: string) => {
    if (isConnected) {
      showSnackbar('connection already active', 'info');
      return;
    }

    const eventSource = new EventSource(`/api/v1/manage/forwarder/${taskId}`, {
      withCredentials: true
    });

    eventSource.onopen = () => {
      setTerminalMessages(prev => [...prev, 'connection opened']);
      setIsConnected(true);
    };

    eventSource.onmessage = (event) => {
      if (event.data === '[STREAM_END]') {
        setTerminalMessages(prev => [...prev, 'Stream ended by server']);
        eventSource.close();
        setIsConnected(false);
      } else {
        setTerminalMessages(prev => [...prev, `${event.data}`]);
      }
    };

    eventSource.onerror = () => {
      setTerminalMessages(prev => [...prev, 'connection error']);
      setIsConnected(false);

      setTimeout(() => {
        if (taskId) {
          setTerminalMessages(prev => [...prev, 'Attempting to reconnect...']);
          startSSEConnection(taskId);
        }
      }, 5000);
    };

    // Cleanup function to close connection
    const cleanup = () => {
      eventSource.close();
      setIsConnected(false);
      setTerminalMessages(prev => [...prev, 'connection closed']);
    };

    // Store cleanup function for later use
    (window as Window & { closeSSE?: () => void }).closeSSE = cleanup;

    // Auto-cleanup on page unload
    window.addEventListener('beforeunload', cleanup);
  };

  const handleDisconnect = () => {
    const win = window as Window & { closeSSE?: () => void };
    if (win.closeSSE) {
      win.closeSSE();
      handleStopJob();
      setShowTerminal(false);
      setTerminalMessages([]);
    }
  };

  return (
    <Box
      sx={{
        perspective: '1000px',
        height: '100%',
        minHeight: '400px',
      }}
    >
      <Card
        sx={{
          display: 'flex',
          flexDirection: 'column',
          height: '100%',
          minHeight: '400px',
          transition: 'transform 0.6s',
          transformStyle: 'preserve-3d',
          transform: showTerminal ? 'rotateY(180deg)' : 'rotateY(0deg)',
          position: 'relative',
          '&:hover': {
            boxShadow: 4,
          },
          background: '#c0b0ffff',
        }}
      >
        {/* Front Side - Info Card */}
        <Box
          sx={{
            backfaceVisibility: showTerminal ? 'hidden' : 'visible',
            position: 'absolute',
            width: '100%',
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <DetailsCard
            client={client}
            isFlipped={showTerminal}
            onDelete={onDelete}
            handleConnection={handleConnection}
            isConnected={isConnected}
          />
        </Box>

        {/* Back Side - Terminal View */}
        <Box
          sx={{
            backfaceVisibility: showTerminal ? 'visible' : 'hidden',
            transform: 'rotateY(180deg)',
            position: 'absolute',
            width: '100%',
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            top: 0,
            left: 0,
            bgcolor: '#1e1e1e',
            borderRadius: '4px',
            overflow: 'hidden',
          }}
        >
          <Terminal
            clientName={client.name}
            messages={terminalMessages}
            onClose={handleDisconnect}
          />
        </Box>
      </Card>
    </Box>
  );
}

export default ClientCard;