import React, { useState, useEffect } from 'react';
import './SettingsPage.css';

const SettingsPage = ({ user, onBack }) => {
  const [profile, setProfile] = useState(null);
  const [consent, setConsent] = useState({
    necessary: true,
    analytics: false,
    marketing: false,
    functional: true
  });
  const [isLoading, setIsLoading] = useState(false);
  const [showEditProfile, setShowEditProfile] = useState(false);

  useEffect(() => {
    loadProfile();
    loadConsent();
  }, []);

  const loadProfile = async () => {
    try {
      const response = await fetch('/api/profile', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setProfile(data);
      }
    } catch (error) {
      console.error('Error loading profile:', error);
    }
  };

  const loadConsent = async () => {
    try {
      const response = await fetch('/api/profile/consent', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setConsent({
          necessary: data.necessary || true,
          analytics: data.analytics || false,
          marketing: data.marketing || false,
          functional: data.functional || true
        });
      }
    } catch (error) {
      console.error('Error loading consent:', error);
    }
  };

  const handleConsentChange = async (key, value) => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/profile/consent', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          [key]: value
        })
      });

      if (response.ok) {
        setConsent(prev => ({ ...prev, [key]: value }));
      } else {
        console.error('Error updating consent');
      }
    } catch (error) {
      console.error('Error updating consent:', error);
    }
    setIsLoading(false);
  };

  const getRoleLabel = (role) => {
    const roleLabels = {
      'client': 'User',
      'lawyer': 'Lawyer',
      'employee': 'Employee',
      'employee_admin': 'Admin'
    };
    return roleLabels[role] || 'User';
  };

  const getLawyerStatusLabel = (status) => {
    const statusLabels = {
      'not_applicable': 'N/A',
      'pending': 'Pending Verification',
      'approved': 'Verified',
      'rejected': 'Rejected'
    };
    return statusLabels[status] || 'Unknown';
  };

  return (
    <div className="settings-page">
      <div className="page-header">
        <button className="back-btn" onClick={onBack}>
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M15 18L9 12L15 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Back
        </button>
        <h1>Settings</h1>
        <p>Manage your account and preferences</p>
      </div>

      <div className="settings-content">
        {/* Profile Section */}
        <div className="settings-section">
          <h2>Profile</h2>
          <p>Manage your personal information and profile settings</p>

          <div className="profile-card">
            <div className="profile-header">
              <div className="profile-avatar">
                {profile?.avatar_url ? (
                  <img src={profile.avatar_url} alt={profile.display_name || user.name} />
                ) : (
                  <div className="avatar-initials">
                    {(profile?.display_name || user.name || 'U').split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
                  </div>
                )}
              </div>
              <div className="profile-info">
                <h3>{profile?.display_name || user.name || 'User'}</h3>
                <p>{user.email}</p>
                {profile?.username && (
                  <p className="username">@{profile.username}</p>
                )}
              </div>
            </div>

            <button
              className="edit-profile-btn"
              onClick={() => setShowEditProfile(true)}
            >
              Edit Profile
            </button>
          </div>
        </div>

        {/* Privacy & Cookies Section */}
        <div className="settings-section">
          <h2>Privacy & Cookies</h2>
          <p>Control how we use your data and cookies</p>

          <div className="consent-settings">
            <div className="consent-item">
              <div className="consent-info">
                <h4>Necessary Cookies</h4>
                <p>Essential cookies required for the website to function properly.</p>
              </div>
              <div className="consent-toggle">
                <label className="toggle-switch">
                  <input
                    type="checkbox"
                    checked={consent.necessary}
                    disabled={true} // Always required
                  />
                  <span className="toggle-slider disabled"></span>
                </label>
                <span className="always-on">Always on</span>
              </div>
            </div>

            <div className="consent-item">
              <div className="consent-info">
                <h4>Analytics Cookies</h4>
                <p>Help us understand how you use LegalAI to improve our service.</p>
              </div>
              <div className="consent-toggle">
                <label className="toggle-switch">
                  <input
                    type="checkbox"
                    checked={consent.analytics}
                    onChange={(e) => handleConsentChange('analytics', e.target.checked)}
                    disabled={isLoading}
                  />
                  <span className="toggle-slider"></span>
                </label>
              </div>
            </div>

            <div className="consent-item">
              <div className="consent-info">
                <h4>Functional Cookies</h4>
                <p>Enable enhanced features and personalization.</p>
              </div>
              <div className="consent-toggle">
                <label className="toggle-switch">
                  <input
                    type="checkbox"
                    checked={consent.functional}
                    onChange={(e) => handleConsentChange('functional', e.target.checked)}
                    disabled={isLoading}
                  />
                  <span className="toggle-slider"></span>
                </label>
              </div>
            </div>

            <div className="consent-item">
              <div className="consent-info">
                <h4>Marketing Cookies</h4>
                <p>Allow us to show you relevant advertisements and content.</p>
              </div>
              <div className="consent-toggle">
                <label className="toggle-switch">
                  <input
                    type="checkbox"
                    checked={consent.marketing}
                    onChange={(e) => handleConsentChange('marketing', e.target.checked)}
                    disabled={isLoading}
                  />
                  <span className="toggle-slider"></span>
                </label>
              </div>
            </div>
          </div>
        </div>

        {/* Account Information Section */}
        <div className="settings-section">
          <h2>Account Information</h2>
          <p>View your account details and status</p>

          <div className="account-info">
            <div className="info-row">
              <span className="label">Email</span>
              <span className="value">{user.email}</span>
            </div>

            <div className="info-row">
              <span className="label">Role</span>
              <span className="value">{getRoleLabel(user.role)}</span>
            </div>

            {user.role === 'lawyer' && profile?.lawyer_status && (
              <div className="info-row">
                <span className="label">Lawyer Status</span>
                <span className={`value status-${profile.lawyer_status}`}>
                  {getLawyerStatusLabel(profile.lawyer_status)}
                </span>
              </div>
            )}

            <div className="info-row">
              <span className="label">Member Since</span>
              <span className="value">
                {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'Unknown'}
              </span>
            </div>

            <div className="info-row">
              <span className="label">Last Login</span>
              <span className="value">
                {user.last_login_at ? new Date(user.last_login_at).toLocaleDateString() : 'Unknown'}
              </span>
            </div>
          </div>
        </div>

        {/* Danger Zone */}
        <div className="settings-section danger-zone">
          <h2>Danger Zone</h2>
          <p>Irreversible actions that affect your account</p>

          <div className="danger-actions">
            <div className="danger-item">
              <div className="danger-info">
                <h4>Log out from all devices</h4>
                <p>Sign out from all browsers and devices where you're currently logged in.</p>
              </div>
              <button className="danger-btn">
                Log out everywhere
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Edit Profile Modal - We'll import and use the existing EditProfileModal */}
      {showEditProfile && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-placeholder">
              <p>Edit Profile Modal would open here</p>
              <p>(Import and integrate EditProfileModal component)</p>
              <button onClick={() => setShowEditProfile(false)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SettingsPage;