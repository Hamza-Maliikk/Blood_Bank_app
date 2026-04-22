from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.config import settings
from typing import List, Dict, Any
import logging
import asyncio
from pathlib import Path
from app.services.email_queue import get_email_queue

logger = logging.getLogger(__name__)

# Email template configuration
# Determine SSL/TLS settings based on port
use_ssl = settings.SMTP_PORT == 465
use_tls = settings.SMTP_PORT == 587

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USERNAME,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.FROM_EMAIL,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_STARTTLS=use_tls,
    MAIL_SSL_TLS=use_ssl,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

class EmailService:
    """Service for sending emails."""

    def __init__(self):
        self.fastmail = FastMail(conf)
        self.queue = get_email_queue()
        # Set this service instance in the queue
        self.queue.set_email_service(self)

    async def send_email(
        self,
        recipients: List[str],
        subject: str,
        body: str,
        subtype: str = "html"
    ) -> bool:
        """
        Enqueue an email to be sent asynchronously.
        This method returns immediately without blocking.
        """
        try:
            # Validate email configuration
            if not settings.SMTP_HOST or not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
                logger.error("Email configuration is incomplete. Check SMTP settings.")
                return False
            
            # Validate recipients
            if not recipients or not all(recipients):
                logger.error(f"Invalid recipients: {recipients}")
                return False
            
            # Enqueue the email task
            task_id = await self.queue.enqueue(
                recipients=recipients,
                subject=subject,
                body=body,
                subtype=subtype
            )
            logger.info(f"Email enqueued (task {task_id}) for {recipients}")
            return True
            
        except asyncio.QueueFull:
            logger.error(f"Email queue is full. Failed to enqueue email to {recipients}")
            return False
        except Exception as e:
            logger.error(f"Error enqueueing email to {recipients}: {str(e)}", exc_info=True)
            return False
    
    async def _send_email_direct(
        self,
        recipients: List[str],
        subject: str,
        body: str,
        subtype: str = "html"
    ) -> bool:
        """
        Internal method to send email directly (used by queue workers).
        This is the actual email sending implementation.
        """
        try:
            # Validate email configuration
            if not settings.SMTP_HOST or not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
                logger.error("Email configuration is incomplete. Check SMTP settings.")
                return False
            
            # Validate recipients
            if not recipients or not all(recipients):
                logger.error(f"Invalid recipients: {recipients}")
                return False
            
            message = MessageSchema(
                subject=subject,
                recipients=recipients,
                body=body,
                subtype=MessageType.html if subtype == "html" else MessageType.plain
            )
            
            await self.fastmail.send_message(message)
            logger.info(f"Email sent successfully to {recipients}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email to {recipients}: {str(e)}", exc_info=True)
            return False

    async def send_password_reset_email(self, email: str, new_password: str) -> bool:
        """Send password reset email with new password."""
        try:
            subject = "Password Reset - BloodBank"
            
            body = f"""
            <html>
                <body>
                    <h2>Password Reset</h2>
                    <p>You requested a password reset for your BloodBank account.</p>
                    <p>Your new password is:</p>
                    <p><strong>{new_password}</strong></p>
                    <p>Please log in with this password and change it immediately.</p>
                    <br>
                    <p>Best regards,</p>
                    <p>BloodBank Team</p>
                </body>
            </html>
            """
            
            return await self.send_email([email], subject, body)
            
        except Exception as e:
            logger.error(f"Error sending password reset email: {e}")
            return False

    async def send_request_notification_to_donor(
        self, 
        donor_email: str, 
        donor_name: str,
        patient_name: str,
        blood_group: str,
        city: str,
        request_id: str
    ) -> bool:
        """Send email notification to donor about a new request."""
        try:
            subject = f"Urgent: {blood_group} Blood Needed in {city}"
            
            body = f"""
            <html>
                <body>
                    <h2>New Blood Request</h2>
                    <p>Hello {donor_name},</p>
                    <p>A new blood request has been created that matches your profile.</p>
                    <ul>
                        <li><strong>Patient Name:</strong> {patient_name}</li>
                        <li><strong>Blood Group:</strong> {blood_group}</li>
                        <li><strong>City:</strong> {city}</li>
                    </ul>
                    <p>Someone is counting on your help. Please check the app for more details.</p>
                    <br>
                    <p>Best regards,</p>
                    <p>BloodBank Team</p>
                </body>
            </html>
            """
            
            return await self.send_email([donor_email], subject, body)
            
        except Exception as e:
            logger.error(f"Error sending request notification email: {e}")
            return False

    async def send_request_accepted_notification(
        self,
        requester_email: str,
        requester_name: str,
        donor_name: str,
        request_id: str
    ) -> bool:
        """Send email notification to requester that a donor accepted."""
        try:
            subject = "Good News: A Donor has Accepted your Request!"
            
            body = f"""
            <html>
                <body>
                    <h2>Request Accepted</h2>
                    <p>Hello {requester_name},</p>
                    <p>Great news! <strong>{donor_name}</strong> has accepted your blood request.</p>
                    <p>Please coordinate with the donor through the application.</p>
                    <br>
                    <p>Best regards,</p>
                    <p>BloodBank Team</p>
                </body>
            </html>
            """
            
            return await self.send_email([requester_email], subject, body)
            
        except Exception as e:
            logger.error(f"Error sending acceptance notification email: {e}")
            return False
