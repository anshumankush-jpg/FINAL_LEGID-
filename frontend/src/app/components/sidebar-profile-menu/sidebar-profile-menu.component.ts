import { Component, Input, Output, EventEmitter, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

interface User {
  id: string;
  email: string;
  name?: string;
  role: string;
  lawyer_status: string;
}

interface UserProfile {
  display_name?: string;
  username?: string;
  avatar_url?: string;
}

@Component({
  selector: 'app-sidebar-profile-menu',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="profile-trigger" (click)="toggleMenu()" [class.active]="isMenuOpen">
      <div class="avatar">
        <img *ngIf="avatarUrl" [src]="avatarUrl" [alt]="displayName || email" />
        <div *ngIf="!avatarUrl" class="avatar-placeholder">
          {{ getInitials() }}
        </div>
      </div>
      <div class="profile-info">
        <div class="display-name">{{ displayName || 'User' }}</div>
      </div>
      <svg class="chevron" [class.rotated]="isMenuOpen" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="6,9 12,15 18,9"></polyline>
      </svg>
    </div>

    <!-- Dropdown Menu -->
    <div class="profile-menu" [class.open]="isMenuOpen" #menuElement>
      <!-- Profile Header -->
      <div class="menu-header" (click)="openEditProfile()">
        <div class="header-avatar">
          <img *ngIf="avatarUrl" [src]="avatarUrl" [alt]="displayName || email" />
          <div *ngIf="!avatarUrl" class="avatar-placeholder large">
            {{ getInitials() }}
          </div>
          <div class="camera-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
              <circle cx="12" cy="13" r="4"></circle>
            </svg>
          </div>
        </div>
        <div class="header-info">
          <div class="header-name">{{ displayName || 'User' }}</div>
          <div class="header-email">{{ user?.email }}</div>
        </div>
      </div>

      <!-- Menu Items -->
      <div class="menu-items">
        <button class="menu-item" (click)="navigateToPersonalization()">
          <svg class="menu-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1 1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
          </svg>
          <span>Personalization</span>
        </button>

        <button class="menu-item" (click)="navigateToSettings()">
          <svg class="menu-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1 1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
          </svg>
          <span>Settings</span>
        </button>

        <div class="menu-section">
          <button class="menu-item" (click)="toggleHelpMenu()">
            <svg class="menu-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
              <path d="M12 17h.01"></path>
            </svg>
            <span>Help</span>
            <svg class="submenu-arrow" [class.expanded]="isHelpMenuOpen" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="9,18 15,12 9,6"></polyline>
            </svg>
          </button>

          <!-- Help Submenu -->
          <div class="submenu" [class.open]="isHelpMenuOpen">
            <button class="submenu-item" (click)="navigateToHelp('center')">Help Center</button>
            <button class="submenu-item" (click)="navigateToHelp('notes')">Release Notes</button>
            <button class="submenu-item" (click)="navigateToHelp('policies')">Terms & Policies</button>
            <button class="submenu-item" (click)="navigateToHelp('bug')">Report Bug</button>
            <button class="submenu-item" (click)="navigateToHelp('shortcuts')">Keyboard Shortcuts</button>
            <button class="submenu-item" (click)="navigateToHelp('apps')">Download Apps</button>
          </div>
        </div>
      </div>

      <!-- Account Summary Card -->
      <div class="account-summary">
        <div class="account-avatar">
          <img *ngIf="avatarUrl" [src]="avatarUrl" [alt]="displayName || email" />
          <div *ngIf="!avatarUrl" class="avatar-placeholder small">
            {{ getInitials() }}
          </div>
        </div>
        <div class="account-info">
          <div class="account-name">{{ displayName || 'User' }}</div>
          <div class="account-role">{{ getRoleLabel() }}</div>
        </div>
      </div>

      <!-- Logout -->
      <div class="menu-footer">
        <button class="menu-item logout" (click)="logout()">
          <svg class="menu-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
            <polyline points="16,17 21,12 16,7"></polyline>
            <line x1="21" y1="12" x2="9" y2="12"></line>
          </svg>
          <span>Log out</span>
        </button>
      </div>
    </div>

    <!-- Backdrop for mobile -->
    <div class="menu-backdrop" [class.visible]="isMenuOpen" (click)="closeMenu()"></div>
  `,
  styles: [`
    .profile-trigger {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.75rem 1rem;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.15s ease;
      margin: 0.5rem 0.25rem;
      border: 1px solid transparent;
    }

    .profile-trigger:hover {
      background: rgba(255, 255, 255, 0.05);
      border-color: rgba(255, 255, 255, 0.1);
    }

    .profile-trigger.active {
      background: rgba(0, 188, 212, 0.1);
      border-color: rgba(0, 188, 212, 0.3);
    }

    .avatar {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      overflow: hidden;
      flex-shrink: 0;
    }

    .avatar img {
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
      font-size: 0.875rem;
    }

    .avatar-placeholder.large {
      width: 48px;
      height: 48px;
      font-size: 1.125rem;
    }

    .avatar-placeholder.small {
      width: 24px;
      height: 24px;
      font-size: 0.75rem;
    }

    .profile-info {
      flex: 1;
      min-width: 0;
    }

    .display-name {
      font-size: 0.875rem;
      font-weight: 500;
      color: #ececec;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .chevron {
      flex-shrink: 0;
      color: #9ca3af;
      transition: transform 0.15s ease;
    }

    .chevron.rotated {
      transform: rotate(180deg);
    }

    .profile-menu {
      position: fixed;
      bottom: 80px;
      left: 16px;
      width: 280px;
      background: #2d2d2d;
      border: 1px solid #404040;
      border-radius: 12px;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
      opacity: 0;
      visibility: hidden;
      transform: translateY(10px);
      transition: all 0.15s ease;
      z-index: 1000;
      max-height: 70vh;
      overflow-y: auto;
    }

    .profile-menu.open {
      opacity: 1;
      visibility: visible;
      transform: translateY(0);
    }

    .menu-header {
      padding: 1rem;
      border-bottom: 1px solid #404040;
      cursor: pointer;
      transition: background-color 0.15s ease;
    }

    .menu-header:hover {
      background: rgba(255, 255, 255, 0.02);
    }

    .header-avatar {
      position: relative;
      display: inline-block;
      margin-bottom: 0.5rem;
    }

    .camera-icon {
      position: absolute;
      bottom: -2px;
      right: -2px;
      width: 20px;
      height: 20px;
      background: #00bcd4;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 2px solid #2d2d2d;
      opacity: 0.8;
    }

    .header-info {
      display: flex;
      flex-direction: column;
      gap: 0.125rem;
    }

    .header-name {
      font-size: 1rem;
      font-weight: 600;
      color: #ececec;
    }

    .header-email {
      font-size: 0.875rem;
      color: #9ca3af;
    }

    .menu-items {
      padding: 0.5rem 0;
    }

    .menu-item {
      width: 100%;
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.75rem 1rem;
      background: none;
      border: none;
      color: #ececec;
      text-align: left;
      cursor: pointer;
      transition: background-color 0.15s ease;
      font-size: 0.875rem;
    }

    .menu-item:hover {
      background: rgba(255, 255, 255, 0.05);
    }

    .menu-item.logout {
      color: #ef4444;
    }

    .menu-item.logout:hover {
      background: rgba(239, 68, 68, 0.1);
    }

    .menu-icon {
      flex-shrink: 0;
      color: #9ca3af;
    }

    .menu-section {
      border-top: 1px solid #404040;
      margin-top: 0.5rem;
      padding-top: 0.5rem;
    }

    .submenu-arrow {
      margin-left: auto;
      transition: transform 0.15s ease;
      color: #6b7280;
    }

    .submenu-arrow.expanded {
      transform: rotate(90deg);
    }

    .submenu {
      max-height: 0;
      overflow: hidden;
      transition: max-height 0.2s ease;
    }

    .submenu.open {
      max-height: 300px;
    }

    .submenu-item {
      width: 100%;
      padding: 0.5rem 1rem 0.5rem 3rem;
      background: none;
      border: none;
      color: #d1d5db;
      text-align: left;
      cursor: pointer;
      font-size: 0.8125rem;
      transition: color 0.15s ease;
    }

    .submenu-item:hover {
      color: #ececec;
    }

    .account-summary {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 1rem;
      background: rgba(255, 255, 255, 0.02);
      border-top: 1px solid #404040;
      margin-top: 0.5rem;
    }

    .account-avatar {
      width: 24px;
      height: 24px;
      border-radius: 50%;
      overflow: hidden;
      flex-shrink: 0;
    }

    .account-info {
      flex: 1;
      min-width: 0;
    }

    .account-name {
      font-size: 0.8125rem;
      font-weight: 500;
      color: #ececec;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .account-role {
      font-size: 0.75rem;
      color: #9ca3af;
    }

    .menu-footer {
      border-top: 1px solid #404040;
      margin-top: 0.5rem;
    }

    .menu-backdrop {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.5);
      opacity: 0;
      visibility: hidden;
      transition: all 0.15s ease;
      z-index: 999;
    }

    .menu-backdrop.visible {
      opacity: 1;
      visibility: visible;
    }

    /* Mobile adjustments */
    @media (max-width: 768px) {
      .profile-menu {
        left: 8px;
        right: 8px;
        width: auto;
        bottom: 72px;
      }

      .menu-header {
        padding: 1.25rem 1rem;
      }
    }
  `]
})
export class SidebarProfileMenuComponent {
  @Input() user: User | null = null;
  @Input() profile: UserProfile | null = null;
  @Output() logoutRequested = new EventEmitter<void>();
  @Output() editProfileRequested = new EventEmitter<void>();

  isMenuOpen = false;
  isHelpMenuOpen = false;

  constructor(private router: Router) {}

  get displayName(): string {
    return this.profile?.display_name || this.user?.name || '';
  }

  get avatarUrl(): string {
    return this.profile?.avatar_url || '';
  }

  get email(): string {
    return this.user?.email || '';
  }

  getInitials(): string {
    const name = this.displayName || this.email;
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) || 'U';
  }

  getRoleLabel(): string {
    if (!this.user) return 'User';

    switch (this.user.role) {
      case 'lawyer':
        return this.user.lawyer_status === 'approved' ? 'Lawyer' : 'Lawyer (Pending)';
      case 'employee':
      case 'employee_admin':
        return 'Employee';
      case 'client':
      default:
        return 'Client';
    }
  }

  toggleMenu(): void {
    this.isMenuOpen = !this.isMenuOpen;
    if (!this.isMenuOpen) {
      this.isHelpMenuOpen = false;
    }
  }

  closeMenu(): void {
    this.isMenuOpen = false;
    this.isHelpMenuOpen = false;
  }

  toggleHelpMenu(): void {
    this.isHelpMenuOpen = !this.isHelpMenuOpen;
  }

  openEditProfile(): void {
    this.editProfileRequested.emit();
    this.closeMenu();
  }

  navigateToPersonalization(): void {
    this.router.navigate(['/personalization']);
    this.closeMenu();
  }

  navigateToSettings(): void {
    this.router.navigate(['/settings']);
    this.closeMenu();
  }

  navigateToHelp(section: string): void {
    this.router.navigate(['/help', section]);
    this.closeMenu();
  }

  logout(): void {
    this.logoutRequested.emit();
    this.closeMenu();
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: Event): void {
    const target = event.target as HTMLElement;
    const menuElement = document.querySelector('.profile-menu');
    const triggerElement = document.querySelector('.profile-trigger');

    if (this.isMenuOpen &&
        menuElement &&
        triggerElement &&
        !menuElement.contains(target) &&
        !triggerElement.contains(target)) {
      this.closeMenu();
    }
  }

  @HostListener('document:keydown.escape')
  onEscapeKey(): void {
    if (this.isMenuOpen) {
      this.closeMenu();
    }
  }
}