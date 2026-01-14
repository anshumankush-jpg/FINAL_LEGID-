import React, { useState, useEffect } from 'react';
import './CookieConsentBanner.css';

const API_URL = 'http://localhost:8000';

const CookieConsentBanner = ({ user, onAccept }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [consent, setConsent] = useState({
    necessary: true,
    functional: true,
    analytics: false,
    marketing: false
  });

  useEffect(() => {
    // Check if consent has already been given
    const savedConsent = localStorage.getItem('cookie_consent');
    if (!savedConsent) {
      setIsVisible(true);
    }
  }, []);

  const handleConsentChange = (key, value) => {
    if (key === 'necessary') return; // Can't disable necessary cookies
    setConsent(prev => ({ ...prev, [key]: value }));
  };

  const acceptAll = async () => {
    const fullConsent = {
      necessary: true,
      functional: true,
      analytics: true,
      marketing: true
    };
    await saveConsent(fullConsent);
  };

  const acceptSelected = async () => {
    await saveConsent(consent);
  };

  const rejectOptional = async () => {
    const minimalConsent = {
      necessary: true,
      functional: false,
      analytics: false,
      marketing: false
    };
    await saveConsent(minimalConsent);
  };

  const saveConsent = async (consentData) => {
    // Save to localStorage
    localStorage.setItem('cookie_consent', JSON.stringify(consentData));
    localStorage.setItem('cookie_consent_date', new Date().toISOString());

    // If user is logged in, save to backend
    if (user) {
      try {
        const token = localStorage.getItem('access_token');
        await fetch(`${API_URL}/api/profile/consent`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(consentData)
        });
      } catch (error) {
        console.error('Error saving consent to server:', error);
      }
    }

    setIsVisible(false);
    if (onAccept) {
      onAccept(consentData);
    }
  };

  if (!isVisible) return null;

  return (
    <div className="cookie-consent-overlay">
      <div className="cookie-consent-banner">
        {/* Header */}
        <div className="ccb-header">
          <div className="ccb-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <circle cx="8" cy="10" r="1" fill="currentColor"/>
              <circle cx="16" cy="10" r="1" fill="currentColor"/>
              <circle cx="10" cy="15" r="1" fill="currentColor"/>
              <circle cx="14" cy="14" r="1" fill="currentColor"/>
              <circle cx="12" cy="8" r="0.5" fill="currentColor"/>
            </svg>
          </div>
          <div className="ccb-title-section">
            <h2 className="ccb-title">Cookie Preferences</h2>
            <p className="ccb-subtitle">We use cookies to enhance your experience</p>
          </div>
        </div>

        {/* Main Content */}
        <div className="ccb-content">
          <p className="ccb-description">
            We use cookies to personalize content, provide security features, and analyze our traffic. 
            You can customize your preferences or accept all cookies.
          </p>

          {/* Cookie Details (expandable) */}
          {showDetails && (
            <div className="ccb-details">
              <div className="ccb-cookie-item">
                <div className="ccb-cookie-info">
                  <h4>Necessary Cookies</h4>
                  <p>Required for the website to function properly. Cannot be disabled.</p>
                </div>
                <div className="ccb-toggle disabled">
                  <input type="checkbox" checked disabled />
                  <span className="ccb-toggle-slider"></span>
                </div>
              </div>

              <div className="ccb-cookie-item">
                <div className="ccb-cookie-info">
                  <h4>Functional Cookies</h4>
                  <p>Remember your preferences and settings.</p>
                </div>
                <div className="ccb-toggle">
                  <input
                    type="checkbox"
                    checked={consent.functional}
                    onChange={(e) => handleConsentChange('functional', e.target.checked)}
                  />
                  <span className="ccb-toggle-slider"></span>
                </div>
              </div>

              <div className="ccb-cookie-item">
                <div className="ccb-cookie-info">
                  <h4>Analytics Cookies</h4>
                  <p>Help us understand how you use our service.</p>
                </div>
                <div className="ccb-toggle">
                  <input
                    type="checkbox"
                    checked={consent.analytics}
                    onChange={(e) => handleConsentChange('analytics', e.target.checked)}
                  />
                  <span className="ccb-toggle-slider"></span>
                </div>
              </div>

              <div className="ccb-cookie-item">
                <div className="ccb-cookie-info">
                  <h4>Marketing Cookies</h4>
                  <p>Used to show you relevant content and offers.</p>
                </div>
                <div className="ccb-toggle">
                  <input
                    type="checkbox"
                    checked={consent.marketing}
                    onChange={(e) => handleConsentChange('marketing', e.target.checked)}
                  />
                  <span className="ccb-toggle-slider"></span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="ccb-actions">
          <button 
            className="ccb-toggle-details" 
            onClick={() => setShowDetails(!showDetails)}
          >
            {showDetails ? 'Hide Details' : 'Customize'}
          </button>

          <div className="ccb-buttons">
            {showDetails ? (
              <>
                <button className="ccb-btn ccb-btn-secondary" onClick={rejectOptional}>
                  Reject Optional
                </button>
                <button className="ccb-btn ccb-btn-primary" onClick={acceptSelected}>
                  Save Preferences
                </button>
              </>
            ) : (
              <>
                <button className="ccb-btn ccb-btn-secondary" onClick={rejectOptional}>
                  Necessary Only
                </button>
                <button className="ccb-btn ccb-btn-primary" onClick={acceptAll}>
                  Accept All
                </button>
              </>
            )}
          </div>
        </div>

        {/* Footer Links */}
        <div className="ccb-footer">
          <a href="/privacy" className="ccb-link">Privacy Policy</a>
          <span className="ccb-separator">|</span>
          <a href="/cookies" className="ccb-link">Cookie Policy</a>
          <span className="ccb-separator">|</span>
          <a href="/terms" className="ccb-link">Terms of Service</a>
        </div>
      </div>
    </div>
  );
};

export default CookieConsentBanner;
