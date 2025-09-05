import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './latex-styles.css';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, Container, Typography, AppBar, Toolbar, Paper } from '@mui/material';
import ChatWindow from './components/ChatWindow';
import MessageInput from './components/MessageInput';

// Create a theme instance
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 500,
    },
  },
});

// Create axios instance with base URL
const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: false
});

function App() {
  const [messages, setMessages] = useState([
    { text: 'Hello! I am your Math Professor. How can I help you with math today?', isUser: false }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [feedbackStates, setFeedbackStates] = useState({});

  useEffect(() => {
    if (!sessionId) {
      setSessionId('session-' + Math.random().toString(36).substr(2, 9));
    }
  }, [sessionId]);

  const handleSend = async (input) => {
    if (!input.trim()) return;

    const userMessage = { text: input, isUser: true };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await api.post('ask', { 
        question: input,
        session_id: sessionId
      });

      setMessages(prev => [
        ...prev, 
        { 
          text: response.data.answer, 
          isUser: false 
        }
      ]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        text: `Error: ${error.message || 'Could not get a response from the server. Please try again later.'}`,
        isUser: false 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFeedback = async (messageIndex, message, feedbackType) => {
    if (!sessionId) return;
    
    try {
      setFeedbackStates(prev => ({ ...prev, [messageIndex]: feedbackType }));
      
      const response = await api.post('feedback', {
        session_id: sessionId,
        question: messages[messageIndex - 1]?.text || '',
        answer: message.text,
        feedback: feedbackType
      });

      const data = response.data;
      
      if (data.regenerated_answer) {
        setMessages(prev => [
          ...prev.slice(0, messageIndex + 1),
          { 
            text: data.regenerated_answer, 
            isUser: false,
            isRegenerated: true 
          },
          ...prev.slice(messageIndex + 1)
        ]);
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: 'background.default',
        }}
      >
        {/* <AppBar position="static" color="default" elevation={1}>
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Math Professor Assistant
            </Typography>
          </Toolbar>
        </AppBar> */}
        
        <Container maxWidth="md" sx={{ py: 4, flex: 1, display: 'flex', flexDirection: 'column' }}>
          <Paper 
            elevation={3} 
            sx={{
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
              position: 'relative',
              minHeight: '70vh',
            }}
          >
            <ChatWindow 
              messages={messages}
              onFeedback={handleFeedback}
              feedbackStates={feedbackStates}
              isLoading={isLoading}
            />
            <MessageInput 
              onSend={handleSend}
              isLoading={isLoading}
            />
          </Paper>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;