import React, { useState, useEffect, useRef } from 'react';
import './SidebarProfileMenu.css';

const SidebarProfileMenu = ({ user, onLogout, onViewChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [profile, setProfile] = useState(null);
  const menuRef = useRef(null);
  const buttonRef = useRef(null);

  useEffect(() => {
    // Load profile data when user is available
    if (user) {
      loadProfile();
    }
  }, [user]);

  useEffect(() => {
    // Close menu when clicking outside
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target) &&
          buttonRef.current && !buttonRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
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

  const handleMenuItemClick = (action) => {
    setIsOpen(false);
    switch (action) {
      case 'edit-profile':
        // This will be handled by opening the edit profile modal
        break;
      case 'personalization':
        onViewChange && onViewChange('personalization');
        break;
      case 'settings':
        onViewChange && onViewChange('settings');
        break;
      case 'help':
        onViewChange && onViewChange('help');
        break;
      case 'logout':
        onLogout && onLogout();
        break;
      default:
        break;
    }
  };

  const getInitials = (name) => {
    if (!name) return 'U';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
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

  if (!user) return null;

  const displayName = profile?.display_name || user.name || 'User';
  const avatarUrl = profile?.avatar_url;
  const role = user.role || 'client';

  return (
    <div className="sidebar-profile-menu">
      <button
        ref={buttonRef}
        className="profile-trigger"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="User menu"
      >
        <div className="profile-avatar">
          {avatarUrl ? (
            <img src={avatarUrl} alt={displayName} />
          ) : (
            <div className="avatar-initials">
              {getInitials(displayName)}
            </div>
          )}
        </div>
        <div className="profile-info">
          <div className="profile-name">{displayName}</div>
          <div className="profile-role">{getRoleLabel(role)}</div>
        </div>
        <div className={`profile-arrow ${isOpen ? 'open' : ''}`}>
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
      </button>

      {isOpen && (
        <div className="profile-dropdown" ref={menuRef}>
          <div className="dropdown-header">
            <div className="dropdown-avatar">
              {avatarUrl ? (
                <img src={avatarUrl} alt={displayName} />
              ) : (
                <div className="avatar-initials">
                  {getInitials(displayName)}
                </div>
              )}
            </div>
            <div className="dropdown-info">
              <div className="dropdown-name">{displayName}</div>
              <div className="dropdown-email">{user.email}</div>
            </div>
          </div>

          <div className="dropdown-menu">
            <button
              className="menu-item"
              onClick={() => handleMenuItemClick('edit-profile')}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M11.5 4L12 4.5L7.5 9L6 7.5L6.5 7L7.5 8L11.5 4Z" fill="currentColor"/>
                <path d="M8 1.5C4.41015 1.5 1.5 4.41015 1.5 8C1.5 11.5899 4.41015 14.5 8 14.5C11.5899 14.5 14.5 11.5899 14.5 8C14.5 4.41015 11.5899 1.5 8 1.5ZM8 13.5C5.51472 13.5 3.5 11.4853 3.5 8C3.5 5.51472 5.51472 3.5 8 3.5C10.4853 3.5 12.5 5.51472 12.5 8C12.5 10.4853 10.4853 12.5 8 12.5Z" fill="currentColor"/>
              </svg>
              My Profile
            </button>

            <button
              className="menu-item"
              onClick={() => handleMenuItemClick('personalization')}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M8 2C6.89543 2 6 2.89543 6 4V6.17157C5.375 6.4741 5 7.06799 5 7.75V13H11V7.75C11 7.06799 10.625 6.4741 10 6.17157V4C10 2.89543 9.10457 2 8 2ZM7 4C7 3.44772 7.44772 3 8 3C8.55228 3 9 3.44772 9 4V5H7V4ZM8 8C7.44772 8 7 8.44772 7 9C7 9.55228 7.44772 10 8 10C8.55228 10 9 9.55228 9 9C9 8.44772 8.55228 8 8 8Z" fill="currentColor"/>
              </svg>
              Personalization
            </button>

            <button
              className="menu-item"
              onClick={() => handleMenuItemClick('settings')}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M13.5 8C13.5 9.933 12.433 11.683 10.75 12.5L9.5 11.5C10.833 10.833 11.5 9.5 11.5 8C11.5 6.5 10.833 5.167 9.5 4.5L10.75 3.5C12.433 4.317 13.5 6.067 13.5 8ZM8 10.5C6.61929 10.5 5.5 9.38071 5.5 8C5.5 6.61929 6.61929 5.5 8 5.5C9.38071 5.5 10.5 6.61929 10.5 8C10.5 9.38071 9.38071 10.5 8 10.5ZM8 6.5C7.17157 6.5 6.5 7.17157 6.5 8C6.5 8.82843 7.17157 9.5 8 9.5C8.82843 9.5 9.5 8.82843 9.5 8C9.5 7.17157 8.82843 6.5 8 6.5ZM2.5 8C2.5 6.067 3.567 4.317 5.25 3.5L6.5 4.5C5.167 5.167 4.5 6.5 4.5 8C4.5 9.5 5.167 10.833 6.5 11.5L5.25 12.5C3.567 11.683 2.5 9.933 2.5 8Z" fill="currentColor"/>
              </svg>
              Settings
            </button>

            <button
              className="menu-item"
              onClick={() => handleMenuItemClick('help')}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M8 1.5C4.41015 1.5 1.5 4.41015 1.5 8C1.5 11.5899 4.41015 14.5 8 14.5C11.5899 14.5 14.5 11.5899 14.5 8C14.5 4.41015 11.5899 1.5 8 1.5ZM8 13.5C5.51472 13.5 3.5 11.4853 3.5 8C3.5 5.51472 5.51472 3.5 8 3.5C10.4853 3.5 12.5 5.51472 12.5 8C12.5 10.4853 10.4853 12.5 8 12.5ZM7.5 9.5H8.5V11H7.5V9.5ZM8 3.5C6.61929 3.5 5.5 4.61929 5.5 6H6.5C6.5 5.17157 7.17157 5.5 8 5.5C8.82843 5.5 9.5 5.17157 9.5 6C9.5 6.5 9.5 6.75 9 7L8 7.5C7.5 7.75 7.5 8.5 7.5 9.5H8.5C8.5 8.5 8.5 7.75 9 7.5L9.5 7C10 6.75 10 6.5 10 6C10 4.61929 8.82843 3.5 8 3.5Z" fill="currentColor"/>
              </svg>
              Help & Support
            </button>
          </div>

          <div className="dropdown-footer">
            <div className="account-card">
              <div className="account-avatar">
                {avatarUrl ? (
                  <img src={avatarUrl} alt={displayName} />
                ) : (
                  <div className="avatar-initials">
                    {getInitials(displayName)}
                  </div>
                )}
              </div>
              <div className="account-info">
                <div className="account-name">{displayName}</div>
                <div className="account-role">{getRoleLabel(role)}</div>
              </div>
            </div>

            <button
              className="logout-btn"
              onClick={() => handleMenuItemClick('logout')}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M6 12.5L10.5 8L6 3.5V6.5H1.5V9.5H6V12.5ZM13.5 1.5H7.5C6.94772 1.5 6.5 1.94772 6.5 2.5V5H7.5V3H12.5V13H7.5V11H6.5V13.5C6.5 14.0523 6.94772 14.5 7.5 14.5H13.5C14.0523 14.5 14.5 14.0523 14.5 13.5V2.5C14.5 1.94772 14.0523 1.5 13.5 1.5Z" fill="currentColor"/>
              </svg>
              Log out
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SidebarProfileMenu;