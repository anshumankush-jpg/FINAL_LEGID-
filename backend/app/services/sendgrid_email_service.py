"""
SendGrid Email Service - Actually sends emails!
Much simpler than Gmail API - no domain delegation needed
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    logger.warning("SendGrid not installed. Install with: pip install sendgrid")


class SendGridEmailService:
    """Send emails using SendGrid API - Simple and reliable!"""
    
    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('EMAIL_FROM', 'noreply@weknowrights.ca')
        self.from_name = os.getenv('EMAIL_FROM_NAME', 'LEGID Legal Assistant')
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """Initialize SendGrid client."""
        if not SENDGRID_AVAILABLE:
            logger.warning("[WARN] SendGrid library not installed")
            logger.info("Install with: pip install sendgrid")
            return
        
        if not self.api_key:
            logger.warning("[WARN] SENDGRID_API_KEY not set in environment")
            logger.info("Get free API key at: https://sendgrid.com")
            return
        
        try:
            self.client = SendGridAPIClient(self.api_key)
            logger.info(f"[OK] SendGrid email service initialized")
            logger.info(f"     Sending from: {self.from_email}")
        except Exception as e:
            logger.error(f"Failed to initialize SendGrid: {e}")
            self.client = None
    
    def send_password_reset_email(
        self,
        to_email: str,
        reset_link: str,
        user_name: Optional[str] = None
    ) -> bool:
        """Send password reset email via SendGrid."""
        try:
            if not self.client:
                # Demo mode
                logger.info("=" * 80)
                logger.info("PASSWORD RESET EMAIL (Demo Mode - SendGrid not configured)")
                logger.info("=" * 80)
                logger.info(f"To: {to_email}")
                logger.info(f"Subject: Reset Your LEGID Password")
                logger.info(f"Reset Link: {reset_link}")
                logger.info("=" * 80)
                logger.info("To enable email sending: Get SendGrid API key at https://sendgrid.com")
                logger.info("=" * 80)
                return False
            
            # HTML email body
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #1f2937; background: #f9fafb; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%); color: white; padding: 50px 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 36px; font-weight: 800; }}
        .content {{ padding: 40px 30px; }}
        .button {{ display: inline-block; padding: 16px 32px; background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%); color: white; text-decoration: none; border-radius: 8px; font-weight: 600; }}
        .link-box {{ background: #f3f4f6; padding: 15px; border-radius: 8px; word-wrap: break-word; font-size: 13px; color: #4b5563; margin: 20px 0; }}
        .warning {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; }}
        .footer {{ background: #f9fafb; padding: 30px; text-align: center; color: #6b7280; font-size: 14px; border-top: 1px solid #e5e7eb; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚖️ LEGID</h1>
            <p style="margin: 10px 0 0 0;">Legal AI Assistant</p>
        </div>
        <div class="content">
            <h2 style="color: #1f2937;">Reset Your Password</h2>
            <p>Hello{' ' + user_name if user_name else ''},</p>
            <p>We received a request to reset your password for your LEGID account. Click the button below to create a new password:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}" class="button">Reset Password</a>
            </div>
            
            <p style="color: #6b7280; font-size: 14px;">Or copy and paste this link:</p>
            <div class="link-box">{reset_link}</div>
            
            <div class="warning">
                <strong>⏰ This link expires in 15 minutes.</strong>
            </div>
            
            <p>If you didn't request this, ignore this email. Your password won't change.</p>
        </div>
        <div class="footer">
            <p>© 2026 LEGID. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """
            
            # Plain text version
            text_content = f"""
LEGID - Legal AI Assistant
Reset Your Password

Hello{' ' + user_name if user_name else ''},

We received a request to reset your password. Click this link:

{reset_link}

This link expires in 15 minutes.

If you didn't request this, ignore this email.

© 2026 LEGID. All rights reserved.
            """
            
            # Create message
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject='Reset Your LEGID Password',
                plain_text_content=Content('text/plain', text_content),
                html_content=Content('text/html', html_content)
            )
            
            # Send
            response = self.client.send(message)
            
            if response.status_code in [200, 202]:
                logger.info(f"[SUCCESS] Password reset email sent to {to_email} via SendGrid")
                logger.info(f"SendGrid Status: {response.status_code}")
                return True
            else:
                logger.error(f"SendGrid returned status: {response.status_code}")
                logger.error(f"Response: {response.body}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send password reset email via SendGrid: {e}")
            logger.info(f"Reset link (fallback): {reset_link}")
            return False
    
    def send_welcome_email(
        self,
        to_email: str,
        user_name: Optional[str] = None
    ) -> bool:
        """Send welcome email to new users via SendGrid."""
        try:
            if not self.client:
                logger.info("=" * 80)
                logger.info("WELCOME EMAIL (Demo Mode - SendGrid not configured)")
                logger.info("=" * 80)
                logger.info(f"To: {to_email}")
                logger.info(f"Name: {user_name}")
                logger.info("=" * 80)
                return False
            
            # HTML email
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #1f2937; background: #f9fafb; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%); color: white; padding: 50px 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 36px; font-weight: 800; }}
        .content {{ padding: 40px 30px; }}
        .feature {{ background: #f3f4f6; padding: 15px 20px; margin: 15px 0; border-left: 4px solid #06b6d4; }}
        .button {{ display: inline-block; padding: 16px 32px; background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%); color: white; text-decoration: none; border-radius: 8px; font-weight: 600; }}
        .footer {{ background: #f9fafb; padding: 30px; text-align: center; color: #6b7280; font-size: 14px; border-top: 1px solid #e5e7eb; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚖️ Welcome to LEGID!</h1>
            <p style="margin: 10px 0 0;">Your Legal AI Assistant</p>
        </div>
        <div class="content">
            <h2>Hello{' ' + user_name if user_name else ''}! 👋</h2>
            
            <p>Thank you for joining <strong>LEGID</strong> - your intelligent legal assistant powered by AI.</p>
            
            <p><strong>You now have access to:</strong></p>
            
            <div class="feature">
                <strong>💬 AI Legal Chat</strong><br>
                Get instant answers with real case law citations
            </div>
            
            <div class="feature">
                <strong>📄 Document Analysis</strong><br>
                Upload PDFs and images with OCR
            </div>
            
            <div class="feature">
                <strong>🏛️ Court Lookup</strong><br>
                Find court information by jurisdiction
            </div>
            
            <div class="feature">
                <strong>📚 Case Citations</strong><br>
                References to similar legal precedents
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="http://localhost:4200" class="button">Start Using LEGID</a>
            </div>
            
            <p style="color: #6b7280; font-size: 14px;">
                <strong>Remember:</strong> LEGID provides general legal information, not legal advice. 
                For advice specific to your situation, consult a licensed lawyer.
            </p>
        </div>
        <div class="footer">
            <p><strong>Welcome to the future of legal assistance! 🚀</strong></p>
            <p>© 2026 LEGID. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """
            
            text_content = f"""
Welcome to LEGID!

Hello{' ' + user_name if user_name else ''}!

Thank you for joining LEGID - your intelligent legal assistant powered by AI.

You now have access to:
• AI Legal Chat - Get instant answers with real case law citations
• Document Analysis - Upload PDFs and images with OCR
• Court Lookup - Find court information by jurisdiction
• Case Citations - References to similar legal precedents

Get Started: http://localhost:4200

© 2026 LEGID. All rights reserved.
            """
            
            # Create message
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject='Welcome to LEGID - Your Legal AI Assistant',
                plain_text_content=Content('text/plain', text_content),
                html_content=Content('text/html', html_content)
            )
            
            # Send
            response = self.client.send(message)
            
            if response.status_code in [200, 202]:
                logger.info(f"[SUCCESS] Welcome email sent to {to_email} via SendGrid")
                return True
            else:
                logger.error(f"SendGrid error: Status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send welcome email via SendGrid: {e}")
            return False


# Singleton
_sendgrid_service: Optional[SendGridEmailService] = None


def get_sendgrid_service() -> SendGridEmailService:
    """Get singleton SendGrid service."""
    global _sendgrid_service
    if _sendgrid_service is None:
        _sendgrid_service = SendGridEmailService()
    return _sendgrid_service
