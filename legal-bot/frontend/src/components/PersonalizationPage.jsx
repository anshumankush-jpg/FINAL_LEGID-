import React, { useState, useEffect } from 'react';
import './PersonalizationPage.css';

const API_URL = 'http://localhost:8000';

const PersonalizationPage = ({ user, onBack, onPreferencesUpdate }) => {
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);
  
  const [preferences, setPreferences] = useState({
    theme: 'dark',
    font_size: 'medium',
    response_style: 'detailed',
    auto_read: false,
    language: 'en'
  });

  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_URL}/api/profile`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.profile?.preferences) {
          setPreferences(prev => ({
            ...prev,
            ...data.profile.preferences
          }));
        }
      }
    } catch (error) {
      console.error('Error loading preferences:', error);
    }
  };

  const handleChange = (key, value) => {
    setPreferences(prev => ({ ...prev, [key]: value }));
  };

  const savePreferences = async () => {
    try {
      setSaving(true);
      setMessage(null);

      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_URL}/api/profile/preferences`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(preferences)
      });

      if (response.ok) {
        setMessage({ type: 'success', text: 'Preferences saved successfully' });
        
        // Apply theme immediately
        document.documentElement.setAttribute('data-theme', preferences.theme);
        localStorage.setItem('theme', preferences.theme);
        
        if (onPreferencesUpdate) {
          onPreferencesUpdate(preferences);
        }
      } else {
        setMessage({ type: 'error', text: 'Failed to save preferences' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to save preferences' });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="personalization-page">
      {/* Header */}
      <div className="personalization-header">
        <button className="personalization-back-btn" onClick={onBack}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
          Back
        </button>
        <h1 className="personalization-title">Personalization</h1>
      </div>

      {/* Message */}
      {message && (
        <div className={`personalization-message ${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="personalization-content">
        {/* Theme Section */}
        <div className="pref-section">
          <h2 className="pref-section-title">Theme</h2>
          <p className="pref-section-desc">Choose how LEGID looks to you</p>
          
          <div className="theme-options">
            <button
              className={`theme-option ${preferences.theme === 'dark' ? 'active' : ''}`}
              onClick={() => handleChange('theme', 'dark')}
            >
              <div className="theme-preview dark">
                <div className="tp-header"></div>
                <div className="tp-content"></div>
              </div>
              <span>Dark</span>
            </button>
            
            <button
              className={`theme-option ${preferences.theme === 'light' ? 'active' : ''}`}
              onClick={() => handleChange('theme', 'light')}
            >
              <div className="theme-preview light">
                <div className="tp-header"></div>
                <div className="tp-content"></div>
              </div>
              <span>Light</span>
            </button>
            
            <button
              className={`theme-option ${preferences.theme === 'system' ? 'active' : ''}`}
              onClick={() => handleChange('theme', 'system')}
            >
              <div className="theme-preview system">
                <div className="tp-header"></div>
                <div className="tp-content"></div>
              </div>
              <span>System</span>
            </button>
          </div>
        </div>

        {/* Font Size Section */}
        <div className="pref-section">
          <h2 className="pref-section-title">Font Size</h2>
          <p className="pref-section-desc">Adjust the text size for better readability</p>
          
          <div className="font-size-options">
            <button
              className={`font-option ${preferences.font_size === 'small' ? 'active' : ''}`}
              onClick={() => handleChange('font_size', 'small')}
            >
              <span className="font-preview small">Aa</span>
              <span>Small</span>
            </button>
            
            <button
              className={`font-option ${preferences.font_size === 'medium' ? 'active' : ''}`}
              onClick={() => handleChange('font_size', 'medium')}
            >
              <span className="font-preview medium">Aa</span>
              <span>Medium</span>
            </button>
            
            <button
              className={`font-option ${preferences.font_size === 'large' ? 'active' : ''}`}
              onClick={() => handleChange('font_size', 'large')}
            >
              <span className="font-preview large">Aa</span>
              <span>Large</span>
            </button>
          </div>
        </div>

        {/* Response Style Section */}
        <div className="pref-section">
          <h2 className="pref-section-title">Response Style</h2>
          <p className="pref-section-desc">How should LEGID respond to your questions?</p>
          
          <div className="response-options">
            <button
              className={`response-option ${preferences.response_style === 'concise' ? 'active' : ''}`}
              onClick={() => handleChange('response_style', 'concise')}
            >
              <div className="response-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="4" y1="9" x2="20" y2="9"/>
                  <line x1="4" y1="15" x2="12" y2="15"/>
                </svg>
              </div>
              <div className="response-text">
                <strong>Concise</strong>
                <span>Brief, to-the-point answers</span>
              </div>
            </button>
            
            <button
              className={`response-option ${preferences.response_style === 'detailed' ? 'active' : ''}`}
              onClick={() => handleChange('response_style', 'detailed')}
            >
              <div className="response-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="4" y1="6" x2="20" y2="6"/>
                  <line x1="4" y1="12" x2="20" y2="12"/>
                  <line x1="4" y1="18" x2="16" y2="18"/>
                </svg>
              </div>
              <div className="response-text">
                <strong>Detailed</strong>
                <span>Comprehensive explanations</span>
              </div>
            </button>
            
            <button
              className={`response-option ${preferences.response_style === 'legal' ? 'active' : ''}`}
              onClick={() => handleChange('response_style', 'legal')}
            >
              <div className="response-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="4" width="18" height="16" rx="2"/>
                  <line x1="7" y1="8" x2="17" y2="8"/>
                  <line x1="7" y1="12" x2="17" y2="12"/>
                  <line x1="7" y1="16" x2="13" y2="16"/>
                </svg>
              </div>
              <div className="response-text">
                <strong>Legal Format</strong>
                <span>Professional legal style with citations</span>
              </div>
            </button>
          </div>
        </div>

        {/* Language Section */}
        <div className="pref-section">
          <h2 className="pref-section-title">Language</h2>
          <p className="pref-section-desc">Primary language for responses</p>
          
          <select
            className="language-select"
            value={preferences.language}
            onChange={(e) => handleChange('language', e.target.value)}
          >
            <option value="en">English</option>
            <option value="fr">French</option>
            <option value="es">Spanish</option>
            <option value="hi">Hindi</option>
            <option value="pa">Punjabi</option>
          </select>
        </div>

        {/* Auto-Read Section */}
        <div className="pref-section">
          <div className="pref-toggle-row">
            <div className="pref-toggle-info">
              <h2 className="pref-section-title">Auto-Read Responses</h2>
              <p className="pref-section-desc">Automatically read responses aloud</p>
            </div>
            <div className="toggle">
              <input
                type="checkbox"
                checked={preferences.auto_read}
                onChange={(e) => handleChange('auto_read', e.target.checked)}
              />
              <span className="toggle-slider"></span>
            </div>
          </div>
        </div>

        {/* Save Button */}
        <button
          className="save-preferences-btn"
          onClick={savePreferences}
          disabled={saving}
        >
          {saving ? 'Saving...' : 'Save Preferences'}
        </button>
      </div>
    </div>
  );
};

export default PersonalizationPage;
