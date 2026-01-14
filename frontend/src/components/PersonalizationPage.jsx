import React, { useState, useEffect } from 'react';
import './PersonalizationPage.css';

const PersonalizationPage = ({ user, onBack }) => {
  const [preferences, setPreferences] = useState({
    theme: 'dark',
    font_size: 'medium',
    response_style: 'detailed',
    auto_read: false,
    language: 'en'
  });

  const [isLoading, setIsLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState(''); // 'saving', 'saved', 'error'

  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    try {
      const response = await fetch('/api/profile', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        if (data.preferences_json) {
          setPreferences(prev => ({ ...prev, ...data.preferences_json }));
        }
      }
    } catch (error) {
      console.error('Error loading preferences:', error);
    }
  };

  const handlePreferenceChange = (key, value) => {
    setPreferences(prev => ({ ...prev, [key]: value }));
  };

  const handleSave = async () => {
    setIsLoading(true);
    setSaveStatus('saving');

    try {
      const response = await fetch('/api/profile/preferences', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(preferences)
      });

      if (response.ok) {
        setSaveStatus('saved');
        setTimeout(() => setSaveStatus(''), 2000);
      } else {
        setSaveStatus('error');
      }
    } catch (error) {
      console.error('Error saving preferences:', error);
      setSaveStatus('error');
    }

    setIsLoading(false);
  };

  const handleReset = () => {
    const defaultPrefs = {
      theme: 'dark',
      font_size: 'medium',
      response_style: 'detailed',
      auto_read: false,
      language: 'en'
    };
    setPreferences(defaultPrefs);
  };

  return (
    <div className="personalization-page">
      <div className="page-header">
        <button className="back-btn" onClick={onBack}>
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M15 18L9 12L15 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Back
        </button>
        <h1>Personalization</h1>
        <p>Customize your LegalAI experience</p>
      </div>

      <div className="personalization-content">
        {/* Theme Section */}
        <div className="preference-section">
          <h2>Theme</h2>
          <p>Choose your preferred color scheme</p>

          <div className="option-grid">
            <label className={`option-card ${preferences.theme === 'dark' ? 'selected' : ''}`}>
              <input
                type="radio"
                name="theme"
                value="dark"
                checked={preferences.theme === 'dark'}
                onChange={(e) => handlePreferenceChange('theme', e.target.value)}
              />
              <div className="option-visual">
                <div className="theme-preview dark-preview"></div>
              </div>
              <div className="option-label">
                <strong>Dark</strong>
                <span>Easy on the eyes</span>
              </div>
            </label>

            <label className={`option-card ${preferences.theme === 'light' ? 'selected' : ''}`}>
              <input
                type="radio"
                name="theme"
                value="light"
                checked={preferences.theme === 'light'}
                onChange={(e) => handlePreferenceChange('theme', e.target.value)}
              />
              <div className="option-visual">
                <div className="theme-preview light-preview"></div>
              </div>
              <div className="option-label">
                <strong>Light</strong>
                <span>Classic and clean</span>
              </div>
            </label>

            <label className={`option-card ${preferences.theme === 'system' ? 'selected' : ''}`}>
              <input
                type="radio"
                name="theme"
                value="system"
                checked={preferences.theme === 'system'}
                onChange={(e) => handlePreferenceChange('theme', e.target.value)}
              />
              <div className="option-visual">
                <div className="theme-preview system-preview"></div>
              </div>
              <div className="option-label">
                <strong>System</strong>
                <span>Follow device setting</span>
              </div>
            </label>
          </div>
        </div>

        {/* Font Size Section */}
        <div className="preference-section">
          <h2>Font Size</h2>
          <p>Adjust the text size for better readability</p>

          <div className="option-grid">
            <label className={`option-card ${preferences.font_size === 'small' ? 'selected' : ''}`}>
              <input
                type="radio"
                name="font_size"
                value="small"
                checked={preferences.font_size === 'small'}
                onChange={(e) => handlePreferenceChange('font_size', e.target.value)}
              />
              <div className="option-visual">
                <div className="font-preview small-font">Aa</div>
              </div>
              <div className="option-label">
                <strong>Small</strong>
                <span>Compact and efficient</span>
              </div>
            </label>

            <label className={`option-card ${preferences.font_size === 'medium' ? 'selected' : ''}`}>
              <input
                type="radio"
                name="font_size"
                value="medium"
                checked={preferences.font_size === 'medium'}
                onChange={(e) => handlePreferenceChange('font_size', e.target.value)}
              />
              <div className="option-visual">
                <div className="font-preview medium-font">Aa</div>
              </div>
              <div className="option-label">
                <strong>Medium</strong>
                <span>Balanced and comfortable</span>
              </div>
            </label>

            <label className={`option-card ${preferences.font_size === 'large' ? 'selected' : ''}`}>
              <input
                type="radio"
                name="font_size"
                value="large"
                checked={preferences.font_size === 'large'}
                onChange={(e) => handlePreferenceChange('font_size', e.target.value)}
              />
              <div className="option-visual">
                <div className="font-preview large-font">Aa</div>
              </div>
              <div className="option-label">
                <strong>Large</strong>
                <span>Easier to read</span>
              </div>
            </label>
          </div>
        </div>

        {/* Response Style Section */}
        <div className="preference-section">
          <h2>Response Style</h2>
          <p>Choose how detailed you want AI responses to be</p>

          <div className="option-grid">
            <label className={`option-card ${preferences.response_style === 'concise' ? 'selected' : ''}`}>
              <input
                type="radio"
                name="response_style"
                value="concise"
                checked={preferences.response_style === 'concise'}
                onChange={(e) => handlePreferenceChange('response_style', e.target.value)}
              />
              <div className="option-visual">
                <div className="response-preview concise-preview">
                  <div className="response-bar short"></div>
                </div>
              </div>
              <div className="option-label">
                <strong>Concise</strong>
                <span>Brief and to the point</span>
              </div>
            </label>

            <label className={`option-card ${preferences.response_style === 'balanced' ? 'selected' : ''}`}>
              <input
                type="radio"
                name="response_style"
                value="balanced"
                checked={preferences.response_style === 'balanced'}
                onChange={(e) => handlePreferenceChange('response_style', e.target.value)}
              />
              <div className="option-visual">
                <div className="response-preview balanced-preview">
                  <div className="response-bar medium"></div>
                </div>
              </div>
              <div className="option-label">
                <strong>Balanced</strong>
                <span>Good detail without being overwhelming</span>
              </div>
            </label>

            <label className={`option-card ${preferences.response_style === 'detailed' ? 'selected' : ''}`}>
              <input
                type="radio"
                name="response_style"
                value="detailed"
                checked={preferences.response_style === 'detailed'}
                onChange={(e) => handlePreferenceChange('response_style', e.target.value)}
              />
              <div className="option-visual">
                <div className="response-preview detailed-preview">
                  <div className="response-bar long"></div>
                </div>
              </div>
              <div className="option-label">
                <strong>Detailed</strong>
                <span>Comprehensive with all context</span>
              </div>
            </label>
          </div>
        </div>

        {/* Legal Tone Section */}
        <div className="preference-section">
          <h2>Legal Tone</h2>
          <p>Set the formality level of legal responses</p>

          <div className="option-grid">
            <label className={`option-card ${preferences.legal_tone === 'neutral' ? 'selected' : ''}`}>
              <input
                type="radio"
                name="legal_tone"
                value="neutral"
                checked={preferences.legal_tone === 'neutral'}
                onChange={(e) => handlePreferenceChange('legal_tone', e.target.value)}
              />
              <div className="option-visual">
                <div className="tone-preview neutral-preview">
                  <span>⚖️</span>
                </div>
              </div>
              <div className="option-label">
                <strong>Neutral</strong>
                <span>Professional and balanced</span>
              </div>
            </label>

            <label className={`option-card ${preferences.legal_tone === 'firm' ? 'selected' : ''}`}>
              <input
                type="radio"
                name="legal_tone"
                value="firm"
                checked={preferences.legal_tone === 'firm'}
                onChange={(e) => handlePreferenceChange('legal_tone', e.target.value)}
              />
              <div className="option-visual">
                <div className="tone-preview firm-preview">
                  <span>🏛️</span>
                </div>
              </div>
              <div className="option-label">
                <strong>Firm</strong>
                <span>Authoritative and confident</span>
              </div>
            </label>

            <label className={`option-card ${preferences.legal_tone === 'very_formal' ? 'selected' : ''}`}>
              <input
                type="radio"
                name="legal_tone"
                value="very_formal"
                checked={preferences.legal_tone === 'very_formal'}
                onChange={(e) => handlePreferenceChange('legal_tone', e.target.value)}
              />
              <div className="option-visual">
                <div className="tone-preview formal-preview">
                  <span>📜</span>
                </div>
              </div>
              <div className="option-label">
                <strong>Very Formal</strong>
                <span>Traditional legal language</span>
              </div>
            </label>
          </div>
        </div>

        {/* Auto-read Toggle */}
        <div className="preference-section">
          <h2>Voice Features</h2>
          <p>Control how LegalAI interacts with voice</p>

          <div className="toggle-option">
            <div className="toggle-info">
              <strong>Auto-read responses</strong>
              <span>Automatically read AI responses aloud</span>
            </div>
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={preferences.auto_read || false}
                onChange={(e) => handlePreferenceChange('auto_read', e.target.checked)}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>
        </div>

        {/* Language Section */}
        <div className="preference-section">
          <h2>Language</h2>
          <p>Select your preferred language for the interface</p>

          <div className="language-select">
            <select
              value={preferences.language || 'en'}
              onChange={(e) => handlePreferenceChange('language', e.target.value)}
            >
              <option value="en">English</option>
              <option value="fr">Français</option>
              <option value="es">Español</option>
              <option value="de">Deutsch</option>
            </select>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="page-actions">
        <button
          className="reset-btn"
          onClick={handleReset}
          disabled={isLoading}
        >
          Reset to Defaults
        </button>

        <div className="save-section">
          {saveStatus === 'saving' && <span className="save-status saving">Saving...</span>}
          {saveStatus === 'saved' && <span className="save-status saved">✓ Saved</span>}
          {saveStatus === 'error' && <span className="save-status error">✗ Error saving</span>}

          <button
            className="save-btn"
            onClick={handleSave}
            disabled={isLoading}
          >
            {isLoading ? 'Saving...' : 'Save Preferences'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default PersonalizationPage;