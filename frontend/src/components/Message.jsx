import React from 'react';
import { Box, Paper } from '@mui/material';
import LatexRenderer from './LatexRenderer';
import FeedbackButtons from './FeedbackButtons';

const Message = ({ message, isUser, onFeedback, showFeedback, feedbackState }) => {
  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        width: '100%',
        '&:first-of-type': {
          marginTop: '8px'
        }
      }}
    >
      <Paper
        elevation={1}
        sx={{
          p: 2,
          borderRadius: '18px',
          backgroundColor: isUser ? '#e3f2fd' : '#f5f5f5',
          maxWidth: '85%',
          textAlign: 'left',
          overflow: 'hidden',
          wordWrap: 'break-word',
          whiteSpace: 'pre-wrap',
          position: 'relative',
          '&:hover': {
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }
        }}
      >
        <LatexRenderer content={message.text} />
        {!isUser && showFeedback && !message.text.includes('Hello! I am your Math Professor') && !message.text.includes("I'm sorry, as a math professor, I can only answer questions about mathematics.") && (
          <FeedbackButtons 
            onFeedback={onFeedback}
            feedbackState={feedbackState}
          />
        )}
      </Paper>
    </Box>
  );
};

export default Message;
