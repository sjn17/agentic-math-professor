import React from 'react';
import 'katex/dist/katex.min.css';
import { InlineMath, BlockMath } from 'react-katex';

const LatexRenderer = ({ content, displayMode = false }) => {
  // First process markdown bold syntax
  const processBold = (text) => {
    const parts = [];
    const boldRegex = /\*\*(.*?)\*\*/g;
    let lastIndex = 0;
    let match;

    while ((match = boldRegex.exec(text)) !== null) {
      // Add text before the match
      if (match.index > lastIndex) {
        parts.push({
          type: 'text',
          content: text.slice(lastIndex, match.index)
        });
      }
      
      // Add the bold content
      parts.push({
        type: 'bold',
        content: match[1]
      });

      lastIndex = match.index + match[0].length;
    }

    // Add any remaining text
    if (lastIndex < text.length) {
      parts.push({
        type: 'text',
        content: text.slice(lastIndex)
      });
    }

    return parts.length > 0 ? parts : [{ type: 'text', content: text }];
  };

  // This regex matches LaTeX expressions between $...$ or $$...$$
  const parts = [];
  const regex = /(\$\$[^$]+\$\$|\$[^$]+\$)/g;
  let lastIndex = 0;
  let match;

  while ((match = regex.exec(content)) !== null) {
    // Add text before the match
    if (match.index > lastIndex) {
      parts.push({
        type: 'text',
        content: content.slice(lastIndex, match.index)
      });
    }

    // Add the LaTeX content
    const latex = match[0];
    const isBlock = latex.startsWith('$$');
    const latexContent = isBlock ? latex.slice(2, -2) : latex.slice(1, -1);
    
    parts.push({
      type: 'latex',
      content: latexContent,
      isBlock
    });

    lastIndex = match.index + match[0].length;
  }

  // Add any remaining text
  if (lastIndex < content.length) {
    parts.push({
      type: 'text',
      content: content.slice(lastIndex)
    });
  }

  // If no LaTeX was found, process for markdown bold only
  if (parts.length === 0) {
    const boldParts = processBold(content);
    return (
      <span>
        {boldParts.map((part, index) => {
          if (part.type === 'bold') {
            return <strong key={index}>{part.content}</strong>;
          }
          return <span key={index}>{part.content}</span>;
        })}
      </span>
    );
  }

  return (
    <span>
      {parts.map((part, index) => {
        if (part.type === 'text') {
          const boldParts = processBold(part.content);
          return (
            <span key={index}>
              {boldParts.map((boldPart, boldIndex) => {
                if (boldPart.type === 'bold') {
                  return <strong key={boldIndex}>{boldPart.content}</strong>;
                }
                return <span key={boldIndex}>{boldPart.content}</span>;
              })}
            </span>
          );
        } else {
          const Component = part.isBlock ? BlockMath : InlineMath;
          return (
            <Component key={index}>
              {part.content}
            </Component>
          );
        }
      })}
    </span>
  );
};

export default LatexRenderer;
