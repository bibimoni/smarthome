"""Email service for sending OTP and notifications."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime
from flask import current_app


class EmailService:
    """Service class for sending emails."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, smtp_server: str = None, smtp_port: int = None,
                 smtp_username: str = None, smtp_password: str = None,
                 email_from: str = None):
        """Initialize email service."""
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.email_from = email_from
        self._initialized = False
        
        if smtp_server and smtp_username:
            self._initialized = True
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance."""
        return cls._instance
    
    @classmethod
    def init_app(cls, app):
        """Initialize email service from Flask app config."""
        smtp_server = app.config.get('SMTP_SERVER')
        smtp_port = app.config.get('SMTP_PORT')
        smtp_username = app.config.get('SMTP_USERNAME')
        smtp_password = app.config.get('SMTP_PASSWORD')
        email_from = app.config.get('EMAIL_FROM')
        
        if smtp_server and smtp_username:
            service = cls(smtp_server, smtp_port, smtp_username, smtp_password, email_from)
            app.email_service = service
            return service
        return None
    
    def send_email(self, to_email: str, subject: str, body: str, 
                   html_body: str = None) -> bool:
        """
        Send an email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
            
        Returns:
            True if sent successfully
        """
        if not self._initialized:
            print("Email service not initialized")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_from
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add plain text part
            msg.attach(MIMEText(body, 'plain'))
            
            # Add HTML part if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Connect and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.email_from, to_email, msg.as_string())
            
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    def send_otp_email(self, to_email: str, otp: str, 
                       expires_at: datetime) -> bool:
        """
        Send OTP email for password reset.
        
        Args:
            to_email: Recipient email
            otp: One-time password
            expires_at: Expiration time
            
        Returns:
            True if sent successfully
        """
        subject = "YoloHome - Password Reset Code"
        
        body = f"""
Your password reset code is: {otp}

This code will expire at {expires_at.strftime('%Y-%m-%d %H:%M:%S')} UTC.

If you did not request this code, please ignore this email.

Best regards,
YoloHome Team
"""
        
        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background-color: #f5f5f5; padding: 20px; border-radius: 10px;">
        <h2 style="color: #333;">YoloHome Password Reset</h2>
        <p style="font-size: 16px;">Your password reset code is:</p>
        <div style="background-color: #fff; padding: 20px; border-radius: 5px; text-align: center;">
            <span style="font-size: 32px; font-weight: bold; color: #007bff; letter-spacing: 5px;">{otp}</span>
        </div>
        <p style="font-size: 14px; color: #666;">
            This code will expire at {expires_at.strftime('%Y-%m-%d %H:%M:%S')} UTC.
        </p>
        <p style="font-size: 12px; color: #999;">
            If you did not request this code, please ignore this email.
        </p>
    </div>
</body>
</html>
"""
        
        return self.send_email(to_email, subject, body, html_body)
    
    def send_welcome_email(self, to_email: str, name: str) -> bool:
        """
        Send welcome email to new user.
        
        Args:
            to_email: Recipient email
            name: User's name
            
        Returns:
            True if sent successfully
        """
        subject = "Welcome to YoloHome!"
        
        body = f"""
Welcome to YoloHome, {name}!

Thank you for registering with YoloHome - your smart home IoT solution.

You can now:
- Monitor your home environment in real-time
- Control devices remotely
- Set up automated rules and scenes
- Track activity history

Get started by logging into your account.

Best regards,
YoloHome Team
"""
        
        return self.send_email(to_email, subject, body)
    
    def send_alert_email(self, to_email: str, alert_title: str, 
                         alert_message: str) -> bool:
        """
        Send alert notification email.
        
        Args:
            to_email: Recipient email
            alert_title: Alert title
            alert_message: Alert message
            
        Returns:
            True if sent successfully
        """
        subject = f"YoloHome Alert: {alert_title}"
        
        body = f"""
YoloHome Alert: {alert_title}

{alert_message}

This is an automated message from YoloHome.

Best regards,
YoloHome Team
"""
        
        return self.send_email(to_email, subject, body)


# Global email service instance
email_service = None


def init_email(app):
    """Initialize email service from Flask app."""
    global email_service
    email_service = EmailService.init_app(app)
    return email_service