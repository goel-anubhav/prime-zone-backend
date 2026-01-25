from datetime import datetime

def confirmation_email_template(name: str, message: str) -> str:
    """
    Generates an attractive HTML email template for user confirmation.
    """
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>We Received Your Enquiry</title>
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
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
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
            .content {{
                padding: 32px;
            }}
            .greeting {{
                font-size: 16px;
                margin-bottom: 24px;
                color: #334155;
            }}
            .message-copy {{
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 24px;
                margin-bottom: 24px;
                font-style: italic;
                color: #64748b;
            }}
            .footer {{
                background-color: #f1f5f9;
                padding: 24px;
                text-align: center;
                font-size: 12px;
                color: #94a3b8;
                border-top: 1px solid #e2e8f0;
            }}
            .button {{
                display: inline-block;
                padding: 12px 24px;
                background-color: #10b981;
                color: #ffffff;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 600;
                margin-top: 16px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Thank You for Contacting Us</h2>
            </div>
            
            <div class="content">
                <div class="greeting">
                    <strong>Hi {name},</strong><br><br>
                    We have received your enquiry and our team will get back to you shortly.
                </div>

                <p style="color: #64748b; margin-bottom: 8px; font-size: 14px; font-weight: 600;">Here is a copy of your message:</p>
                <div class="message-copy">
                    "{message}"
                </div>

                <div style="text-align: center;">
                    <a href="https://primezone.media" class="button">Visit Our Website</a>
                </div>
            </div>

            <div class="footer">
                <p>&copy; {datetime.now().year} Prime Zone Media. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html
