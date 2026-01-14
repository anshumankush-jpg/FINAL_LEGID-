import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, Router, UrlTree } from '@angular/router';
import { Observable, of } from 'rxjs';
import { map, catchError, take } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class RoleGuard implements CanActivate {
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(route: ActivatedRouteSnapshot): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    // First check if user is authenticated
    if (!this.authService.isAuthenticated()) {
      return this.router.createUrlTree(['/login']);
    }

    // Get required roles from route data
    const requiredRoles = route.data['roles'] as string[] | undefined;
    const requireApprovedLawyer = route.data['requireApprovedLawyer'] as boolean | undefined;

    // If no roles specified, allow access
    if (!requiredRoles && !requireApprovedLawyer) {
      return true;
    }

    return this.authService.user$.pipe(
      take(1),
      map(user => {
        if (!user) {
          return this.router.createUrlTree(['/login']);
        }

        // Check if user is provisioned
        if (!user.is_provisioned) {
          return this.router.createUrlTree(['/not-provisioned']);
        }

        // Check for approved lawyer requirement
        if (requireApprovedLawyer) {
          if (user.role === 'lawyer' && user.lawyer_status === 'approved') {
            return true;
          }
          // Redirect to lawyer status page or access denied
          return this.router.createUrlTree(['/access-denied']);
        }

        // Check role requirement
        if (requiredRoles && requiredRoles.length > 0) {
          if (requiredRoles.includes(user.role)) {
            return true;
          }
          return this.router.createUrlTree(['/access-denied']);
        }

        return true;
      }),
      catchError(() => {
        return of(this.router.createUrlTree(['/login']));
      })
    );
  }
}
