from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import get_settings, get_logger
from .template import contact_email_template
from .response_mail import confirmation_email_template
from app.db.schema import BaseOutput

router = APIRouter()
settings = get_settings()
logger = get_logger()

class ContactRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    message: Optional[str] = None
    subject: Optional[str] = "New Contact Enquiry"

def send_email_task(name: str, email: str, phone: str, message: str, subject: str):
    try:
        sender_email = settings.EMAIL
        sender_password = settings.PASSWORD
        smtp_server = settings.SMTP_URL
        smtp_port = settings.SMTP_PORT
        
        # Determine recipients
        # Splitting ADMIN_EMAIL by comma if multiple admins are provided
        recipients = ["testanubhav80@gmail.com"]
        if settings.ADMIN_EMAIL:
            recipients.extend([e.strip() for e in settings.ADMIN_EMAIL.split(',')])
        
        # Also include the sender email as recipient if desired, or if ADMIN_EMAIL is empty
        if not recipients and sender_email:
            recipients.append(sender_email)
            
        if not recipients:
            logger.error("No recipients defined for contact email.")
            return

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = f"Prime Zone Media Contact: {subject}"

        html_body = contact_email_template(name, email, phone, message, subject)
        msg.attach(MIMEText(html_body, 'html'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipients, msg.as_string())
        server.quit()
        
        logger.info(f"Contact email sent successfully to {recipients}")

        # Send to User (Confirmation)
        if email and email != "N/A":
             msg_user = MIMEMultipart()
             msg_user['From'] = sender_email
             msg_user['To'] = email
             msg_user['Subject'] = f"We Received Your Enquiry - Prime Zone Media"
             
             html_user = confirmation_email_template(name, message)
             msg_user.attach(MIMEText(html_user, 'html'))
             
             server = smtplib.SMTP(smtp_server, smtp_port)
             server.starttls()
             server.login(sender_email, sender_password)
             server.sendmail(sender_email, email, msg_user.as_string())
             server.quit()
             logger.info(f"Confirmation email sent to {email}")
        
    except Exception as e:
        logger.error(f"Failed to send contact email: {str(e)}")

@router.post("/", response_model=BaseOutput)
async def contact_us(
    contact_data: ContactRequest,
    background_tasks: BackgroundTasks
):
    # Prepare data, defaulting to "N/A" if None
    name = contact_data.name or "N/A"
    email = contact_data.email or "N/A"
    phone = contact_data.phone or "N/A"
    message = contact_data.message or "N/A"
    subject = contact_data.subject or "New Contact Enquiry"
    
    # Send email in background to not block the response
    background_tasks.add_task(send_email_task, name, email, phone, message, subject)
    
    return BaseOutput(message="Enquiry received", detail="Your message has been sent to our team.")
