import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './latex-styles.css';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Paper from '@mui/material/Paper';
import SendIcon from '@mui/icons-material/Send';
import LatexRenderer from './components/LatexRenderer';

// Create a theme instance
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
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
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check backend connection on component mount
  useEffect(() => {
    const checkApi = async () => {
      try {
        // Check the root endpoint
        const response = await fetch('http://localhost:8000/');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        if (data?.status !== 'ok') {
          throw new Error('Backend health check failed');
        }
        
        console.log('Backend connection successful');
      } catch (error) {
        console.error('Backend connection error:', error);
        setMessages(prev => [...prev, {
          text: `Warning: Could not connect to the backend server. Please ensure it is running on http://localhost:8000\n\nError details: ${error.message}`,
          isUser: false
        }]);
      }
    };
    checkApi();
  }, []);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { text: input, isUser: true };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: input })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      if (data && data.answer) {
        setMessages(prev => [...prev, { text: data.answer, isUser: false }]);
      } else {
        throw new Error('Unexpected response format');
      }
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

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
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
          bgcolor: 'background.default',
          position: 'relative',
          paddingBottom: '80px', // Space for the input box
        }}
      >
        <Container maxWidth="md" sx={{ py: 4, flex: 1, display: 'flex', flexDirection: 'column' }}>
          <Typography variant="h4" component="h1" gutterBottom align="center">
            Math Professor Assistant
          </Typography>
          
          <Paper 
            elevation={3} 
            sx={{ 
              flex: 1, 
              mb: 2, 
              p: 2, 
              overflow: 'auto',
              display: 'flex',
              flexDirection: 'column',
            }}
          >
            {messages.map((msg, index) => (
              <Box
                key={index}
                sx={{
                  textAlign: msg.isUser ? 'right' : 'left',
                  mb: 2,
                }}
              >
                <Paper
                  elevation={1}
                  sx={{
                    display: 'inline-block',
                    p: 2,
                    borderRadius: 2,
                    backgroundColor: msg.isUser ? '#e3f2fd' : '#f5f5f5',
                    maxWidth: '80%',
                    textAlign: 'left',
                    overflowX: 'auto',
                  }}
                >
                  <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
                    <LatexRenderer content={msg.text} />
                  </div>
                </Paper>
              </Box>
            ))}
            {isLoading && (
              <Box sx={{ textAlign: 'left', mb: 2 }}>
                <Paper
                  elevation={1}
                  sx={{
                    display: 'inline-block',
                    p: 2,
                    borderRadius: 2,
                    backgroundColor: '#f5f5f5',
                    maxWidth: '80%',
                  }}
                >
                  <Typography variant="body1">Thinking...</Typography>
                </Paper>
              </Box>
            )}
            <div ref={messagesEndRef} />
          </Paper>
        </Container>
        
        {/* Fixed input box at the bottom */}
        <Box 
          sx={{ 
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            bgcolor: 'background.paper',
            borderTop: '1px solid',
            borderColor: 'divider',
            p: 2,
            zIndex: 1000,
          }}
        >
          <Container maxWidth="md">
            <Box sx={{ display: 'flex', gap: 1 }}>
              <TextField
                fullWidth
                variant="outlined"
                placeholder="Ask a math question..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={isLoading}
                multiline
                maxRows={4}
                sx={{ 
                  bgcolor: 'background.paper',
                  '& .MuiOutlinedInput-root': {
                    bgcolor: 'background.paper',
                  },
                }}
              />
              <Button
                variant="contained"
                color="primary"
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                endIcon={<SendIcon />}
                sx={{ 
                  minWidth: '100px',
                  height: '56px', // Match the input field height
                }}
              >
                Send
              </Button>
            </Box>
          </Container>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;