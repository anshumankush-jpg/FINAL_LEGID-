import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';

type HelpSection = 'center' | 'notes' | 'policies' | 'bug' | 'shortcuts' | 'apps';

@Component({
  selector: 'app-help',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="help-page">
      <!-- Header -->
      <div class="page-header">
        <div class="header-content">
          <button class="back-btn" (click)="goBack()">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 12H5"></path>
              <path d="M12 19l-7-7 7-7"></path>
            </svg>
          </button>
          <h1>{{ getPageTitle() }}</h1>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <div class="help-nav">
        <button 
          *ngFor="let tab of tabs" 
          class="nav-tab" 
          [class.active]="activeSection === tab.id"
          (click)="setSection(tab.id)"
        >
          <span class="tab-icon" [innerHTML]="tab.icon"></span>
          <span class="tab-label">{{ tab.label }}</span>
        </button>
      </div>

      <!-- Content -->
      <div class="page-content">
        <!-- Help Center -->
        <div *ngIf="activeSection === 'center'" class="help-section">
          <div class="section-intro">
            <h2>How can we help you?</h2>
            <p>Find answers to common questions and learn how to use LegalAI effectively.</p>
          </div>

          <div class="faq-list">
            <div class="faq-item" *ngFor="let faq of faqs" (click)="toggleFaq(faq)">
              <div class="faq-question">
                <span>{{ faq.question }}</span>
                <svg [class.rotated]="faq.expanded" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="6,9 12,15 18,9"></polyline>
                </svg>
              </div>
              <div class="faq-answer" [class.expanded]="faq.expanded">
                {{ faq.answer }}
              </div>
            </div>
          </div>

          <div class="contact-support">
            <h3>Still need help?</h3>
            <p>Our support team is here to assist you.</p>
            <a href="mailto:support@legalai.work" class="support-btn">Contact Support</a>
          </div>
        </div>

        <!-- Release Notes -->
        <div *ngIf="activeSection === 'notes'" class="help-section">
          <div class="section-intro">
            <h2>Release Notes</h2>
            <p>Stay updated with the latest features and improvements.</p>
          </div>

          <div class="release-list">
            <div class="release-item" *ngFor="let release of releases">
              <div class="release-header">
                <span class="release-version">{{ release.version }}</span>
                <span class="release-date">{{ release.date }}</span>
              </div>
              <ul class="release-changes">
                <li *ngFor="let change of release.changes">{{ change }}</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Terms & Policies -->
        <div *ngIf="activeSection === 'policies'" class="help-section">
          <div class="section-intro">
            <h2>Terms & Policies</h2>
            <p>Review our legal documents and policies.</p>
          </div>

          <div class="policy-links">
            <a href="/terms" target="_blank" class="policy-link">
              <div class="policy-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14,2 14,8 20,8"></polyline>
                  <line x1="16" y1="13" x2="8" y2="13"></line>
                  <line x1="16" y1="17" x2="8" y2="17"></line>
                  <polyline points="10,9 9,9 8,9"></polyline>
                </svg>
              </div>
              <div class="policy-content">
                <h3>Terms of Service</h3>
                <p>Our terms and conditions for using LegalAI.</p>
              </div>
            </a>

            <a href="/privacy" target="_blank" class="policy-link">
              <div class="policy-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                </svg>
              </div>
              <div class="policy-content">
                <h3>Privacy Policy</h3>
                <p>How we collect, use, and protect your data.</p>
              </div>
            </a>

            <a href="/cookies" target="_blank" class="policy-link">
              <div class="policy-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
              </div>
              <div class="policy-content">
                <h3>Cookie Policy</h3>
                <p>Information about cookies and tracking.</p>
              </div>
            </a>

            <a href="/acceptable-use" target="_blank" class="policy-link">
              <div class="policy-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22,4 12,14.01 9,11.01"></polyline>
                </svg>
              </div>
              <div class="policy-content">
                <h3>Acceptable Use Policy</h3>
                <p>Guidelines for appropriate use of our services.</p>
              </div>
            </a>
          </div>
        </div>

        <!-- Report Bug -->
        <div *ngIf="activeSection === 'bug'" class="help-section">
          <div class="section-intro">
            <h2>Report a Bug</h2>
            <p>Help us improve by reporting issues you encounter.</p>
          </div>

          <form class="bug-form" (ngSubmit)="submitBugReport()">
            <div class="form-group">
              <label for="bugTitle">Issue Title</label>
              <input 
                id="bugTitle" 
                type="text" 
                [(ngModel)]="bugReport.title" 
                name="title"
                placeholder="Brief description of the issue"
                required
              />
            </div>

            <div class="form-group">
              <label for="bugDescription">Description</label>
              <textarea 
                id="bugDescription" 
                [(ngModel)]="bugReport.description" 
                name="description"
                placeholder="Please provide detailed steps to reproduce the issue..."
                rows="5"
                required
              ></textarea>
            </div>

            <div class="form-group">
              <label for="bugSeverity">Severity</label>
              <select id="bugSeverity" [(ngModel)]="bugReport.severity" name="severity">
                <option value="low">Low - Minor inconvenience</option>
                <option value="medium">Medium - Affects functionality</option>
                <option value="high">High - Major feature broken</option>
                <option value="critical">Critical - Cannot use the app</option>
              </select>
            </div>

            <button type="submit" class="submit-btn" [disabled]="isSubmitting">
              {{ isSubmitting ? 'Submitting...' : 'Submit Report' }}
            </button>
          </form>

          <div class="success-message" *ngIf="bugSubmitted">
            Thank you for your report! We'll investigate and get back to you.
          </div>
        </div>

        <!-- Keyboard Shortcuts -->
        <div *ngIf="activeSection === 'shortcuts'" class="help-section">
          <div class="section-intro">
            <h2>Keyboard Shortcuts</h2>
            <p>Navigate LegalAI faster with these shortcuts.</p>
          </div>

          <div class="shortcuts-list">
            <div class="shortcut-group">
              <h3>General</h3>
              <div class="shortcut-item" *ngFor="let shortcut of shortcuts.general">
                <span class="shortcut-keys">
                  <kbd *ngFor="let key of shortcut.keys">{{ key }}</kbd>
                </span>
                <span class="shortcut-action">{{ shortcut.action }}</span>
              </div>
            </div>

            <div class="shortcut-group">
              <h3>Chat</h3>
              <div class="shortcut-item" *ngFor="let shortcut of shortcuts.chat">
                <span class="shortcut-keys">
                  <kbd *ngFor="let key of shortcut.keys">{{ key }}</kbd>
                </span>
                <span class="shortcut-action">{{ shortcut.action }}</span>
              </div>
            </div>

            <div class="shortcut-group">
              <h3>Navigation</h3>
              <div class="shortcut-item" *ngFor="let shortcut of shortcuts.navigation">
                <span class="shortcut-keys">
                  <kbd *ngFor="let key of shortcut.keys">{{ key }}</kbd>
                </span>
                <span class="shortcut-action">{{ shortcut.action }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Download Apps -->
        <div *ngIf="activeSection === 'apps'" class="help-section">
          <div class="section-intro">
            <h2>Download Apps</h2>
            <p>Access LegalAI on your favorite devices.</p>
          </div>

          <div class="apps-grid">
            <div class="app-card">
              <div class="app-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect>
                  <line x1="12" y1="18" x2="12.01" y2="18"></line>
                </svg>
              </div>
              <h3>iOS App</h3>
              <p>Download for iPhone and iPad</p>
              <button class="download-btn" disabled>Coming Soon</button>
            </div>

            <div class="app-card">
              <div class="app-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect>
                  <line x1="12" y1="18" x2="12.01" y2="18"></line>
                </svg>
              </div>
              <h3>Android App</h3>
              <p>Download for Android devices</p>
              <button class="download-btn" disabled>Coming Soon</button>
            </div>

            <div class="app-card">
              <div class="app-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
                  <line x1="8" y1="21" x2="16" y2="21"></line>
                  <line x1="12" y1="17" x2="12" y2="21"></line>
                </svg>
              </div>
              <h3>Desktop App</h3>
              <p>Download for Windows and Mac</p>
              <button class="download-btn" disabled>Coming Soon</button>
            </div>

            <div class="app-card featured">
              <div class="app-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="2" y1="12" x2="22" y2="12"></line>
                  <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
                </svg>
              </div>
              <h3>Web App</h3>
              <p>Use LegalAI in your browser</p>
              <button class="download-btn active" (click)="openWebApp()">Open Now</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .help-page {
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

    .help-nav {
      display: flex;
      gap: 0.5rem;
      padding: 1rem 2rem;
      border-bottom: 1px solid #404040;
      overflow-x: auto;
    }

    .nav-tab {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.75rem 1rem;
      background: none;
      border: 1px solid transparent;
      border-radius: 8px;
      color: #9ca3af;
      cursor: pointer;
      transition: all 0.15s ease;
      white-space: nowrap;
      font-size: 0.875rem;
    }

    .nav-tab:hover {
      background: rgba(255, 255, 255, 0.05);
      color: #ececec;
    }

    .nav-tab.active {
      background: rgba(0, 188, 212, 0.1);
      border-color: #00bcd4;
      color: #00bcd4;
    }

    .tab-icon {
      display: flex;
      align-items: center;
    }

    .page-content {
      max-width: 900px;
      margin: 0 auto;
      padding: 2rem;
    }

    .help-section {
      animation: fadeIn 0.2s ease-out;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .section-intro {
      margin-bottom: 2rem;
    }

    .section-intro h2 {
      font-size: 1.5rem;
      font-weight: 600;
      margin: 0 0 0.5rem 0;
      color: #ececec;
    }

    .section-intro p {
      color: #9ca3af;
      margin: 0;
      font-size: 1rem;
      line-height: 1.5;
    }

    /* FAQ Styles */
    .faq-list {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }

    .faq-item {
      background: #2d2d2d;
      border: 1px solid #404040;
      border-radius: 8px;
      overflow: hidden;
      cursor: pointer;
    }

    .faq-question {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1rem 1.25rem;
      font-weight: 500;
      color: #ececec;
    }

    .faq-question svg {
      flex-shrink: 0;
      color: #9ca3af;
      transition: transform 0.2s ease;
    }

    .faq-question svg.rotated {
      transform: rotate(180deg);
    }

    .faq-answer {
      max-height: 0;
      overflow: hidden;
      padding: 0 1.25rem;
      color: #9ca3af;
      line-height: 1.6;
      transition: all 0.2s ease;
    }

    .faq-answer.expanded {
      max-height: 500px;
      padding: 0 1.25rem 1rem;
    }

    .contact-support {
      margin-top: 3rem;
      padding: 2rem;
      background: #2d2d2d;
      border-radius: 12px;
      text-align: center;
    }

    .contact-support h3 {
      margin: 0 0 0.5rem 0;
      color: #ececec;
    }

    .contact-support p {
      margin: 0 0 1.5rem 0;
      color: #9ca3af;
    }

    .support-btn {
      display: inline-block;
      padding: 0.75rem 1.5rem;
      background: #00bcd4;
      color: white;
      text-decoration: none;
      border-radius: 8px;
      font-weight: 500;
      transition: background-color 0.15s ease;
    }

    .support-btn:hover {
      background: #0097a7;
    }

    /* Release Notes */
    .release-list {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    .release-item {
      background: #2d2d2d;
      border: 1px solid #404040;
      border-radius: 12px;
      padding: 1.5rem;
    }

    .release-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
    }

    .release-version {
      font-weight: 600;
      color: #00bcd4;
      font-size: 1.125rem;
    }

    .release-date {
      color: #9ca3af;
      font-size: 0.875rem;
    }

    .release-changes {
      margin: 0;
      padding-left: 1.25rem;
      color: #d1d5db;
    }

    .release-changes li {
      margin-bottom: 0.5rem;
      line-height: 1.5;
    }

    /* Policy Links */
    .policy-links {
      display: grid;
      gap: 1rem;
    }

    .policy-link {
      display: flex;
      align-items: center;
      gap: 1rem;
      padding: 1.25rem;
      background: #2d2d2d;
      border: 1px solid #404040;
      border-radius: 12px;
      text-decoration: none;
      transition: all 0.15s ease;
    }

    .policy-link:hover {
      border-color: #00bcd4;
      background: rgba(0, 188, 212, 0.05);
    }

    .policy-icon {
      flex-shrink: 0;
      color: #00bcd4;
    }

    .policy-content h3 {
      margin: 0 0 0.25rem 0;
      color: #ececec;
      font-size: 1rem;
    }

    .policy-content p {
      margin: 0;
      color: #9ca3af;
      font-size: 0.875rem;
    }

    /* Bug Report Form */
    .bug-form {
      background: #2d2d2d;
      border: 1px solid #404040;
      border-radius: 12px;
      padding: 2rem;
    }

    .form-group {
      margin-bottom: 1.5rem;
    }

    .form-group label {
      display: block;
      margin-bottom: 0.5rem;
      font-weight: 500;
      color: #ececec;
    }

    .form-group input,
    .form-group textarea,
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
    .form-group textarea:focus,
    .form-group select:focus {
      outline: none;
      border-color: #00bcd4;
    }

    .submit-btn {
      width: 100%;
      padding: 0.875rem;
      background: #00bcd4;
      color: white;
      border: none;
      border-radius: 8px;
      font-weight: 500;
      font-size: 1rem;
      cursor: pointer;
      transition: background-color 0.15s ease;
    }

    .submit-btn:hover:not(:disabled) {
      background: #0097a7;
    }

    .submit-btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .success-message {
      margin-top: 1.5rem;
      padding: 1rem;
      background: #166534;
      color: #bbf7d0;
      border-radius: 8px;
      text-align: center;
    }

    /* Keyboard Shortcuts */
    .shortcuts-list {
      display: flex;
      flex-direction: column;
      gap: 2rem;
    }

    .shortcut-group h3 {
      margin: 0 0 1rem 0;
      color: #ececec;
      font-size: 1rem;
      font-weight: 600;
    }

    .shortcut-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.75rem 1rem;
      background: #2d2d2d;
      border-radius: 8px;
      margin-bottom: 0.5rem;
    }

    .shortcut-keys {
      display: flex;
      gap: 0.25rem;
    }

    .shortcut-keys kbd {
      display: inline-block;
      padding: 0.25rem 0.5rem;
      background: #1f1f1f;
      border: 1px solid #404040;
      border-radius: 4px;
      font-family: monospace;
      font-size: 0.875rem;
      color: #00bcd4;
    }

    .shortcut-action {
      color: #9ca3af;
      font-size: 0.875rem;
    }

    /* Apps Grid */
    .apps-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1.5rem;
    }

    .app-card {
      background: #2d2d2d;
      border: 1px solid #404040;
      border-radius: 12px;
      padding: 2rem;
      text-align: center;
      transition: all 0.15s ease;
    }

    .app-card:hover {
      border-color: #00bcd4;
    }

    .app-card.featured {
      border-color: #00bcd4;
      background: rgba(0, 188, 212, 0.05);
    }

    .app-icon {
      color: #9ca3af;
      margin-bottom: 1rem;
    }

    .app-card.featured .app-icon {
      color: #00bcd4;
    }

    .app-card h3 {
      margin: 0 0 0.5rem 0;
      color: #ececec;
      font-size: 1.125rem;
    }

    .app-card p {
      margin: 0 0 1.5rem 0;
      color: #9ca3af;
      font-size: 0.875rem;
    }

    .download-btn {
      width: 100%;
      padding: 0.75rem;
      background: #374151;
      color: #9ca3af;
      border: none;
      border-radius: 8px;
      font-weight: 500;
      cursor: not-allowed;
    }

    .download-btn.active {
      background: #00bcd4;
      color: white;
      cursor: pointer;
    }

    .download-btn.active:hover {
      background: #0097a7;
    }

    /* Mobile */
    @media (max-width: 768px) {
      .page-header {
        padding: 1rem;
      }

      .help-nav {
        padding: 0.75rem 1rem;
      }

      .nav-tab {
        padding: 0.5rem 0.75rem;
        font-size: 0.8125rem;
      }

      .page-content {
        padding: 1rem;
      }

      .apps-grid {
        grid-template-columns: 1fr;
      }
    }
  `]
})
export class HelpComponent implements OnInit {
  activeSection: HelpSection = 'center';
  
  tabs = [
    { id: 'center' as HelpSection, label: 'Help Center', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><path d="M12 17h.01"></path></svg>' },
    { id: 'notes' as HelpSection, label: 'Release Notes', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14,2 14,8 20,8"></polyline></svg>' },
    { id: 'policies' as HelpSection, label: 'Terms & Policies', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>' },
    { id: 'bug' as HelpSection, label: 'Report Bug', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>' },
    { id: 'shortcuts' as HelpSection, label: 'Shortcuts', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2" ry="2"></rect><path d="M6 8h.001"></path><path d="M10 8h.001"></path><path d="M14 8h.001"></path><path d="M18 8h.001"></path><path d="M8 12h.001"></path><path d="M12 12h.001"></path><path d="M16 12h.001"></path><path d="M7 16h10"></path></svg>' },
    { id: 'apps' as HelpSection, label: 'Download Apps', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7,10 12,15 17,10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>' }
  ];

  faqs = [
    { question: 'What is LegalAI?', answer: 'LegalAI is an AI-powered legal assistant that helps you understand legal documents, get answers to legal questions, and navigate legal processes in Canada and the USA.', expanded: false },
    { question: 'Is LegalAI a replacement for a lawyer?', answer: 'No. LegalAI provides general legal information and guidance, but it is not a substitute for professional legal advice. For specific legal matters, always consult with a licensed lawyer or paralegal.', expanded: false },
    { question: 'How accurate is the legal information?', answer: 'LegalAI uses advanced AI models trained on legal documents and case law. While we strive for accuracy, laws change frequently and vary by jurisdiction. Always verify important information with official sources.', expanded: false },
    { question: 'Is my data secure?', answer: 'Yes. We use industry-standard encryption and security practices to protect your data. Your conversations are private and we do not share your information with third parties without your consent.', expanded: false },
    { question: 'What jurisdictions does LegalAI cover?', answer: 'LegalAI currently focuses on Canadian and US law, with specific coverage for provinces and states. We are continuously expanding our coverage.', expanded: false },
    { question: 'How do I become a verified lawyer on LegalAI?', answer: 'Lawyers can apply for verification by submitting their bar license and credentials through the lawyer portal. Our team reviews applications within 2-3 business days.', expanded: false }
  ];

  releases = [
    { version: 'v2.1.0', date: 'January 2026', changes: ['Added ChatGPT-style profile menu', 'Improved response animation', 'Enhanced legal reasoning with multi-brain system', 'Bug fixes and performance improvements'] },
    { version: 'v2.0.0', date: 'December 2025', changes: ['Complete UI redesign', 'Added document generator', 'Lawyer verification system', 'Multi-language support'] },
    { version: 'v1.5.0', date: 'November 2025', changes: ['Voice chat feature', 'Case lookup integration', 'Improved search functionality'] }
  ];

  shortcuts = {
    general: [
      { keys: ['Ctrl', 'K'], action: 'Open command palette' },
      { keys: ['Ctrl', '/'], action: 'Toggle sidebar' },
      { keys: ['Esc'], action: 'Close modal/menu' }
    ],
    chat: [
      { keys: ['Enter'], action: 'Send message' },
      { keys: ['Shift', 'Enter'], action: 'New line in message' },
      { keys: ['Ctrl', 'N'], action: 'New chat' }
    ],
    navigation: [
      { keys: ['Ctrl', 'H'], action: 'Go to chat history' },
      { keys: ['Ctrl', 'S'], action: 'Go to settings' },
      { keys: ['Ctrl', 'P'], action: 'Go to profile' }
    ]
  };

  bugReport = {
    title: '',
    description: '',
    severity: 'medium'
  };

  isSubmitting = false;
  bugSubmitted = false;

  constructor(
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    // Check for section in route params
    this.route.params.subscribe(params => {
      if (params['section'] && this.isValidSection(params['section'])) {
        this.activeSection = params['section'] as HelpSection;
      }
    });
  }

  isValidSection(section: string): boolean {
    return ['center', 'notes', 'policies', 'bug', 'shortcuts', 'apps'].includes(section);
  }

  getPageTitle(): string {
    const titles: Record<HelpSection, string> = {
      center: 'Help Center',
      notes: 'Release Notes',
      policies: 'Terms & Policies',
      bug: 'Report a Bug',
      shortcuts: 'Keyboard Shortcuts',
      apps: 'Download Apps'
    };
    return titles[this.activeSection];
  }

  setSection(section: HelpSection): void {
    this.activeSection = section;
  }

  toggleFaq(faq: any): void {
    faq.expanded = !faq.expanded;
  }

  submitBugReport(): void {
    if (this.isSubmitting) return;
    
    this.isSubmitting = true;
    
    // Simulate API call
    setTimeout(() => {
      this.isSubmitting = false;
      this.bugSubmitted = true;
      this.bugReport = { title: '', description: '', severity: 'medium' };
      
      setTimeout(() => {
        this.bugSubmitted = false;
      }, 5000);
    }, 1500);
  }

  openWebApp(): void {
    window.location.href = '/chat';
  }

  goBack(): void {
    this.router.navigate(['/chat']);
  }
}
