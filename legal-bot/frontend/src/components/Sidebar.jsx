import React, { useState, useEffect, useRef } from 'react';
import ReactDOM from 'react-dom';
import './Sidebar.css';
import { RESOURCES, ICONS } from '../lib/resources.jsx';

// ResourceTile Component
const ResourceTile = ({ id, label, icon, isActive, onClick, isCollapsed }) => {
  const iconFn = ICONS[icon];
  
  return (
    <button
      className={`resource-tile ${isActive ? 'active' : ''}`}
      onClick={() => onClick(id)}
      aria-pressed={isActive}
      title={isCollapsed ? label : undefined}
    >
      <span className="resource-tile-icon">
        {iconFn && iconFn({ size: 16 })}
      </span>
      {!isCollapsed && <span className="resource-tile-label">{label}</span>}
    </button>
  );
};

// Account Menu Dropdown (ChatGPT-style)
const AccountMenuDropdown = ({ 
  user, 
  isOpen, 
  onClose, 
  onLogout, 
  triggerRef,
  onNavigate 
}) => {
  const menuRef = useRef(null);
  const [position, setPosition] = useState({ bottom: 0, left: 0 });
  const [showHelpSubmenu, setShowHelpSubmenu] = useState(false);

  useEffect(() => {
    if (isOpen && triggerRef.current) {
      const rect = triggerRef.current.getBoundingClientRect();
      setPosition({
        bottom: window.innerHeight - rect.top + 8,
        left: rect.left
      });
    }
  }, [isOpen, triggerRef]);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target) &&
          triggerRef.current && !triggerRef.current.contains(e.target)) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen, onClose, triggerRef]);

  if (!isOpen) return null;

  const getInitials = (name) => {
    if (!name) return '?';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
  };

  const handleMenuClick = (action) => {
    onClose();
    if (onNavigate) {
      onNavigate(action);
    }
  };

  return ReactDOM.createPortal(
    <>
      <div className="account-menu-overlay" onClick={onClose} />
      <div 
        ref={menuRef}
        className="account-menu-dropdown"
        style={{ bottom: `${position.bottom}px`, left: `${position.left}px` }}
      >
        {/* User Header */}
        <div className="amd-header">
          <div className="amd-avatar">
            {user?.avatar_url ? (
              <img src={user.avatar_url} alt={user.name} />
            ) : (
              <span>{getInitials(user?.name)}</span>
            )}
          </div>
          <div className="amd-user-info">
            <div className="amd-user-name">{user?.name || 'User'}</div>
            <div className="amd-user-email">{user?.email || ''}</div>
          </div>
        </div>

        <div className="amd-divider" />

        {/* Menu Items */}
        <div className="amd-menu-items">
          <button className="amd-menu-item" onClick={() => handleMenuClick('personalization')}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/>
            </svg>
            <span>Personalization</span>
          </button>

          <button className="amd-menu-item" onClick={() => handleMenuClick('settings')}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="3"/>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
            </svg>
            <span>Settings</span>
          </button>

          <div className="amd-divider" />

          {/* Help submenu */}
          <div className="amd-submenu-container">
            <button 
              className="amd-menu-item amd-has-submenu" 
              onClick={() => setShowHelpSubmenu(!showHelpSubmenu)}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
              <span>Help</span>
              <svg className={`amd-submenu-arrow ${showHelpSubmenu ? 'open' : ''}`} width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </button>
            
            {showHelpSubmenu && (
              <div className="amd-submenu">
                <button className="amd-submenu-item" onClick={() => handleMenuClick('help-center')}>
                  Help Center
                </button>
                <button className="amd-submenu-item" onClick={() => handleMenuClick('release-notes')}>
                  Release Notes
                </button>
                <button className="amd-submenu-item" onClick={() => handleMenuClick('terms')}>
                  Terms and Policies
                </button>
                <button className="amd-submenu-item" onClick={() => handleMenuClick('keyboard-shortcuts')}>
                  Keyboard Shortcuts
                </button>
              </div>
            )}
          </div>

          <div className="amd-divider" />

          <button className="amd-menu-item amd-logout" onClick={onLogout}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
              <polyline points="16 17 21 12 16 7"/>
              <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
            <span>Log out</span>
          </button>
        </div>

        {/* Footer Account Card */}
        <div className="amd-divider" />
        <div className="amd-footer">
          <div className="amd-footer-avatar">
            {user?.avatar_url ? (
              <img src={user.avatar_url} alt={user.name} />
            ) : (
              <span>{getInitials(user?.name)}</span>
            )}
          </div>
          <div className="amd-footer-info">
            <div className="amd-footer-name">{user?.name || 'User'}</div>
            <div className="amd-footer-role">
              {user?.role === 'lawyer' ? 'Lawyer' : 
               user?.role === 'employee_admin' ? 'Admin' : 'Client'}
            </div>
          </div>
        </div>
      </div>
    </>,
    document.body
  );
};

// Sidebar Component
const Sidebar = ({
  activeResource,
  onResourceChange,
  onNewChat,
  onSearchChats,
  chatHistory = [],
  currentChatId,
  onSelectChat,
  isCollapsed = false,
  onToggleCollapse,
  lawTypeSelection,
  user,
  onLogout,
  onNavigate
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showAccountMenu, setShowAccountMenu] = useState(false);
  const accountBtnRef = useRef(null);

  // Persist active resource
  useEffect(() => {
    if (activeResource) {
      localStorage.setItem('legid_active_resource', activeResource);
    }
  }, [activeResource]);

  // Load persisted active resource
  useEffect(() => {
    const saved = localStorage.getItem('legid_active_resource');
    if (saved && !activeResource) {
      onResourceChange(saved);
    }
  }, []);

  const filteredChats = chatHistory.filter(chat => 
    chat.title?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleResourceClick = (resourceId) => {
    onResourceChange(resourceId);
  };

  const getInitials = (name) => {
    if (!name) return '?';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
  };

  return (
    <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      {/* Sidebar Header */}
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <span className="logo-icon">⚖️</span>
          {!isCollapsed && <span className="logo-text">LEGID</span>}
        </div>
        <button 
          className="collapse-btn"
          onClick={onToggleCollapse}
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? ICONS['chevron-right']({ size: 18 }) : ICONS['chevron-left']({ size: 18 })}
        </button>
      </div>

      {/* New Chat Button */}
      <button className="new-chat-btn" onClick={onNewChat}>
        {ICONS.plus({ size: 16 })}
        {!isCollapsed && <span>New Chat</span>}
      </button>

      {/* Search */}
      {!isCollapsed && (
        <div className="sidebar-search">
          {ICONS.search({ size: 14 })}
          <input
            type="text"
            placeholder="Search chats..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
        </div>
      )}

      <div className="sidebar-divider" />

      {/* Resources Section */}
      <div className="sidebar-section">
        {!isCollapsed && <h3 className="section-title">Resources</h3>}
        <div className={`resources-grid ${isCollapsed ? 'collapsed' : ''}`}>
          {RESOURCES.map((resource) => (
            <ResourceTile
              key={resource.id}
              id={resource.id}
              label={resource.label}
              icon={resource.icon}
              isActive={activeResource === resource.id}
              onClick={handleResourceClick}
              isCollapsed={isCollapsed}
            />
          ))}
        </div>
      </div>

      <div className="sidebar-divider" />

      {/* Chat History Section */}
      <div className="sidebar-section chats-section">
        {!isCollapsed && <h3 className="section-title">Your Chats</h3>}
        <div className="chat-list">
          {filteredChats.length > 0 ? (
            filteredChats.map((chat) => (
              <button
                key={chat.id}
                className={`chat-item ${currentChatId === chat.id ? 'active' : ''}`}
                onClick={() => onSelectChat(chat.id)}
                title={chat.title}
              >
                {ICONS.chat({ size: 14 })}
                {!isCollapsed && (
                  <span className="chat-title">{chat.title || 'Untitled Chat'}</span>
                )}
              </button>
            ))
          ) : (
            !isCollapsed && (
              <div className="no-chats">
                <p>No chats yet</p>
              </div>
            )
          )}
        </div>
      </div>

      {/* Spacer to push account to bottom */}
      <div className="sidebar-spacer" />

      {/* Account Button at Bottom (ChatGPT-style) */}
      {user && (
        <div className="sidebar-account">
          <button
            ref={accountBtnRef}
            className="account-button"
            onClick={() => setShowAccountMenu(!showAccountMenu)}
            title={`${user.name || 'User'} - ${user.email || ''}`}
          >
            <div className="account-avatar">
              {user.avatar_url ? (
                <img src={user.avatar_url} alt={user.name} />
              ) : (
                <span>{getInitials(user.name)}</span>
              )}
            </div>
            {!isCollapsed && (
              <>
                <div className="account-info">
                  <span className="account-name">{user.name || 'User'}</span>
                </div>
                <svg className="account-dots" width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                  <circle cx="3" cy="8" r="1.5"/>
                  <circle cx="8" cy="8" r="1.5"/>
                  <circle cx="13" cy="8" r="1.5"/>
                </svg>
              </>
            )}
          </button>

          <AccountMenuDropdown
            user={user}
            isOpen={showAccountMenu}
            onClose={() => setShowAccountMenu(false)}
            onLogout={onLogout}
            triggerRef={accountBtnRef}
            onNavigate={onNavigate}
          />
        </div>
      )}
    </aside>
  );
};

export default Sidebar;
