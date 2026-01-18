import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {
  loginForm: FormGroup;
  errorMessage: string = '';
  isLoading: boolean = false;
  showForgotPassword: boolean = false;
  forgotPasswordEmail: string = '';
  forgotPasswordMessage: string = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  onSubmit(): void {
    if (this.loginForm.valid) {
      this.isLoading = true;
      this.errorMessage = '';
      
      this.authService.login(
        this.loginForm.value.email,
        this.loginForm.value.password
      ).subscribe({
        next: () => {
          this.router.navigate(['/chat']);
        },
        error: (error) => {
          this.errorMessage = error.error?.detail || 'Login failed. Please try again.';
          this.isLoading = false;
        }
      });
    }
  }

  loginWithGoogle(): void {
    this.authService.loginWithGoogle();
  }

  loginWithMicrosoft(): void {
    this.authService.loginWithMicrosoft();
  }

  goToSignup(): void {
    this.router.navigate(['/signup']);
  }

  toggleForgotPassword(): void {
    this.showForgotPassword = !this.showForgotPassword;
    this.forgotPasswordMessage = '';
    this.errorMessage = '';
    if (this.showForgotPassword) {
      this.forgotPasswordEmail = this.loginForm.get('email')?.value || '';
    }
  }

  sendPasswordReset(): void {
    if (!this.forgotPasswordEmail || !this.forgotPasswordEmail.includes('@')) {
      this.forgotPasswordMessage = 'Please enter a valid email address';
      return;
    }

    this.isLoading = true;
    this.forgotPasswordMessage = '';

    this.authService.requestPasswordReset(this.forgotPasswordEmail).subscribe({
      next: (response) => {
        this.forgotPasswordMessage = response.message || 'Password reset link sent to your email';
        this.isLoading = false;
        
        // Show reset link for demo/testing
        if (response.reset_link) {
          console.log('Password Reset Link (for testing):', response.reset_link);
          this.forgotPasswordMessage += ' (Check console for demo link)';
        }
      },
      error: (error) => {
        this.forgotPasswordMessage = 'An error occurred. Please try again.';
        this.isLoading = false;
      }
    });
  }
}