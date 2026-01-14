import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { Subscription } from 'rxjs';
import { EditProfileModalComponent } from '../../components/edit-profile-modal/edit-profile-modal.component';

interface User {
  id: string;
  email: string;
  name?: string;
  role: string;
  lawyer_status: string;
}

interface UserProfile {
  user_id: string;
  display_name?: string;
  username?: string;
  avatar_url?: string;
  phone?: string;
  address_line_1?: string;
  address_line_2?: string;
  city?: string;
  province_state?: string;
  postal_zip?: string;
  country?: string;
  preferences_json?: any;
  updated_at: string;
}

interface UserConsent {
  user_id: string;
  necessary: boolean;
  analytics: boolean;
  marketing: boolean;
  updated_at: string;
}

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [CommonModule, FormsModule, EditProfileModalComponent],
  template: `
    <div class="settings-page">
      <!-- Header -->
      <div class="page-header">
        <div class="header-content">
          <button class="back-btn" (click)="goBack()">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 12H5"></path>
              <path d="M12 19l-7-7 7-7"></path>
            </svg>
          </button>
          <h1>Settings</h1>
        </div>
      </div>

      <!-- Content -->
      <div class="page-content">
        <!-- Profile Section -->
        <div class="settings-section">
          <div class="section-header">
            <h2>Profile</h2>
            <p>Manage your account information and preferences.</p>
          </div>

          <div class="setting-item">
            <div class="item-content">
              <div class="item-title">Profile Information</div>
              <div class="item-description">Update your name, username, and contact details.</div>
            </div>
            <button class="edit-btn" (click)="openEditProfile()">
              Edit profile
            </button>
          </div>
        </div>

        <!-- Privacy & Cookies Section -->
        <div class="settings-section">
          <div class="section-header">
            <h2>Privacy & Cookies</h2>
            <p>Control how we use your data and manage cookie preferences.</p>
          </div>

          <div class="cookie-settings">
            <div class="cookie-item">
              <div class="cookie-content">
                <div class="cookie-title">Necessary Cookies</div>
                <div class="cookie-description">Required for the website to function properly.</div>
              </div>
              <div class="cookie-status required">
                Always Active
              </div>
            </div>

            <div class="cookie-item">
              <label class="cookie-item">
                <div class="cookie-content">
                  <div class="cookie-title">Analytics Cookies</div>
                  <div class="cookie-description">Help us understand how you use the website.</div>
                </div>
                <div class="toggle-switch">
                  <input
                    type="checkbox"
                    [(ngModel)]="consent.analytics"
                    (change)="updateConsent()"
                    name="analytics"
                  />
                  <span class="toggle-slider"></span>
                </div>
              </label>
            </div>

            <div class="cookie-item">
              <label class="cookie-item">
                <div class="cookie-content">
                  <div class="cookie-title">Marketing Cookies</div>
                  <div class="cookie-description">Used to deliver personalized advertisements.</div>
                </div>
                <div class="toggle-switch">
                  <input
                    type="checkbox"
                    [(ngModel)]="consent.marketing"
                    (change)="updateConsent()"
                    name="marketing"
                  />
                  <span class="toggle-slider"></span>
                </div>
              </label>
            </div>
          </div>

          <div class="cookie-info">
            <p>
              You can change your cookie preferences at any time. Changes will take effect immediately.
            </p>
            <p class="cookie-link">
              Learn more about our
              <a href="/cookies" target="_blank">Cookie Policy</a> and
              <a href="/privacy" target="_blank">Privacy Policy</a>.
            </p>
          </div>
        </div>

        <!-- Account Information Section -->
        <div class="settings-section">
          <div class="section-header">
            <h2>Account Information</h2>
            <p>Your account details and security information.</p>
          </div>

          <div class="account-details">
            <div class="detail-row">
              <span class="detail-label">Email</span>
              <span class="detail-value">{{ user?.email }}</span>
            </div>

            <div class="detail-row">
              <span class="detail-label">Role</span>
              <span class="detail-value">{{ getRoleDisplayName() }}</span>
            </div>

            <div class="detail-row" *ngIf="user?.role === 'lawyer'">
              <span class="detail-label">Lawyer Status</span>
              <span class="detail-value">{{ getLawyerStatusDisplayName() }}</span>
            </div>

            <div class="detail-row">
              <span class="detail-label">Member Since</span>
              <span class="detail-value">{{ profile?.updated_at | date:'mediumDate' || 'N/A' }}</span>
            </div>
          </div>
        </div>

        <!-- Danger Zone -->
        <div class="settings-section danger-zone">
          <div class="section-header">
            <h2>Danger Zone</h2>
            <p>Irreversible actions that affect your account.</p>
          </div>

          <div class="danger-item">
            <div class="danger-content">
              <div class="danger-title">Log out from all devices</div>
              <div class="danger-description">
                This will log you out from all devices where you're currently signed in.
                You'll need to sign in again on each device.
              </div>
            </div>
            <button class="danger-btn" (click)="logoutAllDevices()" [disabled]="isLoggingOut">
              {{ isLoggingOut ? 'Logging out...' : 'Log out everywhere' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Edit Profile Modal -->
      <app-edit-profile-modal
        [isVisible]="showEditProfileModal"
        [user]="user"
        [profile]="profile"
        (closeRequested)="closeEditProfile()"
        (profileUpdated)="onProfileUpdated($event)"
      ></app-edit-profile-modal>

      <!-- Status Messages -->
      <div class="status-message" *ngIf="errorMessage">
        <div class="error-message">
          {{ errorMessage }}
        </div>
      </div>

      <div class="status-message" *ngIf="successMessage">
        <div class="success-message">
          {{ successMessage }}
        </div>
      </div>
    </div>
  `,
  styles: [`
    .settings-page {
      min-height: 100vh;
      background: #212121;
      color: #ececec;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
    }

    .page-header {
      padding: 2rem;
      border-bottom: 1px solid #404040;
    }

    .header-content {
      display: flex;
      align-items: center;
      gap: 1rem;
    }

    .back-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 40px;
      height: 40px;
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid #404040;
      border-radius: 8px;
      color: #9ca3af;
      cursor: pointer;
      transition: all 0.15s ease;
    }

    .back-btn:hover {
      background: rgba(255, 255, 255, 0.15);
      border-color: #00bcd4;
      color: #00bcd4;
    }

    .page-header h1 {
      font-size: 1.5rem;
      font-weight: 600;
      margin: 0;
      color: #ececec;
    }

    .page-content {
      max-width: 800px;
      margin: 0 auto;
      padding: 2rem;
    }

    .settings-section {
      margin-bottom: 2rem;
      padding: 1.5rem;
      background: #2d2d2d;
      border-radius: 12px;
      border: 1px solid #404040;
    }

    .section-header h2 {
      font-size: 1.25rem;
      font-weight: 600;
      color: #ececec;
      margin: 0 0 0.5rem 0;
    }

    .section-header p {
      color: #9ca3af;
      margin: 0;
      font-size: 0.875rem;
      line-height: 1.5;
    }

    .setting-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 1rem 0;
      border-bottom: 1px solid #404040;
    }

    .setting-item:last-child {
      border-bottom: none;
    }

    .item-content {
      flex: 1;
    }

    .item-title {
      font-weight: 500;
      color: #ececec;
      margin-bottom: 0.25rem;
    }

    .item-description {
      color: #9ca3af;
      font-size: 0.875rem;
      line-height: 1.4;
    }

    .edit-btn {
      padding: 0.5rem 1rem;
      background: #00bcd4;
      color: white;
      border: none;
      border-radius: 6px;
      font-size: 0.875rem;
      font-weight: 500;
      cursor: pointer;
      transition: background-color 0.15s ease;
    }

    .edit-btn:hover {
      background: #0097a7;
    }

    .cookie-settings {
      margin-top: 1.5rem;
    }

    .cookie-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 1rem 0;
      border-bottom: 1px solid #404040;
    }

    .cookie-item:last-child {
      border-bottom: none;
    }

    .cookie-item label {
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
      cursor: pointer;
      margin: 0;
    }

    .cookie-content {
      flex: 1;
    }

    .cookie-title {
      font-weight: 500;
      color: #ececec;
      margin-bottom: 0.25rem;
    }

    .cookie-description {
      color: #9ca3af;
      font-size: 0.875rem;
      line-height: 1.4;
    }

    .cookie-status {
      font-size: 0.75rem;
      font-weight: 500;
      padding: 0.25rem 0.75rem;
      border-radius: 12px;
      background: #374151;
      color: #9ca3af;
    }

    .cookie-status.required {
      background: #166534;
      color: #bbf7d0;
    }

    .toggle-switch {
      position: relative;
      display: inline-block;
      width: 44px;
      height: 24px;
      margin-left: 1rem;
    }

    .toggle-switch input {
      opacity: 0;
      width: 0;
      height: 0;
    }

    .toggle-slider {
      position: absolute;
      cursor: pointer;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: #374151;
      transition: 0.2s;
      border-radius: 24px;
    }

    .toggle-slider:before {
      position: absolute;
      content: "";
      height: 18px;
      width: 18px;
      left: 3px;
      bottom: 3px;
      background-color: white;
      transition: 0.2s;
      border-radius: 50%;
    }

    input:checked + .toggle-slider {
      background-color: #00bcd4;
    }

    input:checked + .toggle-slider:before {
      transform: translateX(20px);
    }

    .cookie-info {
      margin-top: 1.5rem;
      padding-top: 1rem;
      border-top: 1px solid #404040;
    }

    .cookie-info p {
      margin: 0 0 0.75rem 0;
      color: #9ca3af;
      font-size: 0.875rem;
      line-height: 1.5;
    }

    .cookie-link {
      margin: 0;
    }

    .cookie-link a {
      color: #00bcd4;
      text-decoration: none;
    }

    .cookie-link a:hover {
      text-decoration: underline;
    }

    .account-details {
      margin-top: 1.5rem;
    }

    .detail-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.75rem 0;
      border-bottom: 1px solid #404040;
    }

    .detail-row:last-child {
      border-bottom: none;
    }

    .detail-label {
      font-weight: 500;
      color: #ececec;
    }

    .detail-value {
      color: #9ca3af;
      font-size: 0.875rem;
    }

    .danger-zone {
      border-color: #dc2626;
      background: rgba(220, 38, 38, 0.05);
    }

    .danger-zone .section-header h2 {
      color: #ef4444;
    }

    .danger-item {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 1rem;
      padding: 1.5rem;
      background: rgba(239, 68, 68, 0.1);
      border: 1px solid #dc2626;
      border-radius: 8px;
      margin-top: 1rem;
    }

    .danger-content {
      flex: 1;
    }

    .danger-title {
      font-weight: 600;
      color: #ef4444;
      margin-bottom: 0.5rem;
    }

    .danger-description {
      color: #9ca3af;
      font-size: 0.875rem;
      line-height: 1.5;
    }

    .danger-btn {
      padding: 0.75rem 1rem;
      background: #dc2626;
      color: white;
      border: none;
      border-radius: 6px;
      font-size: 0.875rem;
      font-weight: 500;
      cursor: pointer;
      transition: background-color 0.15s ease;
      white-space: nowrap;
    }

    .danger-btn:hover:not(:disabled) {
      background: #b91c1c;
    }

    .danger-btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .status-message {
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      max-width: 400px;
      z-index: 1000;
    }

    .error-message {
      background: #fef2f2;
      color: #991b1b;
      padding: 1rem;
      border-radius: 8px;
      border: 1px solid #fecaca;
      font-size: 0.875rem;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    .success-message {
      background: #f0fdf4;
      color: #166534;
      padding: 1rem;
      border-radius: 8px;
      border: 1px solid #bbf7d0;
      font-size: 0.875rem;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    /* Mobile adjustments */
    @media (max-width: 768px) {
      .page-header {
        padding: 1rem;
      }

      .page-content {
        padding: 1rem;
      }

      .settings-section {
        padding: 1rem;
      }

      .setting-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
      }

      .edit-btn {
        align-self: stretch;
        text-align: center;
      }

      .cookie-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.75rem;
      }

      .toggle-switch {
        margin-left: 0;
        align-self: flex-end;
      }

      .detail-row {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.25rem;
      }

      .danger-item {
        flex-direction: column;
        align-items: flex-start;
      }

      .danger-btn {
        align-self: stretch;
        text-align: center;
      }

      .status-message {
        left: 1rem;
        right: 1rem;
        bottom: 1rem;
        max-width: none;
      }
    }
  `]
})
export class SettingsComponent implements OnInit, OnDestroy {
  user: User | null = null;
  profile: UserProfile | null = null;
  consent: UserConsent = {
    user_id: '',
    necessary: true,
    analytics: false,
    marketing: false,
    updated_at: ''
  };

  showEditProfileModal = false;
  isLoggingOut = false;
  errorMessage = '';
  successMessage = '';
  private subscriptions: Subscription[] = [];

  constructor(
    private router: Router,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    this.loadUserData();
    this.loadConsent();
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach(sub => sub.unsubscribe());
  }

  loadUserData(): void {
    // Load user and profile data
    const profileSub = this.http.get<UserProfile>('/api/profile').subscribe({
      next: (profile) => {
        this.profile = profile;
        // Extract user info from profile if needed
        // In a real app, you'd have a separate /api/me endpoint
      },
      error: (error) => {
        console.error('Failed to load profile:', error);
      }
    });

    this.subscriptions.push(profileSub);
  }

  loadConsent(): void {
    const consentSub = this.http.get<UserConsent>('/api/consent').subscribe({
      next: (consent) => {
        this.consent = consent;
      },
      error: (error) => {
        console.error('Failed to load consent:', error);
      }
    });

    this.subscriptions.push(consentSub);
  }

  updateConsent(): void {
    const consentSub = this.http.put<UserConsent>('/api/consent', {
      necessary: this.consent.necessary,
      analytics: this.consent.analytics,
      marketing: this.consent.marketing
    }).subscribe({
      next: (response) => {
        this.consent = response;
        this.showSuccessMessage('Cookie preferences updated');
      },
      error: (error) => {
        this.showErrorMessage('Failed to update cookie preferences');
        console.error('Failed to update consent:', error);
      }
    });

    this.subscriptions.push(consentSub);
  }

  getRoleDisplayName(): string {
    if (!this.user) return 'User';

    switch (this.user.role) {
      case 'client':
        return 'Client';
      case 'lawyer':
        return 'Lawyer';
      case 'employee':
        return 'Employee';
      case 'employee_admin':
        return 'Admin';
      default:
        return 'User';
    }
  }

  getLawyerStatusDisplayName(): string {
    if (!this.user) return '';

    switch (this.user.lawyer_status) {
      case 'approved':
        return 'Verified';
      case 'pending':
        return 'Verification Pending';
      case 'rejected':
        return 'Verification Rejected';
      case 'not_applicable':
        return 'Not Applicable';
      default:
        return '';
    }
  }

  openEditProfile(): void {
    this.showEditProfileModal = true;
  }

  closeEditProfile(): void {
    this.showEditProfileModal = false;
  }

  onProfileUpdated(updatedProfile: UserProfile): void {
    this.profile = updatedProfile;
    this.showSuccessMessage('Profile updated successfully');
  }

  logoutAllDevices(): void {
    if (this.isLoggingOut) return;

    this.isLoggingOut = true;
    this.showErrorMessage('');

    const logoutSub = this.http.post('/api/logout', {}).subscribe({
      next: () => {
        this.isLoggingOut = false;
        // Redirect to login page
        this.router.navigate(['/login']);
      },
      error: (error) => {
        this.isLoggingOut = false;
        this.showErrorMessage('Failed to log out from all devices');
        console.error('Logout error:', error);
      }
    });

    this.subscriptions.push(logoutSub);
  }

  goBack(): void {
    this.router.navigate(['/']);
  }

  private showErrorMessage(message: string): void {
    this.errorMessage = message;
    this.successMessage = '';
    setTimeout(() => {
      this.errorMessage = '';
    }, 5000);
  }

  private showSuccessMessage(message: string): void {
    this.successMessage = message;
    this.errorMessage = '';
    setTimeout(() => {
      this.successMessage = '';
    }, 3000);
  }
}