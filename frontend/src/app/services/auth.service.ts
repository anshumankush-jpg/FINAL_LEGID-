import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject, of, throwError } from 'rxjs';
import { tap, catchError, map, switchMap } from 'rxjs/operators';
import { Router } from '@angular/router';
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
  preferences_json?: any;
  updated_at: string;
}

export interface SessionResponse {
  user: User;
  profile: UserProfile;
  token: string;
  expires_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface OAuthLoginData {
  provider: 'google' | 'microsoft';
  token: string;
  role?: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl || 'http://localhost:8001';
  
  private isAuthenticatedSubject = new BehaviorSubject<boolean>(false);
  private userSubject = new BehaviorSubject<User | null>(null);
  private profileSubject = new BehaviorSubject<UserProfile | null>(null);
  private isProvisionedSubject = new BehaviorSubject<boolean>(true);
  
  public isAuthenticated$ = this.isAuthenticatedSubject.asObservable();
  public user$ = this.userSubject.asObservable();
  public profile$ = this.profileSubject.asObservable();
  public isProvisioned$ = this.isProvisionedSubject.asObservable();

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    this.checkAuthStatus();
  }

  private getHeaders(): HttpHeaders {
    const token = this.getToken();
    return new HttpHeaders({
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    });
  }

  // ============================================
  // SESSION MANAGEMENT
  // ============================================

  /**
   * Create session with email/password
   */
  login(email: string, password: string): Observable<SessionResponse> {
    return this.http.post<SessionResponse>(`${this.apiUrl}/api/session`, { 
      email, 
      password,
      auth_type: 'email'
    }).pipe(
      tap(response => this.handleSessionResponse(response)),
      catchError(error => this.handleAuthError(error))
    );
  }

  /**
   * Create session with OAuth provider
   */
  loginWithOAuth(data: OAuthLoginData): Observable<SessionResponse> {
    return this.http.post<SessionResponse>(`${this.apiUrl}/api/session`, {
      provider: data.provider,
      token: data.token,
      role: data.role,
      auth_type: 'oauth'
    }).pipe(
      tap(response => this.handleSessionResponse(response)),
      catchError(error => this.handleAuthError(error))
    );
  }

  /**
   * Handle successful session response
   */
  private handleSessionResponse(response: SessionResponse): void {
    if (response.token) {
      localStorage.setItem('authToken', response.token);
      localStorage.setItem('legalai_user', JSON.stringify(response.user));
      localStorage.setItem('legalai_profile', JSON.stringify(response.profile));
      
      this.userSubject.next(response.user);
      this.profileSubject.next(response.profile);
      this.isAuthenticatedSubject.next(true);
      this.isProvisionedSubject.next(response.user.is_provisioned);
    }
  }

  /**
   * Handle authentication errors
   */
  private handleAuthError(error: any): Observable<never> {
    if (error.status === 403 && error.error?.code === 'NOT_PROVISIONED') {
      this.isProvisionedSubject.next(false);
      // Store minimal user info for access request
      if (error.error?.user) {
        localStorage.setItem('legalai_pending_user', JSON.stringify(error.error.user));
      }
    }
    return throwError(() => error);
  }

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
        this.isProvisionedSubject.next(response.user.is_provisioned);
        localStorage.setItem('legalai_user', JSON.stringify(response.user));
        localStorage.setItem('legalai_profile', JSON.stringify(response.profile));
      }),
      catchError(error => {
        if (error.status === 401) {
          this.logout();
        }
        return throwError(() => error);
      })
    );
  }

  /**
   * Refresh session / validate token
   */
  refreshSession(): Observable<SessionResponse> {
    return this.http.post<SessionResponse>(
      `${this.apiUrl}/api/session/refresh`,
      {},
      { headers: this.getHeaders() }
    ).pipe(
      tap(response => this.handleSessionResponse(response)),
      catchError(error => {
        if (error.status === 401) {
          this.logout();
        }
        return throwError(() => error);
      })
    );
  }

  // ============================================
  // LOGOUT
  // ============================================

  /**
   * Logout - clear session and redirect
   */
  logout(): void {
    // Call backend to invalidate session
    this.http.post(`${this.apiUrl}/api/logout`, {}, { headers: this.getHeaders() })
      .pipe(catchError(() => of(null)))
      .subscribe(() => {
        this.clearLocalState();
        this.router.navigate(['/login']);
      });
  }

  /**
   * Logout from all devices
   */
  logoutAllDevices(): Observable<void> {
    return this.http.post<void>(
      `${this.apiUrl}/api/logout/all`,
      {},
      { headers: this.getHeaders() }
    ).pipe(
      tap(() => {
        this.clearLocalState();
        this.router.navigate(['/login']);
      }),
      catchError(error => {
        console.error('Failed to logout from all devices:', error);
        // Still clear local state
        this.clearLocalState();
        this.router.navigate(['/login']);
        return throwError(() => error);
      })
    );
  }

  /**
   * Clear all local state
   */
  private clearLocalState(): void {
    localStorage.removeItem('authToken');
    localStorage.removeItem('legalai_user');
    localStorage.removeItem('legalai_profile');
    localStorage.removeItem('legalai_pending_user');
    
    this.userSubject.next(null);
    this.profileSubject.next(null);
    this.isAuthenticatedSubject.next(false);
    this.isProvisionedSubject.next(true);
  }

  // ============================================
  // AUTH STATE
  // ============================================

  isAuthenticated(): boolean {
    return !!localStorage.getItem('authToken');
  }

  getToken(): string | null {
    return localStorage.getItem('authToken');
  }

  getCurrentUser(): User | null {
    return this.userSubject.getValue();
  }

  getCurrentProfile(): UserProfile | null {
    return this.profileSubject.getValue();
  }

  isUserProvisioned(): boolean {
    return this.isProvisionedSubject.getValue();
  }

  /**
   * Check if user has specific role
   */
  hasRole(role: string | string[]): boolean {
    const user = this.getCurrentUser();
    if (!user) return false;
    
    const roles = Array.isArray(role) ? role : [role];
    return roles.includes(user.role);
  }

  /**
   * Check if lawyer is approved
   */
  isApprovedLawyer(): boolean {
    const user = this.getCurrentUser();
    return user?.role === 'lawyer' && user?.lawyer_status === 'approved';
  }

  private checkAuthStatus(): void {
    const token = this.getToken();
    const cachedUser = localStorage.getItem('legalai_user');
    const cachedProfile = localStorage.getItem('legalai_profile');
    
    if (token) {
      this.isAuthenticatedSubject.next(true);
      
      if (cachedUser) {
        try {
          const user = JSON.parse(cachedUser);
          this.userSubject.next(user);
          this.isProvisionedSubject.next(user.is_provisioned);
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
      
      // Validate token with backend
      this.getMe().pipe(
        catchError(() => of(null))
      ).subscribe();
    }
  }
}