import React, { useEffect, useRef } from 'react';
import { Box, Paper, Typography } from '@mui/material';
import Message from './Message';

const ChatWindow = ({ messages, onFeedback, feedbackStates, isLoading }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <Box sx={{ 
      flex: 1, 
      overflowY: 'auto',
      p: '16px',
      pb: '70px',
      //minHeight: 'calc(100vh - 60px)',
      //maxHeight: 'calc(100vh - 60px)',
      height: "100vh",
      boxSizing: 'border-box',
      display: 'flex',
      flexDirection: 'column',
      '& > *:first-child': {
        marginTop: 0
      },
      '& > * + *': {
        marginTop: '16px'
      },
      '&::-webkit-scrollbar': {
        width: '6px'
      },
      '&::-webkit-scrollbar-thumb': {
        backgroundColor: 'rgba(0,0,0,0.2)',
        borderRadius: '3px'
      }
    }}>
      {messages.map((message, index) => (
        <Message
          key={index}
          message={message}
          isUser={message.isUser}
          onFeedback={(type) => onFeedback(index, message, type)}
          showFeedback={!message.isUser && !message.isRegenerated}
          feedbackState={feedbackStates[index]}
        />
      ))}
      <div ref={messagesEndRef} />
      {isLoading && (
        <Box sx={{ textAlign: 'left', mb: 2 }}>
          <Paper
            elevation={1}
            sx={{
              display: 'inline-block',
              p: 2,
              borderRadius: 2,
              backgroundColor: '#f5f5f5',
              maxWidth: '90%',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box className="typing-dots">
                <span>.</span>
                <span>.</span>
                <span>.</span>
              </Box>
            </Box>
          </Paper>
        </Box>
      )}
    </Box>
  );
};

export default ChatWindow;
