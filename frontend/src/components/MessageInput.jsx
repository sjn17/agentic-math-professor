import React, { useState } from 'react';
import { Box, TextField, IconButton, Paper } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';

const MessageInput = ({ onSend, isLoading }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSend(input);
      setInput('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      handleSubmit(e);
    }
  };

  return (
    <Paper
      component="form"
      onSubmit={handleSubmit}
      sx={{
        p: '8px 16px',
        width: '100%',
        backgroundColor: 'background.paper',
        borderTop: '1px solid',
        borderColor: 'divider',
        borderRadius: 0,
        boxSizing: 'border-box',
        boxShadow: '0 -2px 10px rgba(0,0,0,0.05)'
      }}
      elevation={2}
    >
      <Box display="flex" gap={1} alignItems="center" width="100%" margin="0 auto">
        <TextField
          fullWidth
          variant="outlined"
          size="small"
          placeholder="Type your math question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={isLoading}
          multiline
          maxRows={2}
          sx={{
            '& .MuiOutlinedInput-root': {
              padding: '4px 8px',
              '& textarea': {
                padding: '4px 0',
                lineHeight: '1.2',
                maxHeight: '48px',
                overflowY: 'auto !important',
                fontSize: '0.9rem'
              },
              '& fieldset': {
                border: '1px solid #e0e0e0',
              },
              '&:hover fieldset': {
                borderColor: '#90caf9 !important',
              },
            },
          }}
        />
        <IconButton 
          type="submit" 
          color="primary" 
          disabled={!input.trim() || isLoading}
          size="small"
          sx={{ 
            alignSelf: 'flex-end',
            marginBottom: '4px',
            padding: '6px',
            '&:hover': {
              backgroundColor: 'rgba(25, 118, 210, 0.08)'
            }
          }}
        >
          <SendIcon fontSize="small" />
        </IconButton>
      </Box>
    </Paper>
  );
};

export default MessageInput;
