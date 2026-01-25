def contact_email_template(name: str, email: str, phone: str, message: str, subject: str) -> str:
    """
    Generates an attractive HTML email template for contact form submissions.
    """
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>New Contact Enquiry</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background-color: #f4f7fa;
                margin: 0;
                padding: 0;
                line-height: 1.6;
                color: #1a202c;
            }}
            .container {{
                max_width: 600px;
                margin: 40px auto;
                background-color: #ffffff;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05), 0 10px 15px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                color: #ffffff;
                padding: 30px;
                text-align: center;
            }}
            .header h2 {{
                margin: 0;
                font-size: 24px;
                font-weight: 700;
                letter-spacing: -0.025em;
            }}
            .subheader {{
                margin-top: 8px;
                font-size: 14px;
                color: #94a3b8;
                font-weight: 500;
            }}
            .content {{
                padding: 32px;
            }}
            .greeting {{
                font-size: 16px;
                margin-bottom: 24px;
                color: #475569;
            }}
            .info-card {{
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 24px;
                margin-bottom: 24px;
            }}
            .field-row {{
                margin-bottom: 16px;
                border-bottom: 1px solid #e2e8f0;
                padding-bottom: 16px;
            }}
            .field-row:last-child {{
                margin-bottom: 0;
                border-bottom: none;
                padding-bottom: 0;
            }}
            .label {{
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: #64748b;
                font-weight: 600;
                margin-bottom: 4px;
                display: block;
            }}
            .value {{
                font-size: 15px;
                color: #334155;
                font-weight: 500;
            }}
            .message-box {{
                background-color: #fff;
                border: 1px solid #e2e8f0;
                border-left: 4px solid #3b82f6;
                border-radius: 4px;
                padding: 16px;
                margin-top: 8px;
                font-size: 15px;
                color: #334155;
                white-space: pre-wrap;
            }}
            .footer {{
                background-color: #f1f5f9;
                padding: 24px;
                text-align: center;
                font-size: 12px;
                color: #94a3b8;
                border-top: 1px solid #e2e8f0;
            }}
            .footer p {{
                margin: 0;
            }}
            .priority-badge {{
                display: inline-block;
                padding: 4px 8px;
                background-color: #dbeafe;
                color: #1e40af;
                font-size: 12px;
                font-weight: 600;
                border-radius: 9999px;
                margin-bottom: 16px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>New Enquiry</h2>
                <div class="subheader">Prime Zone Media Smart Form</div>
            </div>
            
            <div class="content">
                <div class="greeting">
                    <strong>Hello Admin,</strong><br>
                    You have received a new contact request from your website. Here are the details:
                </div>

                <div class="info-card">
                    <div class="field-row">
                        <span class="label">Subject</span>
                        <div class="value">{subject}</div>
                    </div>
                
                    <div class="field-row">
                        <span class="label">Full Name</span>
                        <div class="value">{name}</div>
                    </div>
                    
                    <div class="field-row">
                        <span class="label">Email Address</span>
                        <div class="value">
                            <a href="mailto:{email}" style="color: #2563eb; text-decoration: none;">{email}</a>
                        </div>
                    </div>
                    
                    <div class="field-row">
                        <span class="label">Phone Number</span>
                        <div class="value">
                            <a href="tel:{phone}" style="color: #2563eb; text-decoration: none;">{phone}</a>
                        </div>
                    </div>
                </div>

                <div>
                    <span class="label" style="color: #64748b; margin-bottom: 8px;">Message Content</span>
                    <div class="message-box">
                        {message}
                    </div>
                </div>
            </div>

            <div class="footer">
                <p>&copy; {datetime.now().year} Prime Zone Media. All rights reserved.</p>
                <p style="margin-top: 8px;">This email was automatically generated by the Prime Zone Media system.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

from datetime import datetime
