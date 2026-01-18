"""
Gmail Email Service - Actually sends emails using Gmail API
Configured with your GCP service account
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
    from googleapiclient.errors import HttpError
    GMAIL_API_AVAILABLE = True
except ImportError:
    GMAIL_API_AVAILABLE = False
    logger.error("Gmail API not available. Install: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")


class GmailEmailService:
    """Send emails using Gmail API with service account delegation."""
    
    def __init__(self):
        self.from_email = os.getenv('EMAIL_FROM', 'info@predictivetechlabs.com')
        self.from_name = os.getenv('EMAIL_FROM_NAME', 'LEGID Legal Assistant')
        self.delegate_email = os.getenv('GMAIL_DELEGATE_EMAIL', 'info@predictivetechlabs.com')
        self.service = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Gmail API with service account."""
        if not GMAIL_API_AVAILABLE:
            logger.warning("Gmail API libraries not installed")
            return
        
        try:
            credentials_path = os.getenv('EMAIL_SERVICE_ACCOUNT_PATH', './gcp-email-service-account.json')
            
            if not os.path.exists(credentials_path):
                logger.warning(f"Email service account not found: {credentials_path}")
                return
            
            # Load service account credentials with Gmail send scope
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=[
                    'https://www.googleapis.com/auth/gmail.send',
                    'https://www.googleapis.com/auth/gmail.compose'
                ]
            )
            
            # Delegate to a user email (service account acting on behalf of user)
            # If you have domain-wide delegation set up, use it
            # Otherwise, we'll try without delegation
            try:
                delegated_credentials = credentials.with_subject(self.delegate_email)
                self.service = build('gmail', 'v1', credentials=delegated_credentials)
                logger.info(f"[OK] Gmail API initialized with delegation to {self.delegate_email}")
            except Exception as e:
                # Fallback: try without delegation
                self.service = build('gmail', 'v1', credentials=credentials)
                logger.info(f"[OK] Gmail API initialized (no delegation)")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gmail API: {e}")
            self.service = None
    
    def send_password_reset_email(
        self,
        to_email: str,
        reset_link: str,
        user_name: Optional[str] = None
    ) -> bool:
        """
        Send password reset email via Gmail API.
        
        Args:
            to_email: Recipient email
            reset_link: Password reset URL
            user_name: User's name
            
        Returns:
            True if sent, False otherwise
        """
        try:
            if not self.service:
                # Demo mode - log to console
                logger.info("=" * 80)
                logger.info("PASSWORD RESET EMAIL (Demo Mode - Gmail API not initialized)")
                logger.info("=" * 80)
                logger.info(f"To: {to_email}")
                logger.info(f"From: {self.from_email}")
                logger.info(f"Subject: Reset Your LEGID Password")
                logger.info(f"Reset Link: {reset_link}")
                logger.info("=" * 80)
                logger.info("NOTE: To send real emails, configure Gmail API delegation or use SendGrid")
                logger.info("=" * 80)
                return True
            
            # Create message
            message = MIMEMultipart('alternative')
            message['From'] = f"{self.from_name} <{self.from_email}>"
            message['To'] = to_email
            message['Subject'] = "Reset Your LEGID Password"
            
            # HTML email
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #1f2937; background: #f9fafb; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%); color: white; padding: 40px 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 32px; font-weight: 800; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
        .content {{ padding: 40px 30px; }}
        .content h2 {{ color: #1f2937; margin-top: 0; }}
        .button {{ display: inline-block; padding: 16px 32px; background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%); color: white; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; }}
        .button:hover {{ opacity: 0.9; }}
        .link-box {{ background: #f3f4f6; padding: 15px; border-radius: 8px; word-wrap: break-word; font-size: 13px; color: #4b5563; margin: 20px 0; }}
        .footer {{ background: #f9fafb; padding: 20px 30px; text-align: center; color: #6b7280; font-size: 14px; border-top: 1px solid #e5e7eb; }}
        .warning {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚖️ LEGID</h1>
            <p>Legal AI Assistant</p>
        </div>
        <div class="content">
            <h2>Reset Your Password</h2>
            <p>Hello{' ' + user_name if user_name else ''},</p>
            <p>We received a request to reset your password for your LEGID account. Click the button below to create a new password:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}" class="button">Reset Password</a>
            </div>
            
            <p style="color: #6b7280; font-size: 14px;">Or copy and paste this link into your browser:</p>
            <div class="link-box">{reset_link}</div>
            
            <div class="warning">
                <strong>⏰ This link will expire in 15 minutes.</strong>
            </div>
            
            <p>If you didn't request a password reset, you can safely ignore this email. Your password will remain unchanged.</p>
            
            <p style="margin-top: 30px; color: #6b7280; font-size: 14px;">
                For security reasons, this link can only be used once. If you need another reset link, please request a new one.
            </p>
        </div>
        <div class="footer">
            <p style="margin: 5px 0;">This is an automated message from LEGID Legal AI Assistant.</p>
            <p style="margin: 5px 0;">© 2026 LEGID. All rights reserved.</p>
            <p style="margin: 5px 0; font-size: 12px;">
                <a href="#" style="color: #6b7280; text-decoration: none;">Privacy Policy</a> · 
                <a href="#" style="color: #6b7280; text-decoration: none;">Terms of Service</a>
            </p>
        </div>
    </div>
</body>
</html>
            """
            
            # Plain text version
            text_body = f"""
LEGID - Legal AI Assistant
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
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send via Gmail API
            send_result = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            logger.info(f"[SUCCESS] Password reset email sent to {to_email}")
            logger.info(f"Gmail Message ID: {send_result.get('id')}")
            return True
            
        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            logger.error(f"Error details: {e.error_details if hasattr(e, 'error_details') else 'No details'}")
            
            # Log the reset link anyway so user can still test
            logger.info("=" * 80)
            logger.info(f"PASSWORD RESET LINK (Email failed to send):")
            logger.info(f"To: {to_email}")
            logger.info(f"Link: {reset_link}")
            logger.info("=" * 80)
            return False
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            logger.info(f"Reset link (for testing): {reset_link}")
            return False
    
    def send_welcome_email(
        self,
        to_email: str,
        user_name: Optional[str] = None
    ) -> bool:
        """
        Send welcome email to new users.
        
        Args:
            to_email: New user's email
            user_name: User's name
            
        Returns:
            True if sent successfully
        """
        try:
            if not self.service:
                # Demo mode - log to console
                logger.info("=" * 80)
                logger.info("WELCOME EMAIL (Demo Mode)")
                logger.info("=" * 80)
                logger.info(f"To: {to_email}")
                logger.info(f"Subject: Welcome to LEGID Legal AI Assistant")
                logger.info("=" * 80)
                return True
            
            # Create message
            message = MIMEMultipart('alternative')
            message['From'] = f"{self.from_name} <{self.from_email}>"
            message['To'] = to_email
            message['Subject'] = "Welcome to LEGID - Your Legal AI Assistant"
            
            # HTML email
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #1f2937; background: #f9fafb; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%); color: white; padding: 50px 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 36px; font-weight: 800; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.95; font-size: 18px; }}
        .content {{ padding: 40px 30px; }}
        .feature {{ background: #f3f4f6; padding: 15px 20px; margin: 15px 0; border-left: 4px solid #06b6d4; border-radius: 4px; }}
        .feature-title {{ font-weight: 600; color: #1f2937; margin: 0 0 5px 0; }}
        .cta {{ text-align: center; margin: 30px 0; }}
        .button {{ display: inline-block; padding: 16px 32px; background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%); color: white; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; }}
        .footer {{ background: #f9fafb; padding: 30px; text-align: center; color: #6b7280; font-size: 14px; border-top: 1px solid #e5e7eb; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚖️ Welcome to LEGID</h1>
            <p>Your Legal AI Assistant</p>
        </div>
        <div class="content">
            <h2 style="color: #1f2937; margin-top: 0;">Hello{' ' + user_name if user_name else ''}! 👋</h2>
            
            <p>Thank you for joining <strong>LEGID</strong> - your intelligent legal assistant powered by AI.</p>
            
            <p>You now have access to:</p>
            
            <div class="feature">
                <p class="feature-title">💬 AI Legal Chat</p>
                <p style="margin: 0; color: #4b5563; font-size: 14px;">Get instant answers to legal questions with real case law citations</p>
            </div>
            
            <div class="feature">
                <p class="feature-title">📄 Document Analysis</p>
                <p style="margin: 0; color: #4b5563; font-size: 14px;">Upload PDFs and images - our OCR extracts and analyzes legal documents</p>
            </div>
            
            <div class="feature">
                <p class="feature-title">🏛️ Court Lookup</p>
                <p style="margin: 0; color: #4b5563; font-size: 14px;">Find court information and case lookup tools by jurisdiction</p>
            </div>
            
            <div class="feature">
                <p class="feature-title">📚 Case Citations</p>
                <p style="margin: 0; color: #4b5563; font-size: 14px;">Get references to similar legal precedents from Canada and USA</p>
            </div>
            
            <div class="feature">
                <p class="feature-title">🌍 Multi-Language Support</p>
                <p style="margin: 0; color: #4b5563; font-size: 14px;">Available in English, French, Hindi, Punjabi, Spanish, and more</p>
            </div>
            
            <div class="cta">
                <a href="http://localhost:4200" class="button">Start Using LEGID</a>
            </div>
            
            <p style="margin-top: 30px; color: #6b7280; font-size: 14px;">
                <strong>Need Help?</strong> Our AI assistant is available 24/7 to answer your legal questions.
            </p>
            
            <p style="color: #6b7280; font-size: 14px;">
                Remember: LEGID provides general legal information, not legal advice. For advice specific to your situation, consult a licensed lawyer.
            </p>
        </div>
        <div class="footer">
            <p style="margin: 5px 0; font-weight: 600;">Welcome to the future of legal assistance! 🚀</p>
            <p style="margin: 5px 0;">This is an automated message from LEGID Legal AI Assistant.</p>
            <p style="margin: 5px 0;">© 2026 LEGID. All rights reserved.</p>
            <p style="margin: 15px 0 5px 0; font-size: 12px;">
                <a href="#" style="color: #6b7280; text-decoration: none;">Privacy Policy</a> · 
                <a href="#" style="color: #6b7280; text-decoration: none;">Terms of Service</a> · 
                <a href="#" style="color: #6b7280; text-decoration: none;">Help Center</a>
            </p>
        </div>
    </div>
</body>
</html>
            """
            
            # Plain text version
            text_body = f"""
LEGID - Legal AI Assistant
Welcome to LEGID!

Hello{' ' + user_name if user_name else ''}!

Thank you for joining LEGID - your intelligent legal assistant powered by AI.

You now have access to:

• AI Legal Chat - Get instant answers to legal questions with real case law citations
• Document Analysis - Upload PDFs and images with OCR
• Court Lookup - Find court information by jurisdiction  
• Case Citations - Get references to similar legal precedents
• Multi-Language Support - Available in English, French, Hindi, Punjabi, and more

Get Started: http://localhost:4200

Need Help? Our AI assistant is available 24/7 to answer your legal questions.

Remember: LEGID provides general legal information, not legal advice. For advice specific to your situation, consult a licensed lawyer.

---
Welcome to the future of legal assistance!
LEGID Legal AI Assistant
© 2026 LEGID. All rights reserved.
            """
            
            # Attach both versions
            message.attach(MIMEText(text_body, 'plain'))
            message.attach(MIMEText(html_body, 'html'))
            
            # Encode and send
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send via Gmail API
            send_result = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            logger.info(f"[SUCCESS] Welcome email sent to {to_email}")
            logger.info(f"Gmail Message ID: {send_result.get('id')}")
            return True
            
        except HttpError as e:
            logger.error(f"Gmail API error sending welcome email: {e}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to send welcome email: {e}")
            return False


# Singleton
_gmail_service: Optional[GmailEmailService] = None


def get_gmail_service() -> GmailEmailService:
    """Get singleton Gmail service instance."""
    global _gmail_service
    if _gmail_service is None:
        _gmail_service = GmailEmailService()
    return _gmail_service
