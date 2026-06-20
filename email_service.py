"""
Email Service for AI Resume Screening System
Uses SMTP to send HTML emails at each pipeline stage.
Configure via environment variables or EMAIL_CONFIG dict.
"""

import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


import os
from dotenv import load_dotenv
load_dotenv()

# ==================== CONFIGURATION ====================
# Credentials loaded from .env file (see .env.example for setup)
# Guide: https://support.google.com/accounts/answer/185833
EMAIL_CONFIG = {
    'SMTP_SERVER': 'smtp.gmail.com',
    'SMTP_PORT': 587,
    'SMTP_USERNAME': os.environ.get('SMTP_USERNAME', ''),
    'SMTP_PASSWORD': os.environ.get('SMTP_PASSWORD', ''),
    'SENDER_EMAIL': os.environ.get('SMTP_USERNAME', ''),
    'SENDER_NAME': 'AI Resume Screening System',
    'ENABLED': True,
}


def _is_enabled():
    """Check if email sending is properly configured and enabled."""
    return (EMAIL_CONFIG['ENABLED']
            and EMAIL_CONFIG['SMTP_USERNAME']
            and EMAIL_CONFIG['SMTP_PASSWORD']
            and EMAIL_CONFIG['SENDER_EMAIL'])


# ==================== HTML TEMPLATE ====================
def _build_html(title, heading, body_html, accent_color='#6C63FF'):
    """Build a branded HTML email."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin:0;padding:0;background:#f4f4f9;font-family:'Segoe UI',Arial,sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f9;padding:30px 0;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">
                        <!-- Header -->
                        <tr>
                            <td style="background:linear-gradient(135deg, {accent_color}, #3B3694);padding:32px 40px;">
                                <h1 style="margin:0;color:#ffffff;font-size:22px;font-weight:600;">{heading}</h1>
                            </td>
                        </tr>
                        <!-- Body -->
                        <tr>
                            <td style="padding:32px 40px;color:#333333;font-size:15px;line-height:1.7;">
                                {body_html}
                            </td>
                        </tr>
                        <!-- Footer -->
                        <tr>
                            <td style="background:#fafafa;padding:20px 40px;text-align:center;border-top:1px solid #eee;">
                                <p style="margin:0;color:#999;font-size:12px;">
                                    AI Resume Screening System &bull; {datetime.now().strftime('%Y')}
                                </p>
                                <p style="margin:4px 0 0;color:#bbb;font-size:11px;">
                                    This is an automated email. Please do not reply directly.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


# ==================== SEND (ASYNC) ====================
def _send_email(to_email, subject, html_content):
    """Send an email via SMTP. Runs in a background thread to avoid blocking."""
    if not _is_enabled() or not to_email:
        return

    def _do_send():
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{EMAIL_CONFIG['SENDER_NAME']} <{EMAIL_CONFIG['SENDER_EMAIL']}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(html_content, 'html'))

            with smtplib.SMTP(EMAIL_CONFIG['SMTP_SERVER'], EMAIL_CONFIG['SMTP_PORT']) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(EMAIL_CONFIG['SMTP_USERNAME'], EMAIL_CONFIG['SMTP_PASSWORD'])
                server.sendmail(EMAIL_CONFIG['SENDER_EMAIL'], to_email, msg.as_string())

            print(f"[EMAIL] Sent to {to_email}: {subject}")
        except Exception as e:
            print(f"[EMAIL ERROR] Failed to send to {to_email}: {e}")

    thread = threading.Thread(target=_do_send, daemon=True)
    thread.start()


# ==================== PIPELINE EMAIL FUNCTIONS ====================

def send_selection_email(to_email, applicant_name, job_title, company):
    """Candidate selected for next round."""
    html = _build_html(
        title='Selected for Next Round',
        heading='🎉 Congratulations!',
        body_html=f"""
            <p>Dear <strong>{applicant_name}</strong>,</p>
            <p>Great news! You have been <strong>selected for the next round</strong> for the position of
            <strong>{job_title}</strong> at <strong>{company}</strong>.</p>
            <p>Please log in to your dashboard to answer the screening questions and move forward in the process.</p>
            <p style="margin-top:24px;">Best regards,<br><strong>{company} Hiring Team</strong></p>
        """,
        accent_color='#28a745'
    )
    _send_email(to_email, f"Selected for Next Round — {job_title} at {company}", html)


def send_rejection_email(to_email, applicant_name, job_title, company):
    """Candidate rejected."""
    html = _build_html(
        title='Application Update',
        heading='Application Update',
        body_html=f"""
            <p>Dear <strong>{applicant_name}</strong>,</p>
            <p>Thank you for your interest in the <strong>{job_title}</strong> position at <strong>{company}</strong>
            and for the time you invested in the application process.</p>
            <p>After careful consideration, we have decided to proceed with other candidates whose qualifications
            more closely align with our current needs.</p>
            <p>We encourage you to apply for future openings that match your profile.</p>
            <p style="margin-top:24px;">Warm regards,<br><strong>{company} Hiring Team</strong></p>
        """,
        accent_color='#6c757d'
    )
    _send_email(to_email, f"Application Update — {job_title} at {company}", html)


def send_interview_scheduled_email(to_email, applicant_name, job_title, company, date, time, interview_type='virtual', location='', additional_instructions=''):
    """Interview scheduled."""
    location_row = f'''
                <tr>
                    <td style="padding:8px 16px;background:#f0f0ff;font-weight:600;color:#555;">Location</td>
                    <td style="padding:8px 16px;background:#f8f8ff;">{location}</td>
                </tr>
    ''' if interview_type == 'in-person' else ''
    
    instructions_block = f'''
            <div style="margin-top: 20px; padding: 15px; background: #fff3cd; border-left: 4px solid #ffc107;">
                <strong style="color: #856404;">Additional Instructions:</strong>
                <p style="margin: 5px 0 0 0; color: #856404;">{additional_instructions}</p>
            </div>
    ''' if additional_instructions else ''
    
    join_text = '<p>Please log in to your dashboard to join the virtual interview room at the scheduled time.</p>' if interview_type == 'virtual' else '<p>We look forward to seeing you in person!</p>'
    
    html = _build_html(
        title='Interview Scheduled',
        heading='📅 Interview Scheduled',
        body_html=f"""
            <p>Dear <strong>{applicant_name}</strong>,</p>
            <p>Your interview for <strong>{job_title}</strong> at <strong>{company}</strong> has been scheduled.</p>
            <table style="margin:20px 0;border-collapse:collapse;">
                <tr>
                    <td style="padding:8px 16px;background:#f0f0ff;border-radius:6px 0 0 0;font-weight:600;color:#555;">Date</td>
                    <td style="padding:8px 16px;background:#f8f8ff;border-radius:0 6px 0 0;">{date}</td>
                </tr>
                <tr>
                    <td style="padding:8px 16px;background:#f0f0ff;border-radius:0 0 0 6px;font-weight:600;color:#555;">Time</td>
                    <td style="padding:8px 16px;background:#f8f8ff;border-radius:0 0 6px 0;">{time}</td>
                </tr>
                {location_row}
            </table>
            {instructions_block}
            {join_text}
            <p style="margin-top:24px;">Best regards,<br><strong>{company} Hiring Team</strong></p>
        """,
        accent_color='#0d6efd'
    )
    _send_email(to_email, f"Interview Scheduled — {job_title} at {company}", html)


def send_interview_rescheduled_email(to_email, applicant_name, job_title, company, old_date, old_time, new_date, new_time, recruiter_name, interview_type='virtual', location='', additional_instructions=''):
    """Interview rescheduled."""
    location_text = f"<p><strong>Location:</strong> {location}</p>" if interview_type == 'in-person' else "<p><strong>Type:</strong> Virtual</p>"
    
    instructions_block = f'''
            <div style="margin-top: 20px; padding: 15px; background: #fff3cd; border-left: 4px solid #ffc107;">
                <strong style="color: #856404;">Additional Instructions:</strong>
                <p style="margin: 5px 0 0 0; color: #856404;">{additional_instructions}</p>
            </div>
    ''' if additional_instructions else ''
    
    html = _build_html(
        title='Interview Rescheduled',
        heading='🔄 Interview Rescheduled',
        body_html=f"""
            <p>Dear <strong>{applicant_name}</strong>,</p>
            <p>Your interview for <strong>{job_title}</strong> at <strong>{company}</strong> has been
            rescheduled by <strong>{recruiter_name}</strong>.</p>
            <table style="margin:20px 0;border-collapse:collapse;width:100%;">
                <tr>
                    <td style="padding:8px 16px;background:#fff3cd;font-weight:600;color:#856404;">Previous</td>
                    <td style="padding:8px 16px;background:#fff9e6;text-decoration:line-through;color:#999;">{old_date} at {old_time}</td>
                </tr>
                <tr>
                    <td style="padding:8px 16px;background:#d4edda;font-weight:600;color:#155724;">New</td>
                    <td style="padding:8px 16px;background:#e8f5e9;font-weight:600;">{new_date} at {new_time}</td>
                </tr>
            </table>
            {location_text}
            {instructions_block}
            <p>Please update your calendar accordingly.</p>
            <p style="margin-top:24px;">Best regards,<br><strong>{company} Hiring Team</strong></p>
        """,
        accent_color='#fd7e14'
    )
    _send_email(to_email, f"Interview Rescheduled — {job_title} at {company}", html)


def send_interview_completed_email(to_email, applicant_name, job_title, company):
    """Interview feedback submitted / completed."""
    html = _build_html(
        title='Interview Completed',
        heading='🎤 Interview Completed',
        body_html=f"""
            <p>Dear <strong>{applicant_name}</strong>,</p>
            <p>Your interview for <strong>{job_title}</strong> at <strong>{company}</strong> has been completed.</p>
            <p>The hiring team is reviewing the results. You will be notified of the outcome soon.</p>
            <p style="margin-top:24px;">Best regards,<br><strong>{company} Hiring Team</strong></p>
        """,
        accent_color='#6C63FF'
    )
    _send_email(to_email, f"Interview Completed — {job_title} at {company}", html)


def send_hired_email(to_email, applicant_name, job_title, company):
    """Candidate hired."""
    html = _build_html(
        title='You are Hired!',
        heading='🎉 Congratulations — You Are Hired!',
        body_html=f"""
            <p>Dear <strong>{applicant_name}</strong>,</p>
            <p>We are thrilled to inform you that you have been <strong>officially hired</strong> for the position of
            <strong>{job_title}</strong> at <strong>{company}</strong>!</p>
            <p style="font-size:20px;text-align:center;margin:24px 0;">🎊 Welcome aboard! 🎊</p>
            <p>The team will reach out shortly with onboarding details. We look forward to working with you.</p>
            <p style="margin-top:24px;">Warm regards,<br><strong>{company} Hiring Team</strong></p>
        """,
        accent_color='#28a745'
    )
    _send_email(to_email, f"🎉 You're Hired — {job_title} at {company}", html)


def send_questions_answered_email(to_email, recruiter_name, applicant_name, job_title):
    """Notify recruiter that applicant answered screening questions."""
    html = _build_html(
        title='Screening Questions Answered',
        heading='📋 Screening Responses Submitted',
        body_html=f"""
            <p>Hi <strong>{recruiter_name}</strong>,</p>
            <p><strong>{applicant_name}</strong> has submitted their answers to the screening questions
            for <strong>{job_title}</strong>.</p>
            <p>Log in to your dashboard to review the responses and schedule an interview.</p>
        """,
        accent_color='#17a2b8'
    )
    _send_email(to_email, f"Screening Answers Submitted — {applicant_name} for {job_title}", html)
