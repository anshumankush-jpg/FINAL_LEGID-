import React, { useState, useEffect, useRef } from 'react';
import './EditProfileModal.css';

const EditProfileModal = ({ isOpen, onClose, user, onProfileUpdate }) => {
  const [profile, setProfile] = useState({
    display_name: '',
    username: '',
    avatar_url: '',
    phone: '',
    address_line_1: '',
    address_line_2: '',
    city: '',
    province_state: '',
    postal_zip: '',
    country: ''
  });

  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [errors, setErrors] = useState({});
  const [usernameChecking, setUsernameChecking] = useState(false);
  const [usernameAvailable, setUsernameAvailable] = useState(null);

  const fileInputRef = useRef(null);

  useEffect(() => {
    if (isOpen && user) {
      loadProfile();
    }
  }, [isOpen, user]);

  const loadProfile = async () => {
    try {
      const response = await fetch('/api/profile', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setProfile({
          display_name: data.display_name || user.name || '',
          username: data.username || '',
          avatar_url: data.avatar_url || '',
          phone: data.phone || '',
          address_line_1: data.address?.line_1 || '',
          address_line_2: data.address?.line_2 || '',
          city: data.address?.city || '',
          province_state: data.address?.province_state || '',
          postal_zip: data.address?.postal_zip || '',
          country: data.address?.country || ''
        });
      }
    } catch (error) {
      console.error('Error loading profile:', error);
    }
  };

  const handleInputChange = (field, value) => {
    setProfile(prev => ({ ...prev, [field]: value }));

    // Clear field-specific errors
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }

    // Check username availability when it changes
    if (field === 'username' && value && value !== profile.username) {
      checkUsernameAvailability(value);
    }
  };

  const checkUsernameAvailability = async (username) => {
    if (!username || username.length < 3) {
      setUsernameAvailable(null);
      return;
    }

    setUsernameChecking(true);
    try {
      const response = await fetch(`/api/profile/check-username/${username}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      const data = await response.json();
      setUsernameAvailable(data.available);
    } catch (error) {
      console.error('Error checking username:', error);
      setUsernameAvailable(null);
    }
    setUsernameChecking(false);
  };

  const validateForm = () => {
    const newErrors = {};

    if (!profile.display_name.trim()) {
      newErrors.display_name = 'Display name is required';
    }

    if (profile.username) {
      if (profile.username.length < 3 || profile.username.length > 20) {
        newErrors.username = 'Username must be 3-20 characters';
      } else if (!/^[a-zA-Z0-9_]+$/.test(profile.username)) {
        newErrors.username = 'Username can only contain letters, numbers, and underscores';
      } else if (usernameAvailable === false) {
        newErrors.username = 'Username is already taken';
      }
    }

    if (profile.phone && !/^[\+]?[1-9][\d]{0,15}$/.test(profile.phone.replace(/[\s\-\(\)]/g, ''))) {
      newErrors.phone = 'Invalid phone number format';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleAvatarUpload = async (file) => {
    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg'];
    if (!allowedTypes.includes(file.type)) {
      setErrors({ avatar: 'Please select a valid image file (JPEG, PNG, WebP)' });
      return;
    }

    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      setErrors({ avatar: 'File size must be less than 5MB' });
      return;
    }

    setIsUploading(true);
    setErrors({});

    try {
      // Get signed URL for upload
      const uploadResponse = await fetch(`/api/profile/avatar/upload-url?filename=${file.name}&content_type=${file.type}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!uploadResponse.ok) {
        throw new Error('Failed to get upload URL');
      }

      const uploadData = await uploadResponse.json();

      // Upload file to GCS
      const uploadResult = await fetch(uploadData.signed_url, {
        method: 'PUT',
        body: file,
        headers: {
          'Content-Type': file.type
        }
      });

      if (!uploadResult.ok) {
        throw new Error('Failed to upload file');
      }

      // Update profile with new avatar URL
      const updateResponse = await fetch('/api/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          avatar_url: uploadData.public_url
        })
      });

      if (updateResponse.ok) {
        setProfile(prev => ({ ...prev, avatar_url: uploadData.public_url }));
        if (onProfileUpdate) {
          onProfileUpdate({ avatar_url: uploadData.public_url });
        }
      } else {
        throw new Error('Failed to update profile');
      }
    } catch (error) {
      console.error('Error uploading avatar:', error);
      setErrors({ avatar: 'Failed to upload avatar. Please try again.' });
    }

    setIsUploading(false);
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      handleAvatarUpload(file);
    }
  };

  const handleAvatarClick = () => {
    fileInputRef.current?.click();
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    setErrors({});

    try {
      const response = await fetch('/api/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          display_name: profile.display_name,
          username: profile.username || null,
          phone: profile.phone || null,
          address_line_1: profile.address_line_1 || null,
          address_line_2: profile.address_line_2 || null,
          city: profile.city || null,
          province_state: profile.province_state || null,
          postal_zip: profile.postal_zip || null,
          country: profile.country || null
        })
      });

      if (response.ok) {
        const updatedProfile = await response.json();
        if (onProfileUpdate) {
          onProfileUpdate(updatedProfile);
        }
        onClose();
      } else {
        const errorData = await response.json();
        setErrors({ submit: errorData.detail || 'Failed to update profile' });
      }
    } catch (error) {
      console.error('Error updating profile:', error);
      setErrors({ submit: 'Network error. Please try again.' });
    }

    setIsLoading(false);
  };

  const getInitials = (name) => {
    if (!name) return 'U';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2>My Profile</h2>
          <button className="close-btn" onClick={onClose} aria-label="Close">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="profile-form">
          {/* Avatar Section */}
          <div className="avatar-section">
            <div className="avatar-container">
              <div className="avatar-large" onClick={handleAvatarClick}>
                {profile.avatar_url ? (
                  <img src={profile.avatar_url} alt={profile.display_name} />
                ) : (
                  <div className="avatar-initials-large">
                    {getInitials(profile.display_name)}
                  </div>
                )}
                <div className="avatar-overlay">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M17 8L12 3L7 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M12 3V15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp,image/jpg"
                onChange={handleFileSelect}
                style={{ display: 'none' }}
              />
            </div>
            {isUploading && <div className="upload-status">Uploading...</div>}
            {errors.avatar && <div className="error-message">{errors.avatar}</div>}
          </div>

          {/* Form Fields */}
          <div className="form-fields">
            <div className="form-group">
              <label htmlFor="display_name">Display Name *</label>
              <input
                id="display_name"
                type="text"
                value={profile.display_name}
                onChange={(e) => handleInputChange('display_name', e.target.value)}
                className={errors.display_name ? 'error' : ''}
                placeholder="Enter your display name"
              />
              {errors.display_name && <div className="error-message">{errors.display_name}</div>}
            </div>

            <div className="form-group">
              <label htmlFor="username">Username</label>
              <div className="username-input-container">
                <input
                  id="username"
                  type="text"
                  value={profile.username}
                  onChange={(e) => handleInputChange('username', e.target.value)}
                  className={errors.username ? 'error' : ''}
                  placeholder="Choose a username (optional)"
                  maxLength="20"
                />
                {usernameChecking && <div className="username-status checking">Checking...</div>}
                {!usernameChecking && usernameAvailable === true && profile.username && (
                  <div className="username-status available">✓ Available</div>
                )}
                {!usernameChecking && usernameAvailable === false && (
                  <div className="username-status taken">✗ Taken</div>
                )}
              </div>
              {errors.username && <div className="error-message">{errors.username}</div>}
            </div>

            <div className="form-group">
              <label htmlFor="phone">Phone Number</label>
              <input
                id="phone"
                type="tel"
                value={profile.phone}
                onChange={(e) => handleInputChange('phone', e.target.value)}
                className={errors.phone ? 'error' : ''}
                placeholder="Enter your phone number"
              />
              {errors.phone && <div className="error-message">{errors.phone}</div>}
            </div>

            <div className="address-section">
              <h3>Address Information</h3>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="address_line_1">Address Line 1</label>
                  <input
                    id="address_line_1"
                    type="text"
                    value={profile.address_line_1}
                    onChange={(e) => handleInputChange('address_line_1', e.target.value)}
                    placeholder="Street address"
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="address_line_2">Address Line 2</label>
                  <input
                    id="address_line_2"
                    type="text"
                    value={profile.address_line_2}
                    onChange={(e) => handleInputChange('address_line_2', e.target.value)}
                    placeholder="Apartment, suite, etc."
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="city">City</label>
                  <input
                    id="city"
                    type="text"
                    value={profile.city}
                    onChange={(e) => handleInputChange('city', e.target.value)}
                    placeholder="City"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="province_state">Province/State</label>
                  <input
                    id="province_state"
                    type="text"
                    value={profile.province_state}
                    onChange={(e) => handleInputChange('province_state', e.target.value)}
                    placeholder="Province or State"
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="postal_zip">Postal/Zip Code</label>
                  <input
                    id="postal_zip"
                    type="text"
                    value={profile.postal_zip}
                    onChange={(e) => handleInputChange('postal_zip', e.target.value)}
                    placeholder="Postal or Zip code"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="country">Country</label>
                  <input
                    id="country"
                    type="text"
                    value={profile.country}
                    onChange={(e) => handleInputChange('country', e.target.value)}
                    placeholder="Country"
                  />
                </div>
              </div>
            </div>
          </div>

          {errors.submit && <div className="error-message submit-error">{errors.submit}</div>}

          {/* Modal Actions */}
          <div className="modal-actions">
            <button type="button" className="cancel-btn" onClick={onClose} disabled={isLoading}>
              Cancel
            </button>
            <button type="submit" className="save-btn" disabled={isLoading || isUploading}>
              {isLoading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditProfileModal;