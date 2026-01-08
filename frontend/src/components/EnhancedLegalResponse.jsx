import React, { useState, useEffect } from 'react';
import './EnhancedLegalResponse.css';

// Typing animation component
const TypingText = ({ text, speed = 20 }) => {
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (currentIndex < text.length) {
      const timeout = setTimeout(() => {
        setDisplayedText(prev => prev + text[currentIndex]);
        setCurrentIndex(prev => prev + 1);
      }, speed);
      return () => clearTimeout(timeout);
    }
  }, [currentIndex, text, speed]);

  return <span>{displayedText}</span>;
};

// Animated section component
const AnimatedSection = ({ children, delay = 0 }) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const timeout = setTimeout(() => {
      setIsVisible(true);
    }, delay);
    return () => clearTimeout(timeout);
  }, [delay]);

  return (
    <div style={{ 
      opacity: isVisible ? 1 : 0,
      transform: isVisible ? 'translateY(0)' : 'translateY(10px)',
      transition: 'all 0.5s ease-out'
    }}>
      {children}
    </div>
  );
};

const EnhancedLegalResponse = ({ response }) => {
  // Function to convert URLs to clickable links
  const linkifyText = (text) => {
    if (!text) return text;
    
    // Regular expression to match URLs
    const urlRegex = /(https?:\/\/[^\s\)]+)/g;
    
    const parts = text.split(urlRegex);
    
    return parts.map((part, index) => {
      if (part.match(urlRegex)) {
        return (
          <a 
            key={index} 
            href={part} 
            target="_blank" 
            rel="noopener noreferrer"
            className="response-link"
          >
            {part}
          </a>
        );
      }
      return part;
    });
  };

  // Parse the structured response
  const parseStructuredResponse = (answer) => {
    const lines = answer.split('\n');
    let currentSection = null;
    const sections = {
      offense: [],
      solution: [],
      reference: [],
      statistics: []
    };

    for (const line of lines) {
      const trimmedLine = line.trim();

      if (trimmedLine.includes('🎯 OFFENSE:') || trimmedLine.includes('OFFENSE:')) {
        currentSection = 'offense';
        continue;
      } else if (trimmedLine.includes('💡 SOLUTION:') || trimmedLine.includes('SOLUTION:')) {
        currentSection = 'solution';
        continue;
      } else if (trimmedLine.includes('📚 REFERENCE:') || trimmedLine.includes('REFERENCE:')) {
        currentSection = 'reference';
        continue;
      } else if (trimmedLine.includes('📊 STATISTICS:') || trimmedLine.includes('STATISTICS:')) {
        currentSection = 'statistics';
        continue;
      }

      if (currentSection && trimmedLine && !trimmedLine.startsWith('---')) {
        sections[currentSection].push(trimmedLine);
      }
    }

    return sections;
  };

  // Get answer from either response.answer or response.content
  const answerText = response.answer || response.content || '';
  const sections = parseStructuredResponse(answerText);

  return (
    <div className="enhanced-legal-response">
      {/* Offense Section */}
      {sections.offense.length > 0 && (
        <AnimatedSection delay={100}>
          <div className="response-section offense-section">
            <div className="section-header">
              <span className="section-icon">🎯</span>
              <h3>OFFENSE</h3>
            </div>
            <div className="section-content">
              {sections.offense.map((line, index) => (
                <p key={index} className="offense-text">
                  {linkifyText(line)}
                </p>
              ))}
            </div>
          </div>
        </AnimatedSection>
      )}

      {/* Solution Section */}
      {sections.solution.length > 0 && (
        <AnimatedSection delay={300}>
          <div className="response-section solution-section">
            <div className="section-header">
              <span className="section-icon">💡</span>
              <h3>SOLUTION</h3>
            </div>
            <div className="section-content">
              <ol className="solution-list">
                {sections.solution.map((line, index) => {
                  // Remove numbering if present (e.g., "1. " at start)
                  const cleanLine = line.replace(/^\d+\.\s*/, '').trim();
                  if (cleanLine && cleanLine.length > 10) { // Filter out very short fragments
                    return (
                      <li key={index} className="solution-item">
                        {linkifyText(cleanLine)}
                      </li>
                    );
                  }
                  return null;
                }).filter(Boolean)}
              </ol>
            </div>
          </div>
        </AnimatedSection>
      )}

      {/* Reference Section - Only show if there are structured references */}
      {sections.reference.length > 0 && (
        <AnimatedSection delay={500}>
          <div className="response-section reference-section">
            <div className="section-header">
              <span className="section-icon">📚</span>
              <h3>REFERENCE</h3>
            </div>
            <div className="section-content">
              {sections.reference.map((line, index) => {
                if (line.includes('[') && line.includes(']')) {
                  return <p key={index} className="reference-item">{linkifyText(line)}</p>;
                }
                return null;
              }).filter(Boolean)}
            </div>
          </div>
        </AnimatedSection>
      )}

      {/* Statistics Section */}
      {sections.statistics.length > 0 && (
        <AnimatedSection delay={700}>
          <div className="response-section statistics-section">
            <div className="section-header">
              <span className="section-icon">📊</span>
              <h3>STATISTICS</h3>
            </div>
            <div className="section-content">
              {sections.statistics.map((line, index) => (
                <p key={index} className="statistics-item">{linkifyText(line)}</p>
              ))}
            </div>
          </div>
        </AnimatedSection>
      )}

      {/* Fallback for unstructured responses */}
      {sections.offense.length === 0 && sections.solution.length === 0 && sections.reference.length === 0 && (
        <div className="fallback-response">
          {answerText && answerText.trim() ? (
            <div className="message-text">
              {linkifyText(answerText)}
            </div>
          ) : (
            <p className="no-response">No response received. Please try again.</p>
          )}
        </div>
      )}

      {/* Response metadata - only show chunks, removed confidence */}
      {response.chunks_used > 0 && (
        <div className="response-metadata">
          <span className="chunks-badge">
            Analyzed {response.chunks_used} document chunks
          </span>
        </div>
      )}
    </div>
  );
};

export default EnhancedLegalResponse;