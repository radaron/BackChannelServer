import { Box, IconButton, Typography } from '@mui/material';
import { Computer, Close } from '@mui/icons-material';
import { useEffect, useRef } from 'react';

interface TerminalProps {
  clientName: string;
  messages: string[];
  onClose: () => void;
}

const TerminalCard: React.FC<TerminalProps> = ({ clientName, messages, onClose }) => {
  const terminalContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (terminalContainerRef.current) {
      terminalContainerRef.current.scrollTo({
        top: terminalContainerRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  }, [messages]);

  return (
    <>
      {/* Terminal Header */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          p: 2,
          bgcolor: '#1e1e1e',
          borderBottom: '1px solid #333',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Computer sx={{ color: '#00ff00', fontSize: 20 }} />
          <Typography variant="subtitle2" sx={{ color: '#00ff00', fontFamily: 'monospace' }}>
            {clientName}
          </Typography>
        </Box>
        <IconButton
          size="small"
          onClick={onClose}
          sx={{
            color: '#ff5555',
            '&:hover': {
              bgcolor: 'rgba(255, 85, 85, 0.1)',
            },
          }}
        >
          <Close />
        </IconButton>
      </Box>

      {/* Terminal Content */}
      <Box
        ref={terminalContainerRef}
        sx={{
          flexGrow: 1,
          bgcolor: '#1e1e1e',
          p: 2,
          overflow: 'auto',
          fontFamily: 'monospace',
          fontSize: '0.6rem',
          color: '#00ff00',
          borderRadius: 0,
          boxShadow: 'none',
          '&::-webkit-scrollbar': {
            width: '8px',
          },
          '&::-webkit-scrollbar-track': {
            bgcolor: '#2b2b2b',
          },
          '&::-webkit-scrollbar-thumb': {
            bgcolor: '#555',
            borderRadius: '4px',
            '&:hover': {
              bgcolor: '#777',
            },
          },
        }}
      >
        {messages.map((message, index) => (
          <Box
            key={index}
            sx={{
              mb: 0.5,
              wordBreak: 'break-word',
              whiteSpace: 'pre-wrap',
            }}
          >
            {message}
          </Box>
        ))}
      </Box>
    </>
  );
};

export default TerminalCard;
