import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { Subscription } from 'rxjs';

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
  preferences_json?: {
    theme?: 'dark' | 'light';
    font_size?: 'small' | 'medium' | 'large';
    response_style?: 'concise' | 'balanced' | 'detailed';
    legal_tone?: 'neutral' | 'firm' | 'very_formal';
    auto_read_responses?: boolean;
  };
  updated_at: string;
}

@Component({
  selector: 'app-personalization',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="personalization-page">
      <!-- Header -->
      <div class="page-header">
        <div class="header-content">
          <button class="back-btn" (click)="goBack()">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 12H5"></path>
              <path d="M12 19l-7-7 7-7"></path>
            </svg>
          </button>
          <h1>Personalization</h1>
        </div>
        <p class="page-description">
          Customize your experience to match your preferences.
        </p>
      </div>

      <!-- Content -->
      <div class="page-content">
        <!-- Theme Section -->
        <div class="settings-section">
          <h2>Appearance</h2>

          <div class="setting-group">
            <h3>Theme</h3>
            <p class="setting-description">Choose your preferred color scheme.</p>

            <div class="radio-group">
              <label class="radio-option" [class.selected]="preferences.theme === 'dark'">
                <input
                  type="radio"
                  name="theme"
                  value="dark"
                  [(ngModel)]="preferences.theme"
                  (change)="onPreferenceChange()"
                />
                <div class="radio-content">
                  <div class="radio-label">Dark</div>
                  <div class="radio-description">Easy on the eyes in low light</div>
                </div>
              </label>

              <label class="radio-option" [class.selected]="preferences.theme === 'light'">
                <input
                  type="radio"
                  name="theme"
                  value="light"
                  [(ngModel)]="preferences.theme"
                  (change)="onPreferenceChange()"
                />
                <div class="radio-content">
                  <div class="radio-label">Light</div>
                  <div class="radio-description">Classic bright interface</div>
                </div>
              </label>
            </div>
          </div>

          <div class="setting-group">
            <h3>Font Size</h3>
            <p class="setting-description">Adjust the text size for better readability.</p>

            <div class="radio-group">
              <label class="radio-option" [class.selected]="preferences.font_size === 'small'">
                <input
                  type="radio"
                  name="font_size"
                  value="small"
                  [(ngModel)]="preferences.font_size"
                  (change)="onPreferenceChange()"
                />
                <div class="radio-content">
                  <div class="radio-label">Small</div>
                  <div class="radio-description">Compact and space-efficient</div>
                </div>
              </label>

              <label class="radio-option" [class.selected]="preferences.font_size === 'medium'">
                <input
                  type="radio"
                  name="font_size"
                  value="medium"
                  [(ngModel)]="preferences.font_size"
                  (change)="onPreferenceChange()"
                />
                <div class="radio-content">
                  <div class="radio-label">Medium</div>
                  <div class="radio-description">Balanced and comfortable</div>
                </div>
              </label>

              <label class="radio-option" [class.selected]="preferences.font_size === 'large'">
                <input
                  type="radio"
                  name="font_size"
                  value="large"
                  [(ngModel)]="preferences.font_size"
                  (change)="onPreferenceChange()"
                />
                <div class="radio-content">
                  <div class="radio-label">Large</div>
                  <div class="radio-description">Enhanced readability</div>
                </div>
              </label>
            </div>
          </div>
        </div>

        <!-- Response Style Section -->
        <div class="settings-section">
          <h2>Response Style</h2>

          <div class="setting-group">
            <h3>Detail Level</h3>
            <p class="setting-description">Choose how detailed you want AI responses to be.</p>

            <div class="radio-group">
              <label class="radio-option" [class.selected]="preferences.response_style === 'concise'">
                <input
                  type="radio"
                  name="response_style"
                  value="concise"
                  [(ngModel)]="preferences.response_style"
                  (change)="onPreferenceChange()"
                />
                <div class="radio-content">
                  <div class="radio-label">Concise</div>
                  <div class="radio-description">Brief, to-the-point answers</div>
                </div>
              </label>

              <label class="radio-option" [class.selected]="preferences.response_style === 'balanced'">
                <input
                  type="radio"
                  name="response_style"
                  value="balanced"
                  [(ngModel)]="preferences.response_style"
                  (change)="onPreferenceChange()"
                />
                <div class="radio-content">
                  <div class="radio-label">Balanced</div>
                  <div class="radio-description">Comprehensive but not overwhelming</div>
                </div>
              </label>

              <label class="radio-option" [class.selected]="preferences.response_style === 'detailed'">
                <input
                  type="radio"
                  name="response_style"
                  value="detailed"
                  [(ngModel)]="preferences.response_style"
                  (change)="onPreferenceChange()"
                />
                <div class="radio-content">
                  <div class="radio-label">Detailed</div>
                  <div class="radio-description">Thorough explanations with examples</div>
                </div>
              </label>
            </div>
          </div>

          <div class="setting-group">
            <h3>Legal Tone</h3>
            <p class="setting-description">Set the communication style for legal responses.</p>

            <div class="radio-group">
              <label class="radio-option" [class.selected]="preferences.legal_tone === 'neutral'">
                <input
                  type="radio"
                  name="legal_tone"
                  value="neutral"
                  [(ngModel)]="preferences.legal_tone"
                  (change)="onPreferenceChange()"
                />
                <div class="radio-content">
                  <div class="radio-label">Neutral</div>
                  <div class="radio-description">Professional and balanced</div>
                </div>
              </label>

              <label class="radio-option" [class.selected]="preferences.legal_tone === 'firm'">
                <input
                  type="radio"
                  name="legal_tone"
                  value="firm"
                  [(ngModel)]="preferences.legal_tone"
                  (change)="onPreferenceChange()"
                />
                <div class="radio-content">
                  <div class="radio-label">Firm</div>
                  <div class="radio-description">Direct and assertive</div>
                </div>
              </label>

              <label class="radio-option" [class.selected]="preferences.legal_tone === 'very_formal'">
                <input
                  type="radio"
                  name="legal_tone"
                  value="very_formal"
                  [(ngModel)]="preferences.legal_tone"
                  (change)="onPreferenceChange()"
                />
                <div class="radio-content">
                  <div class="radio-label">Very Formal</div>
                  <div class="radio-description">Traditional legal language</div>
                </div>
              </label>
            </div>
          </div>
        </div>

        <!-- Voice Settings Section -->
        <div class="settings-section">
          <h2>Voice & Audio</h2>
          <div class="setting-group">
            <div class="setting-item">
              <div class="setting-content">
                <div class="setting-label">
                  <div class="setting-title">Auto-Read Responses</div>
                  <div class="setting-description">
                    Automatically play audio for AI responses using text-to-speech
                  </div>
                </div>
                <label class="toggle-switch">
                  <input
                    type="checkbox"
                    [(ngModel)]="preferences.auto_read_responses"
                    (change)="onPreferenceChange()"
                  />
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- Preview Section -->
        <div class="settings-section">
          <h2>Preview</h2>
          <div class="preview-notice">
            <div class="preview-icon">💡</div>
            <div class="preview-content">
              <h3>Changes Applied</h3>
              <p>Your preferences will be saved automatically and applied to your experience.</p>
              <p class="preview-note">
                Note: Some visual changes may require refreshing the page to take full effect.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Status Messages -->
      <div class="status-message" *ngIf="saveError">
        <div class="error-message">
          {{ saveError }}
        </div>
      </div>

      <div class="status-message" *ngIf="saveSuccess">
        <div class="success-message">
          Preferences saved successfully!
        </div>
      </div>
    </div>
  `,
  styles: [`
    .personalization-page {
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
      margin-bottom: 0.5rem;
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

    .page-description {
      color: #9ca3af;
      margin: 0;
      font-size: 0.875rem;
    }

    .page-content {
      max-width: 800px;
      margin: 0 auto;
      padding: 2rem;
    }

    .settings-section {
      margin-bottom: 3rem;
    }

    .settings-section h2 {
      font-size: 1.25rem;
      font-weight: 600;
      color: #ececec;
      margin: 0 0 1.5rem 0;
    }

    .setting-group {
      margin-bottom: 2rem;
      padding: 1.5rem;
      background: #2d2d2d;
      border-radius: 12px;
      border: 1px solid #404040;
    }

    .setting-group h3 {
      font-size: 1rem;
      font-weight: 600;
      color: #ececec;
      margin: 0 0 0.5rem 0;
    }

    .setting-description {
      color: #9ca3af;
      font-size: 0.875rem;
      margin: 0 0 1.5rem 0;
      line-height: 1.5;
    }

    .radio-group {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }

    .radio-option {
      display: flex;
      align-items: flex-start;
      gap: 0.75rem;
      padding: 1rem;
      border: 2px solid #404040;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.15s ease;
      background: #1f1f1f;
    }

    .radio-option:hover {
      border-color: #00bcd4;
      background: rgba(0, 188, 212, 0.05);
    }

    .radio-option.selected {
      border-color: #00bcd4;
      background: rgba(0, 188, 212, 0.1);
    }

    .radio-option input[type="radio"] {
      display: none;
    }

    .radio-content {
      flex: 1;
    }

    .radio-label {
      font-weight: 500;
      color: #ececec;
      margin-bottom: 0.25rem;
    }

    .radio-description {
      font-size: 0.875rem;
      color: #9ca3af;
      line-height: 1.4;
    }

    .preview-notice {
      display: flex;
      gap: 1rem;
      padding: 1.5rem;
      background: #2d2d2d;
      border-radius: 12px;
      border: 1px solid #404040;
    }

    .preview-icon {
      font-size: 1.5rem;
      flex-shrink: 0;
    }

    .preview-content h3 {
      margin: 0 0 0.5rem 0;
      font-size: 1rem;
      font-weight: 600;
      color: #ececec;
    }

    .preview-content p {
      margin: 0 0 0.5rem 0;
      color: #9ca3af;
      font-size: 0.875rem;
      line-height: 1.5;
    }

    .preview-note {
      font-style: italic;
      color: #6b7280;
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

      .header-content {
        gap: 0.75rem;
      }

      .page-header h1 {
        font-size: 1.25rem;
      }

      .page-content {
        padding: 1rem;
      }

      .setting-group {
        padding: 1rem;
      }

      .radio-option {
        padding: 0.75rem;
      }

      .preview-notice {
        flex-direction: column;
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
export class PersonalizationComponent implements OnInit, OnDestroy {
  preferences: any = {
    theme: 'dark',
    font_size: 'medium',
    response_style: 'balanced',
    legal_tone: 'neutral',
    auto_read_responses: false
  };

  saveError = '';
  saveSuccess = false;
  private saveTimeout: any;
  private subscriptions: Subscription[] = [];

  constructor(
    private router: Router,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    this.loadPreferences();
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach(sub => sub.unsubscribe());
    if (this.saveTimeout) {
      clearTimeout(this.saveTimeout);
    }
  }

  loadPreferences(): void {
    const sub = this.http.get<UserProfile>('/api/profile').subscribe({
      next: (profile) => {
        if (profile.preferences_json) {
          this.preferences = { ...this.preferences, ...profile.preferences_json };
        }
      },
      error: (error) => {
        console.error('Failed to load preferences:', error);
      }
    });
    this.subscriptions.push(sub);
  }

  onPreferenceChange(): void {
    // Auto-save after a short delay
    if (this.saveTimeout) {
      clearTimeout(this.saveTimeout);
    }

    this.saveTimeout = setTimeout(() => {
      this.savePreferences();
    }, 1000); // 1 second delay
  }

  savePreferences(): void {
    this.saveError = '';
    this.saveSuccess = false;

    const sub = this.http.put<UserProfile>('/api/profile', {
      preferences_json: this.preferences
    }).subscribe({
      next: (response) => {
        this.saveSuccess = true;
        setTimeout(() => {
          this.saveSuccess = false;
        }, 3000);
      },
      error: (error) => {
        this.saveError = error.error?.detail || 'Failed to save preferences';
        setTimeout(() => {
          this.saveError = '';
        }, 5000);
      }
    });
    this.subscriptions.push(sub);
  }

  goBack(): void {
    this.router.navigate(['/']);
  }
}