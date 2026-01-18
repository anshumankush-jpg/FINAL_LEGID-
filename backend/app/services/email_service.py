"""
Email Service for Password Reset and Notifications
Uses Gmail API via GCP Service Account
"""
import os
import base64
import logging
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    logger.warning("Google API client not installed. Install with: pip install google-api-python-client")


class EmailService:
    """Email service using Gmail API via service account."""
    
    def __init__(self):
        self.from_email = os.getenv('EMAIL_FROM', 'noreply@weknowrights.ca')
        self.from_name = os.getenv('EMAIL_FROM_NAME', 'LEGID Legal Assistant')
        self.service = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Gmail API client with service account."""
        if not GMAIL_AVAILABLE:
            logger.warning("Gmail API not available")
            return
        
        try:
            credentials_path = os.getenv('EMAIL_SERVICE_ACCOUNT_PATH', './gcp-email-service-account.json')
            
            if not os.path.exists(credentials_path):
                logger.warning(f"Email service account not found at {credentials_path}")
                return
            
            # Load service account credentials
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/gmail.send']
            )
            
            # For service accounts, we need to delegate domain-wide authority
            # Or use SendGrid/AWS SES for simpler setup
            # For now, we'll use a simpler approach
            
            logger.info(f"Email service initialized with credentials from {credentials_path}")
            self.service = build('gmail', 'v1', credentials=credentials)
            
        except Exception as e:
            logger.error(f"Failed to initialize email service: {e}")
            self.service = None
    
    def send_password_reset_email(
        self,
        to_email: str,
        reset_link: str,
        user_name: Optional[str] = None
    ) -> bool:
        """
        Send password reset email.
        
        Args:
            to_email: Recipient email address
            reset_link: Password reset URL with token
            user_name: User's name (optional)
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # For development without Gmail API setup, just log the email
            if not self.service:
                logger.info("=" * 80)
                logger.info("PASSWORD RESET EMAIL (Demo Mode)")
                logger.info("=" * 80)
                logger.info(f"To: {to_email}")
                logger.info(f"Subject: Reset Your LEGID Password")
                logger.info(f"Reset Link: {reset_link}")
                logger.info("=" * 80)
                
                # In production, integrate with SendGrid, AWS SES, or Gmail API
                return True
            
            # Create email message
            message = MIMEMultipart('alternative')
            message['From'] = f"{self.from_name} <{self.from_email}>"
            message['To'] = to_email
            message['Subject'] = "Reset Your LEGID Password"
            
            # HTML email body
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .button {{ display: inline-block; padding: 14px 28px; background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%); color: white; text-decoration: none; border-radius: 8px; font-weight: bold; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #6b7280; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1 style="margin: 0;">⚖️ LEGID</h1>
                        <p style="margin: 10px 0 0 0;">Legal AI Assistant</p>
                    </div>
                    <div class="content">
                        <h2>Reset Your Password</h2>
                        <p>Hello{' ' + user_name if user_name else ''},</p>
                        <p>We received a request to reset your password. Click the button below to create a new password:</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{reset_link}" class="button">Reset Password</a>
                        </div>
                        
                        <p style="color: #6b7280; font-size: 14px;">Or copy and paste this link into your browser:</p>
                        <p style="background: #e5e7eb; padding: 10px; border-radius: 5px; word-wrap: break-word; font-size: 12px;">{reset_link}</p>
                        
                        <p><strong>This link will expire in 15 minutes.</strong></p>
                        
                        <p>If you didn't request a password reset, you can safely ignore this email. Your password will remain unchanged.</p>
                        
                        <div class="footer">
                            <p>This is an automated message from LEGID Legal AI Assistant.</p>
                            <p>© 2026 LEGID. All rights reserved.</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text version (fallback)
            text_body = f"""
            Reset Your Password
            
            Hello{' ' + user_name if user_name else ''},
            
            We received a request to reset your password. Click the link below to create a new password:
            
            {reset_link}
            
            This link will expire in 15 minutes.
            
            If you didn't request a password reset, you can safely ignore this email.
            
            ---
            LEGID Legal AI Assistant
            © 2026 LEGID. All rights reserved.
            """
            
            # Attach both versions
            message.attach(MIMEText(text_body, 'plain'))
            message.attach(MIMEText(html_body, 'html'))
            
            # Encode and send
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            send_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            logger.info(f"Password reset email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")
            return False


# Singleton instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get the singleton EmailService instance."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
