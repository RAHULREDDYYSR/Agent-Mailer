import smtplib
import os
import ssl
from email.message import EmailMessage
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

@tool
def send_email(recipient: str, subject: str, body: str, attachments: list[str] = None) -> str:
    """
    Sends an email to a recipient with a given subject and body using SMTP.
    
    Args:
        recipient: The email address of the recipient.
        subject: The subject of the email.
        body: The body text of the email.
        attachments: A list of file paths to attach to the email.
    """
    
    email_host = os.getenv("EMAIL_HOST")
    email_port = os.getenv("EMAIL_PORT")
    email_user = os.getenv("EMAIL_USER")
    email_password = os.getenv("EMAIL_PASSWORD")

    if not all([email_host, email_port, email_user, email_password]):
        return "Error: Missing email configuration in environment variables (EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD)."

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = email_user
    msg["To"] = recipient

    # Handle Attachments
    import mimetypes
    if attachments:
        for filepath in attachments:
            if not os.path.exists(filepath):
                print(f"Warning: Attachment not found at {filepath}")
                continue
            
            # Guess MIME type or default to binary
            ctype, encoding = mimetypes.guess_type(filepath)
            if ctype is None or encoding is not None:
                # No guess could be made, or the file is encoded (compressed), so
                # use a generic bag-of-bits type.
                ctype = 'application/octet-stream'
            
            maintype, subtype = ctype.split('/', 1)

            try:
                with open(filepath, 'rb') as f:
                    file_data = f.read()
                    filename = os.path.basename(filepath)
                    msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=filename)
            except Exception as e:
                return f"Error reading attachment {filepath}: {str(e)}"

    try:
        # Create a secure SSL context
        context = ssl.create_default_context()

        # Connect to the server
        # Try SSL first (default port 465)
        if email_port == '465':
            with smtplib.SMTP_SSL(email_host, int(email_port), context=context) as server:
                server.login(email_user, email_password)
                server.send_message(msg)
        # Try STARTTLS (default port 587)
        else:
             with smtplib.SMTP(email_host, int(email_port)) as server:
                server.starttls(context=context)
                server.login(email_user, email_password)
                server.send_message(msg)
        
        return "Email sent successfully!"

    except Exception as e:
        return f"Failed to send email: {str(e)}"

if __name__ == "__main__":
    # Test with dummy data if env vars are present, otherwise warn user
    if os.getenv("EMAIL_USER"):
        print(send_email.invoke({
            "recipient": 'rahulreddyysr7@gmail.com', # Send to self for testing
            "subject": "Test Email from LangChain Tool",
            "body": "This is a test email sent from the send_email tool."
        }))
    else:
        print("Please set EMAIL_HOST, EMAIL_PORT, EMAIL_USER, and EMAIL_PASSWORD in .env to test this file.")
