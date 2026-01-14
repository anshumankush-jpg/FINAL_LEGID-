import { Injectable } from '@angular/core';
import { CanActivate, Router, UrlTree } from '@angular/router';
import { Observable, of } from 'rxjs';
import { map, catchError, take } from 'rxjs/operators';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

interface UserCheckResponse {
  is_provisioned: boolean;
  user?: {
    id: string;
    email: string;
    name?: string;
    role: string;
    lawyer_status: string;
  };
}

@Injectable({
  providedIn: 'root'
})
export class ProvisionedGuard implements CanActivate {
  private apiUrl = environment.apiUrl || 'http://localhost:8000';

  constructor(
    private router: Router,
    private http: HttpClient
  ) {}

  canActivate(): Observable<boolean | UrlTree> {
    const token = localStorage.getItem('authToken');
    
    if (!token) {
      return of(this.router.createUrlTree(['/login']));
    }

    // Check if user is provisioned
    return this.http.get<UserCheckResponse>(`${this.apiUrl}/api/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }).pipe(
      take(1),
      map(response => {
        // Check if user is provisioned
        if (response.is_provisioned === false) {
          // Store user info for the not-provisioned page
          if (response.user) {
            localStorage.setItem('pendingUser', JSON.stringify(response.user));
          }
          return this.router.createUrlTree(['/not-provisioned']);
        }
        return true;
      }),
      catchError(error => {
        console.error('Provisioned check failed:', error);
        
        // If 403, user is not provisioned
        if (error.status === 403) {
          const errorData = error.error;
          if (errorData?.code === 'NOT_PROVISIONED') {
            if (errorData.user) {
              localStorage.setItem('pendingUser', JSON.stringify(errorData.user));
            }
            return of(this.router.createUrlTree(['/not-provisioned']));
          }
        }
        
        // For other errors, redirect to login
        localStorage.removeItem('authToken');
        return of(this.router.createUrlTree(['/login']));
      })
    );
  }
}
