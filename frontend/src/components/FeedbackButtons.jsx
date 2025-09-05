import React from 'react';

const FeedbackButtons = ({ onFeedback, feedbackState }) => {
  const buttons = [
    { type: 'correct', label: '✅ Correct', color: '#4caf50' },
    { type: 'incorrect', label: '❌ Incorrect', color: '#f44336' },
    { type: 'clarify', label: '🔄 Clarify', color: '#2196f3' },
  ];

  return (
    <div style={{ 
      display: 'flex', 
      gap: '8px', 
      marginTop: '8px',
      flexWrap: 'wrap'
    }}>
      {buttons.map(({ type, label, color }) => (
        <button
          key={type}
          onClick={() => onFeedback(type)}
          style={{
            background: 'transparent',
            border: `1px solid ${color}`,
            borderRadius: '4px',
            padding: '2px 8px',
            cursor: 'pointer',
            color: feedbackState === type ? 'white' : color,
            backgroundColor: feedbackState === type ? color : 'transparent',
            transition: 'all 0.2s',
            ':hover': {
              opacity: 0.9
            }
          }}
        >
          {label}
        </button>
      ))}
    </div>
  );
};

export default FeedbackButtons;
