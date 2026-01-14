import { Component, Input, Output, EventEmitter, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Subscription } from 'rxjs';

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

@Component({
  selector: 'app-edit-profile-modal',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="modal-backdrop" (click)="close()" *ngIf="isVisible">
      <div class="modal-content" (click)="$event.stopPropagation()">
        <!-- Header -->
        <div class="modal-header">
          <h2>Edit profile</h2>
          <button class="close-btn" (click)="close()">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        <!-- Avatar Section -->
        <div class="avatar-section">
          <div class="avatar-upload">
            <div class="avatar-preview" (click)="triggerFileInput()">
              <img *ngIf="avatarPreview || profile?.avatar_url" [src]="avatarPreview || profile?.avatar_url" alt="Avatar" />
              <div *ngIf="!avatarPreview && !profile?.avatar_url" class="avatar-placeholder">
                {{ getInitials() }}
              </div>
              <div class="camera-overlay">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
                  <circle cx="12" cy="13" r="4"></circle>
                </svg>
              </div>
            </div>
            <input
              #fileInput
              type="file"
              accept="image/jpeg,image/jpg,image/png,image/webp"
              (change)="onFileSelected($event)"
              style="display: none;"
            />
          </div>
          <div class="avatar-actions">
            <button
              class="upload-btn"
              (click)="triggerFileInput()"
              [disabled]="isUploading"
            >
              {{ isUploading ? 'Uploading...' : 'Upload photo' }}
            </button>
            <button
              class="remove-btn"
              (click)="removeAvatar()"
              *ngIf="profile?.avatar_url && !isUploading"
            >
              Remove
            </button>
          </div>
        </div>

        <!-- Form -->
        <form class="profile-form" (ngSubmit)="onSubmit()" #profileForm="ngForm">
          <!-- Display Name -->
          <div class="form-group">
            <label for="displayName">Display name</label>
            <input
              id="displayName"
              type="text"
              [(ngModel)]="formData.display_name"
              name="display_name"
              placeholder="Enter your display name"
              maxlength="255"
              #displayNameInput="ngModel"
            />
          </div>

          <!-- Username -->
          <div class="form-group">
            <label for="username">Username</label>
            <div class="username-input">
              <span class="username-prefix">@</span>
              <input
                id="username"
                type="text"
                [(ngModel)]="formData.username"
                name="username"
                placeholder="username"
                pattern="^[a-zA-Z0-9_]{3,20}$"
                maxlength="20"
                #usernameInput="ngModel"
                [class.error]="usernameInput.invalid && usernameInput.touched"
              />
            </div>
            <div class="form-help">
              Usernames can only contain letters, numbers, and underscores (3-20 characters).
            </div>
            <div class="form-error" *ngIf="usernameInput.invalid && usernameInput.touched">
              <span *ngIf="usernameInput.errors?.['pattern']">Invalid username format</span>
              <span *ngIf="usernameInput.errors?.['required']">Username is required</span>
            </div>
            <div class="form-error" *ngIf="usernameTaken">
              Username is already taken
            </div>
          </div>

          <!-- Email (Read-only) -->
          <div class="form-group">
            <label for="email">Email</label>
            <input
              id="email"
              type="email"
              [value]="user?.email"
              readonly
              class="readonly"
            />
            <div class="form-help">
              Email cannot be changed. Contact support if you need to update it.
            </div>
          </div>

          <!-- Phone -->
          <div class="form-group">
            <label for="phone">Phone (optional)</label>
            <input
              id="phone"
              type="tel"
              [(ngModel)]="formData.phone"
              name="phone"
              placeholder="Enter your phone number"
              maxlength="50"
            />
          </div>

          <!-- Address Section -->
          <div class="address-section">
            <h3>Address (optional)</h3>

            <div class="form-row">
              <div class="form-group half">
                <label for="addressLine1">Address line 1</label>
                <input
                  id="addressLine1"
                  type="text"
                  [(ngModel)]="formData.address_line_1"
                  name="address_line_1"
                  placeholder="Street address"
                  maxlength="255"
                />
              </div>
              <div class="form-group half">
                <label for="addressLine2">Address line 2</label>
                <input
                  id="addressLine2"
                  type="text"
                  [(ngModel)]="formData.address_line_2"
                  name="address_line_2"
                  placeholder="Apartment, suite, etc."
                  maxlength="255"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group third">
                <label for="city">City</label>
                <input
                  id="city"
                  type="text"
                  [(ngModel)]="formData.city"
                  name="city"
                  placeholder="City"
                  maxlength="100"
                />
              </div>
              <div class="form-group third">
                <label for="province">Province/State</label>
                <input
                  id="province"
                  type="text"
                  [(ngModel)]="formData.province_state"
                  name="province_state"
                  placeholder="Province or State"
                  maxlength="100"
                />
              </div>
              <div class="form-group third">
                <label for="postal">Postal/Zip</label>
                <input
                  id="postal"
                  type="text"
                  [(ngModel)]="formData.postal_zip"
                  name="postal_zip"
                  placeholder="Postal or ZIP code"
                  maxlength="20"
                />
              </div>
            </div>

            <div class="form-group">
              <label for="country">Country</label>
              <select
                id="country"
                [(ngModel)]="formData.country"
                name="country"
              >
                <option value="">Select country</option>
                <option value="Canada">Canada</option>
                <option value="United States">United States</option>
              </select>
            </div>
          </div>

          <!-- Actions -->
          <div class="form-actions">
            <button
              type="button"
              class="cancel-btn"
              (click)="close()"
              [disabled]="isSaving"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="save-btn"
              [disabled]="profileForm.invalid || isSaving || usernameTaken"
            >
              {{ isSaving ? 'Saving...' : 'Save' }}
            </button>
          </div>
        </form>

        <!-- Status Messages -->
        <div class="status-message" *ngIf="saveError">
          <div class="error-message">
            {{ saveError }}
          </div>
        </div>

        <div class="status-message" *ngIf="saveSuccess">
          <div class="success-message">
            Profile updated successfully!
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .modal-backdrop {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.75);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 2000;
      animation: fadeIn 0.2s ease-out;
    }

    .modal-content {
      background: #2d2d2d;
      border-radius: 12px;
      width: 90%;
      max-width: 500px;
      max-height: 90vh;
      overflow-y: auto;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
      animation: slideIn 0.2s ease-out;
    }

    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }

    @keyframes slideIn {
      from { opacity: 0; transform: translateY(-20px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .modal-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 1.5rem 2rem 1rem;
      border-bottom: 1px solid #404040;
    }

    .modal-header h2 {
      margin: 0;
      font-size: 1.25rem;
      font-weight: 600;
      color: #ececec;
    }

    .close-btn {
      background: none;
      border: none;
      color: #9ca3af;
      cursor: pointer;
      padding: 0.5rem;
      border-radius: 6px;
      transition: all 0.15s ease;
    }

    .close-btn:hover {
      background: rgba(255, 255, 255, 0.1);
      color: #ececec;
    }

    .avatar-section {
      padding: 2rem;
      text-align: center;
      border-bottom: 1px solid #404040;
    }

    .avatar-upload {
      margin-bottom: 1rem;
    }

    .avatar-preview {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      margin: 0 auto 1rem;
      position: relative;
      cursor: pointer;
      border: 3px solid #404040;
      overflow: hidden;
      transition: border-color 0.15s ease;
    }

    .avatar-preview:hover {
      border-color: #00bcd4;
    }

    .avatar-preview img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    .avatar-placeholder {
      width: 100%;
      height: 100%;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-weight: 600;
      font-size: 1.5rem;
    }

    .camera-overlay {
      position: absolute;
      bottom: -5px;
      right: -5px;
      width: 28px;
      height: 28px;
      background: #00bcd4;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 3px solid #2d2d2d;
      opacity: 0.9;
    }

    .avatar-actions {
      display: flex;
      gap: 0.5rem;
      justify-content: center;
    }

    .upload-btn, .remove-btn {
      padding: 0.5rem 1rem;
      border-radius: 6px;
      border: none;
      font-size: 0.875rem;
      cursor: pointer;
      transition: all 0.15s ease;
    }

    .upload-btn {
      background: #00bcd4;
      color: white;
    }

    .upload-btn:hover:not(:disabled) {
      background: #0097a7;
    }

    .remove-btn {
      background: #ef4444;
      color: white;
    }

    .remove-btn:hover {
      background: #dc2626;
    }

    .upload-btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .profile-form {
      padding: 2rem;
    }

    .form-group {
      margin-bottom: 1.5rem;
    }

    .form-group label {
      display: block;
      margin-bottom: 0.5rem;
      font-size: 0.875rem;
      font-weight: 500;
      color: #ececec;
    }

    .form-group input,
    .form-group select {
      width: 100%;
      padding: 0.75rem;
      background: #1f1f1f;
      border: 2px solid #404040;
      border-radius: 8px;
      color: #ececec;
      font-size: 1rem;
      transition: border-color 0.15s ease;
    }

    .form-group input:focus,
    .form-group select:focus {
      outline: none;
      border-color: #00bcd4;
      box-shadow: 0 0 0 3px rgba(0, 188, 212, 0.1);
    }

    .form-group input.readonly {
      background: #262626;
      cursor: not-allowed;
      opacity: 0.7;
    }

    .form-group input.error {
      border-color: #ef4444;
    }

    .username-input {
      position: relative;
    }

    .username-prefix {
      position: absolute;
      left: 0.75rem;
      top: 50%;
      transform: translateY(-50%);
      color: #9ca3af;
      font-weight: 500;
      z-index: 1;
    }

    .username-input input {
      padding-left: 2rem;
    }

    .form-help {
      margin-top: 0.25rem;
      font-size: 0.75rem;
      color: #9ca3af;
    }

    .form-error {
      margin-top: 0.25rem;
      font-size: 0.75rem;
      color: #ef4444;
    }

    .address-section {
      margin-top: 2rem;
      padding-top: 2rem;
      border-top: 1px solid #404040;
    }

    .address-section h3 {
      margin: 0 0 1.5rem 0;
      font-size: 1rem;
      font-weight: 600;
      color: #ececec;
    }

    .form-row {
      display: flex;
      gap: 1rem;
      margin-bottom: 1rem;
    }

    .form-group.half {
      flex: 1;
    }

    .form-group.third {
      flex: 1;
    }

    .form-actions {
      display: flex;
      gap: 1rem;
      justify-content: flex-end;
      margin-top: 2rem;
      padding-top: 1.5rem;
      border-top: 1px solid #404040;
    }

    .cancel-btn, .save-btn {
      padding: 0.75rem 1.5rem;
      border-radius: 8px;
      border: none;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.15s ease;
    }

    .cancel-btn {
      background: #4b5563;
      color: #ececec;
    }

    .cancel-btn:hover:not(:disabled) {
      background: #374151;
    }

    .save-btn {
      background: #00bcd4;
      color: white;
    }

    .save-btn:hover:not(:disabled) {
      background: #0097a7;
    }

    .save-btn:disabled,
    .cancel-btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .status-message {
      margin: 0 2rem 2rem;
    }

    .error-message {
      background: #fef2f2;
      color: #991b1b;
      padding: 0.75rem;
      border-radius: 6px;
      border: 1px solid #fecaca;
      font-size: 0.875rem;
    }

    .success-message {
      background: #f0fdf4;
      color: #166534;
      padding: 0.75rem;
      border-radius: 6px;
      border: 1px solid #bbf7d0;
      font-size: 0.875rem;
    }

    /* Mobile adjustments */
    @media (max-width: 768px) {
      .modal-content {
        width: 95%;
        margin: 1rem;
      }

      .modal-header {
        padding: 1rem 1.5rem 0.75rem;
      }

      .avatar-section {
        padding: 1.5rem;
      }

      .profile-form {
        padding: 1.5rem;
      }

      .form-row {
        flex-direction: column;
        gap: 0;
      }

      .form-group.half,
      .form-group.third {
        margin-bottom: 1rem;
      }

      .form-actions {
        flex-direction: column-reverse;
      }

      .cancel-btn, .save-btn {
        width: 100%;
      }
    }
  `]
})
export class EditProfileModalComponent implements OnInit, OnDestroy {
  @Input() isVisible = false;
  @Input() user: User | null = null;
  @Input() profile: UserProfile | null = null;
  @Output() closeRequested = new EventEmitter<void>();
  @Output() profileUpdated = new EventEmitter<UserProfile>();

  formData: any = {};
  avatarPreview: string | null = null;
  selectedFile: File | null = null;
  isUploading = false;
  isSaving = false;
  saveError = '';
  saveSuccess = false;
  usernameTaken = false;

  private subscriptions: Subscription[] = [];

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loadProfileData();
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach(sub => sub.unsubscribe());
  }

  loadProfileData(): void {
    if (this.profile) {
      this.formData = { ...this.profile };
    } else {
      this.formData = {
        display_name: this.user?.name || '',
        username: '',
        phone: '',
        address_line_1: '',
        address_line_2: '',
        city: '',
        province_state: '',
        postal_zip: '',
        country: ''
      };
    }
  }

  getInitials(): string {
    const name = this.formData.display_name || this.user?.name || this.user?.email || '';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) || 'U';
  }

  triggerFileInput(): void {
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    if (fileInput) {
      fileInput.click();
    }
  }

  onFileSelected(event: Event): void {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (file) {
      this.selectedFile = file;

      // Validate file size (5MB)
      if (file.size > 5 * 1024 * 1024) {
        this.saveError = 'File size must be less than 5MB';
        return;
      }

      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        this.avatarPreview = e.target?.result as string;
      };
      reader.readAsDataURL(file);

      // Upload immediately
      this.uploadAvatar();
    }
  }

  async uploadAvatar(): Promise<void> {
    if (!this.selectedFile) return;

    this.isUploading = true;
    this.saveError = '';

    try {
      // Get signed URL
      const signedUrlResponse = await this.http.post<{
        signed_url: string;
        file_path: string;
        public_url: string;
      }>('/api/avatar/upload-url', {
        filename: this.selectedFile.name,
        content_type: this.selectedFile.type
      }).toPromise();

      if (!signedUrlResponse) {
        throw new Error('Failed to get upload URL');
      }

      // Upload to GCS
      const uploadResponse = await fetch(signedUrlResponse.signed_url, {
        method: 'PUT',
        body: this.selectedFile,
        headers: {
          'Content-Type': this.selectedFile.type
        }
      });

      if (!uploadResponse.ok) {
        throw new Error('Upload failed');
      }

      // Update profile with new avatar URL
      await this.http.put('/api/profile/avatar', {
        avatar_url: signedUrlResponse.public_url
      }).toPromise();

      // Update local profile
      if (this.profile) {
        this.profile.avatar_url = signedUrlResponse.public_url;
      }

      this.isUploading = false;
      this.selectedFile = null;

    } catch (error: any) {
      this.saveError = error.message || 'Upload failed';
      this.isUploading = false;
      this.avatarPreview = null;
      this.selectedFile = null;
    }
  }

  removeAvatar(): void {
    this.avatarPreview = null;
    this.selectedFile = null;
    if (this.profile) {
      this.profile.avatar_url = '';
      // You would call the API to remove the avatar here
    }
  }

  async onSubmit(): Promise<void> {
    if (this.isSaving) return;

    this.isSaving = true;
    this.saveError = '';
    this.saveSuccess = false;
    this.usernameTaken = false;

    try {
      const response = await this.http.put<UserProfile>('/api/profile', this.formData).toPromise();

      if (response) {
        this.saveSuccess = true;
        this.profileUpdated.emit(response);

        // Close modal after a delay
        setTimeout(() => {
          this.close();
        }, 1500);
      }
    } catch (error: any) {
      if (error.status === 400 && error.error?.detail?.includes('username')) {
        this.usernameTaken = true;
      } else {
        this.saveError = error.error?.detail || 'Failed to save profile';
      }
    } finally {
      this.isSaving = false;
    }
  }

  close(): void {
    this.isVisible = false;
    this.saveError = '';
    this.saveSuccess = false;
    this.usernameTaken = false;
    this.avatarPreview = null;
    this.selectedFile = null;
    this.closeRequested.emit();
  }
}