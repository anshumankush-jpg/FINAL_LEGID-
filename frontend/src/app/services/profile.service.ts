import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { BehaviorSubject, Observable, throwError } from 'rxjs';
import { tap, catchError, map } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface UserProfile {
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
  preferences_json?: UserPreferences;
  updated_at?: string;
}

export interface UserPreferences {
  theme?: 'dark' | 'light' | 'system';
  font_size?: 'small' | 'medium' | 'large';
  response_style?: 'concise' | 'balanced' | 'detailed';
  legal_tone?: 'neutral' | 'firm' | 'very_formal';
  auto_read?: boolean;
  auto_read_responses?: boolean; // Preferred name
  language?: string;
}

export interface User {
  id: string;
  email: string;
  name?: string;
  role: 'client' | 'lawyer' | 'employee' | 'employee_admin';
  lawyer_status: 'not_applicable' | 'pending' | 'approved' | 'rejected';
  is_provisioned?: boolean;
  created_at?: string;
  last_login_at?: string;
}

export interface UserConsent {
  necessary: boolean;
  analytics: boolean;
  marketing: boolean;
  functional: boolean;
  updated_at?: string;
}

export interface FullUserData {
  user: User;
  profile: UserProfile;
  consent: UserConsent;
}

export interface AvatarUploadResponse {
  signed_url: string;
  file_path: string;
  public_url: string;
}

@Injectable({
  providedIn: 'root'
})
export class ProfileService {
  private apiUrl = environment.apiUrl || 'http://localhost:8000';
  
  // State management
  private profileSubject = new BehaviorSubject<UserProfile | null>(null);
  private userSubject = new BehaviorSubject<User | null>(null);
  private consentSubject = new BehaviorSubject<UserConsent | null>(null);
  private loadingSubject = new BehaviorSubject<boolean>(false);
  
  // Public observables
  public profile$ = this.profileSubject.asObservable();
  public user$ = this.userSubject.asObservable();
  public consent$ = this.consentSubject.asObservable();
  public loading$ = this.loadingSubject.asObservable();

  constructor(private http: HttpClient) {}

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('authToken');
    return new HttpHeaders({
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    });
  }

  /**
   * Load full user data (user + profile + consent)
   */
  loadFullUserData(): Observable<FullUserData> {
    this.loadingSubject.next(true);
    
    return this.http.get<FullUserData>(`${this.apiUrl}/api/profile`, {
      headers: this.getHeaders()
    }).pipe(
      tap(data => {
        this.userSubject.next(data.user);
        this.profileSubject.next(data.profile);
        this.consentSubject.next(data.consent);
        this.loadingSubject.next(false);
      }),
      catchError(error => {
        this.loadingSubject.next(false);
        console.error('Failed to load user data:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Get current profile
   */
  getProfile(): Observable<UserProfile> {
    return this.http.get<any>(`${this.apiUrl}/api/profile`, {
      headers: this.getHeaders()
    }).pipe(
      map(response => response.profile || response),
      tap(profile => this.profileSubject.next(profile)),
      catchError(error => {
        console.error('Failed to get profile:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Update profile
   */
  updateProfile(updates: Partial<UserProfile>): Observable<UserProfile> {
    return this.http.put<any>(`${this.apiUrl}/api/profile`, updates, {
      headers: this.getHeaders()
    }).pipe(
      map(response => response.profile || response),
      tap(profile => {
        const current = this.profileSubject.value;
        this.profileSubject.next({ ...current, ...profile });
      }),
      catchError(error => {
        console.error('Failed to update profile:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Update preferences
   */
  updatePreferences(preferences: Partial<UserPreferences>): Observable<UserPreferences> {
    return this.http.put<any>(`${this.apiUrl}/api/profile/preferences`, preferences, {
      headers: this.getHeaders()
    }).pipe(
      map(response => response.preferences),
      tap(prefs => {
        const current = this.profileSubject.value;
        if (current) {
          this.profileSubject.next({
            ...current,
            preferences_json: { ...current.preferences_json, ...prefs }
          });
        }
      }),
      catchError(error => {
        console.error('Failed to update preferences:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Check username availability
   */
  checkUsernameAvailable(username: string): Observable<boolean> {
    return this.http.get<{ available: boolean }>(`${this.apiUrl}/api/profile/check-username/${username}`, {
      headers: this.getHeaders()
    }).pipe(
      map(response => response.available),
      catchError(error => {
        console.error('Failed to check username:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Get signed URL for avatar upload
   */
  getAvatarUploadUrl(filename: string, contentType: string): Observable<AvatarUploadResponse> {
    return this.http.post<AvatarUploadResponse>(`${this.apiUrl}/api/profile/avatar/upload-url`, {
      filename,
      content_type: contentType
    }, {
      headers: this.getHeaders()
    }).pipe(
      catchError(error => {
        console.error('Failed to get upload URL:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Upload avatar to signed URL
   */
  async uploadAvatarToSignedUrl(signedUrl: string, file: File): Promise<void> {
    const response = await fetch(signedUrl, {
      method: 'PUT',
      body: file,
      headers: {
        'Content-Type': file.type
      }
    });

    if (!response.ok) {
      throw new Error('Failed to upload avatar');
    }
  }

  /**
   * Update avatar URL after upload
   */
  updateAvatarUrl(avatarUrl: string): Observable<UserProfile> {
    return this.updateProfile({ avatar_url: avatarUrl });
  }

  /**
   * Remove avatar
   */
  removeAvatar(): Observable<UserProfile> {
    return this.updateProfile({ avatar_url: '' });
  }

  /**
   * Get consent settings
   */
  getConsent(): Observable<UserConsent> {
    return this.http.get<UserConsent>(`${this.apiUrl}/api/profile/consent`, {
      headers: this.getHeaders()
    }).pipe(
      tap(consent => this.consentSubject.next(consent)),
      catchError(error => {
        console.error('Failed to get consent:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Update consent settings
   */
  updateConsent(consent: Partial<UserConsent>): Observable<UserConsent> {
    return this.http.put<any>(`${this.apiUrl}/api/profile/consent`, consent, {
      headers: this.getHeaders()
    }).pipe(
      map(response => response.consent || response),
      tap(updated => {
        const current = this.consentSubject.value;
        this.consentSubject.next({ ...current, ...updated });
      }),
      catchError(error => {
        console.error('Failed to update consent:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Get current values synchronously
   */
  getCurrentProfile(): UserProfile | null {
    return this.profileSubject.value;
  }

  getCurrentUser(): User | null {
    return this.userSubject.value;
  }

  getCurrentConsent(): UserConsent | null {
    return this.consentSubject.value;
  }

  /**
   * Clear all state (on logout)
   */
  clearState(): void {
    this.profileSubject.next(null);
    this.userSubject.next(null);
    this.consentSubject.next(null);
  }
}

import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject, of } from 'rxjs';
import { tap, catchError, map } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface User {
  id: string;
  email: string;
  name?: string;
  role: 'client' | 'lawyer' | 'employee' | 'employee_admin';
  lawyer_status: 'not_applicable' | 'pending' | 'approved' | 'rejected';
  is_provisioned: boolean;
  created_at: string;
  last_login_at?: string;
}

export interface UserProfile {
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
  preferences_json?: UserPreferences;
  updated_at: string;
}

export interface UserPreferences {
  theme?: 'dark' | 'light';
  font_size?: 'small' | 'medium' | 'large';
  response_style?: 'concise' | 'balanced' | 'detailed';
  legal_tone?: 'neutral' | 'firm' | 'very_formal';
}

export interface UserConsent {
  user_id: string;
  necessary: boolean;
  analytics: boolean;
  marketing: boolean;
  updated_at: string;
}

export interface SignedUrlResponse {
  signed_url: string;
  file_path: string;
  public_url: string;
}

export interface AccessRequest {
  id: string;
  email: string;
  name: string;
  requested_role: string;
  reason?: string;
  organization?: string;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class ProfileService {
  private apiUrl = environment.apiUrl || 'http://localhost:8001';
  
  private userSubject = new BehaviorSubject<User | null>(null);
  private profileSubject = new BehaviorSubject<UserProfile | null>(null);
  private consentSubject = new BehaviorSubject<UserConsent | null>(null);
  
  public user$ = this.userSubject.asObservable();
  public profile$ = this.profileSubject.asObservable();
  public consent$ = this.consentSubject.asObservable();

  constructor(private http: HttpClient) {
    // Load cached data on init
    this.loadCachedData();
  }

  private loadCachedData(): void {
    const cachedUser = localStorage.getItem('legalai_user');
    const cachedProfile = localStorage.getItem('legalai_profile');
    
    if (cachedUser) {
      try {
        this.userSubject.next(JSON.parse(cachedUser));
      } catch (e) {
        localStorage.removeItem('legalai_user');
      }
    }
    
    if (cachedProfile) {
      try {
        this.profileSubject.next(JSON.parse(cachedProfile));
      } catch (e) {
        localStorage.removeItem('legalai_profile');
      }
    }
  }

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('authToken');
    return new HttpHeaders({
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    });
  }

  // ============================================
  // USER & SESSION
  // ============================================

  /**
   * Get current user info from /api/me
   */
  getMe(): Observable<{ user: User; profile: UserProfile }> {
    return this.http.get<{ user: User; profile: UserProfile }>(
      `${this.apiUrl}/api/me`,
      { headers: this.getHeaders() }
    ).pipe(
      tap(response => {
        this.userSubject.next(response.user);
        this.profileSubject.next(response.profile);
        localStorage.setItem('legalai_user', JSON.stringify(response.user));
        localStorage.setItem('legalai_profile', JSON.stringify(response.profile));
      }),
      catchError(error => {
        console.error('Failed to get user info:', error);
        throw error;
      })
    );
  }

  /**
   * Get current user synchronously
   */
  getCurrentUser(): User | null {
    return this.userSubject.getValue();
  }

  /**
   * Get current profile synchronously
   */
  getCurrentProfile(): UserProfile | null {
    return this.profileSubject.getValue();
  }

  // ============================================
  // PROFILE
  // ============================================

  /**
   * Get user profile
   */
  getProfile(): Observable<UserProfile> {
    return this.http.get<UserProfile>(
      `${this.apiUrl}/api/profile`,
      { headers: this.getHeaders() }
    ).pipe(
      tap(profile => {
        this.profileSubject.next(profile);
        localStorage.setItem('legalai_profile', JSON.stringify(profile));
      }),
      catchError(error => {
        console.error('Failed to get profile:', error);
        throw error;
      })
    );
  }

  /**
   * Update user profile
   */
  updateProfile(profileData: Partial<UserProfile>): Observable<UserProfile> {
    return this.http.put<UserProfile>(
      `${this.apiUrl}/api/profile`,
      profileData,
      { headers: this.getHeaders() }
    ).pipe(
      tap(profile => {
        this.profileSubject.next(profile);
        localStorage.setItem('legalai_profile', JSON.stringify(profile));
      }),
      catchError(error => {
        console.error('Failed to update profile:', error);
        throw error;
      })
    );
  }

  /**
   * Check if username is available
   */
  checkUsernameAvailability(username: string): Observable<{ available: boolean }> {
    return this.http.get<{ available: boolean }>(
      `${this.apiUrl}/api/profile/check-username`,
      { 
        headers: this.getHeaders(),
        params: { username }
      }
    ).pipe(
      catchError(error => {
        console.error('Failed to check username:', error);
        return of({ available: false });
      })
    );
  }

  // ============================================
  // AVATAR
  // ============================================

  /**
   * Get signed URL for avatar upload
   */
  getAvatarUploadUrl(filename: string, contentType: string): Observable<SignedUrlResponse> {
    const formData = new FormData();
    formData.append('filename', filename);
    formData.append('content_type', contentType);

    const token = localStorage.getItem('authToken');
    const headers = new HttpHeaders({
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    });

    return this.http.post<SignedUrlResponse>(
      `${this.apiUrl}/api/avatar/upload-url`,
      formData,
      { headers }
    );
  }

  /**
   * Upload avatar to signed URL
   */
  async uploadAvatar(file: File): Promise<string> {
    // Get signed URL
    const signedUrlResponse = await this.getAvatarUploadUrl(
      file.name,
      file.type
    ).toPromise();

    if (!signedUrlResponse) {
      throw new Error('Failed to get upload URL');
    }

    // Upload to GCS
    const uploadResponse = await fetch(signedUrlResponse.signed_url, {
      method: 'PUT',
      body: file,
      headers: {
        'Content-Type': file.type
      }
    });

    if (!uploadResponse.ok) {
      throw new Error('Upload failed');
    }

    // Update profile with new avatar URL
    await this.updateAvatarUrl(signedUrlResponse.public_url).toPromise();

    return signedUrlResponse.public_url;
  }

  /**
   * Update avatar URL in profile
   */
  updateAvatarUrl(avatarUrl: string): Observable<UserProfile> {
    return this.http.put<UserProfile>(
      `${this.apiUrl}/api/profile/avatar`,
      { avatar_url: avatarUrl },
      { headers: this.getHeaders() }
    ).pipe(
      tap(profile => {
        this.profileSubject.next(profile);
        localStorage.setItem('legalai_profile', JSON.stringify(profile));
      })
    );
  }

  /**
   * Remove avatar
   */
  removeAvatar(): Observable<UserProfile> {
    return this.updateProfile({ avatar_url: '' });
  }

  // ============================================
  // CONSENT
  // ============================================

  /**
   * Get user consent settings
   */
  getConsent(): Observable<UserConsent> {
    return this.http.get<UserConsent>(
      `${this.apiUrl}/api/consent`,
      { headers: this.getHeaders() }
    ).pipe(
      tap(consent => {
        this.consentSubject.next(consent);
      }),
      catchError(error => {
        console.error('Failed to get consent:', error);
        throw error;
      })
    );
  }

  /**
   * Update user consent settings
   */
  updateConsent(consentData: Partial<UserConsent>): Observable<UserConsent> {
    return this.http.put<UserConsent>(
      `${this.apiUrl}/api/consent`,
      consentData,
      { headers: this.getHeaders() }
    ).pipe(
      tap(consent => {
        this.consentSubject.next(consent);
      }),
      catchError(error => {
        console.error('Failed to update consent:', error);
        throw error;
      })
    );
  }

  // ============================================
  // ACCESS REQUEST
  // ============================================

  /**
   * Request access for non-provisioned user
   */
  requestAccess(requestData: {
    name: string;
    requested_role: string;
    reason?: string;
    organization?: string;
  }): Observable<AccessRequest> {
    return this.http.post<AccessRequest>(
      `${this.apiUrl}/api/request-access`,
      requestData,
      { headers: this.getHeaders() }
    );
  }

  // ============================================
  // PREFERENCES
  // ============================================

  /**
   * Update user preferences
   */
  updatePreferences(preferences: UserPreferences): Observable<UserProfile> {
    return this.updateProfile({ preferences_json: preferences });
  }

  /**
   * Get current preferences
   */
  getPreferences(): UserPreferences {
    const profile = this.profileSubject.getValue();
    return profile?.preferences_json || {
      theme: 'dark',
      font_size: 'medium',
      response_style: 'balanced',
      legal_tone: 'neutral',
      auto_read_responses: false
    };
  }

  /**
   * Apply theme preference
   */
  applyTheme(theme: 'dark' | 'light'): void {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('legalai_theme', theme);
  }

  // ============================================
  // HELPERS
  // ============================================

  /**
   * Get user initials for avatar placeholder
   */
  getInitials(user?: User | null, profile?: UserProfile | null): string {
    const u = user || this.userSubject.getValue();
    const p = profile || this.profileSubject.getValue();
    
    const name = p?.display_name || u?.name || u?.email || '';
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2) || 'U';
  }

  /**
   * Get role display label
   */
  getRoleLabel(user?: User | null): string {
    const u = user || this.userSubject.getValue();
    if (!u) return 'User';

    switch (u.role) {
      case 'lawyer':
        return u.lawyer_status === 'approved' ? 'Lawyer' : 'Lawyer (Pending)';
      case 'employee':
      case 'employee_admin':
        return 'Employee';
      case 'client':
      default:
        return 'Client';
    }
  }

  /**
   * Clear all cached data (on logout)
   */
  clearCache(): void {
    this.userSubject.next(null);
    this.profileSubject.next(null);
    this.consentSubject.next(null);
    localStorage.removeItem('legalai_user');
    localStorage.removeItem('legalai_profile');
  }
}
