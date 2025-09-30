import {
  Button,
  Card,
  CardContent,
  Typography,
} from '@mui/material';
import { useState } from 'react';

const ManageItem: React.FC<{
  title: string;
  description: string;
  icon: React.ReactElement;
  onClick: () => void;
}> = ({ title, description, icon, onClick }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [taskId, setTaskId] = useState<string | null>(null);

  const handleConnection = async () => {
    try {
      const res = await fetch('/api/v1/manage/connect', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: 'test_client' }),
      });

      if (res.ok) {
        const data = await res.json();
        console.log('Connection Data:', data);

        // Assuming the response contains a jobId
        if (data.jobId) {
          setTaskId(data.jobId);
          startSSEConnection(data.jobId);
        }
      } else {
        console.error('Failed to establish connection');
      }
    } catch (error) {
      console.error('Connection error:', error);
    }
  };

  const handleStopJob = async () => {
    if (!taskId) return;

    try {
      const res = await fetch(`/api/v1/manage/forwarder/${taskId}`, {
        method: 'DELETE',
        credentials: 'include',
      });

      if (res.ok) {
        console.log('Job stopped successfully');
        setIsConnected(false);
        setTaskId(null);
      } else {
        console.error('Failed to stop job');
      }
    } catch (error) {
      console.error('Error stopping job:', error);
    }
  };

  const startSSEConnection = (taskId: string) => {
    if (isConnected) {
      console.log('SSE connection already active');
      return;
    }

    console.log(`Starting SSE connection for task: ${taskId}`);

    const eventSource = new EventSource(`/api/v1/manage/forwarder/${taskId}`, {
      withCredentials: true
    });

    eventSource.onopen = () => {
      console.log('SSE connection opened');
      setIsConnected(true);
    };

    eventSource.onmessage = (event) => {
      if (event.data === '[STREAM_END]') {
        console.log('Stream ended by server');
        eventSource.close();
        setIsConnected(false);
      } else {
        console.log('SSE Message:', event.data);
      }
    };

    eventSource.onerror = (error) => {
      console.error('SSE connection error:', error);
      setIsConnected(false);

      setTimeout(() => {
        if (taskId) {
          console.log('Attempting to reconnect SSE...');
          startSSEConnection(taskId);
        }
      }, 5000);
    };

    // Cleanup function to close connection
    const cleanup = () => {
      eventSource.close();
      setIsConnected(false);
      console.log('SSE connection closed');
    };

    // Store cleanup function for later use
    (window as any).closeSSE = cleanup;

    // Auto-cleanup on page unload
    window.addEventListener('beforeunload', cleanup);
  };

  const handleDisconnect = () => {
    if ((window as any).closeSSE) {
      (window as any).closeSSE();
      handleStopJob();
    }
  };

  return (
    <Card
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        p: 2,
        cursor: 'pointer',
        transition: 'transform 0.2s',
        '&:hover': {
          transform: 'scale(1.05)',
        },
      }}
      onClick={onClick}
    >
      {icon}
      <CardContent>
        <Typography variant="h6" component="div" gutterBottom>
          {title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          <Button
            variant="outlined"
            onClick={handleConnection}
            disabled={isConnected}
          >
            {isConnected ? 'Connected' : description}
          </Button>
          {isConnected && (
            <Button
              variant="outlined"
              onClick={handleDisconnect}
              sx={{ ml: 1 }}
              color="error"
            >
              Disconnect
            </Button>
          )}
        </Typography>
        {taskId && (
          <Typography variant="caption" display="block" sx={{ mt: 1 }}>
            Task ID: {taskId}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}

export default ManageItem;