import smtplib, ssl
from pathlib import Path
import environ
import os


BASE_DIR = Path(__file__).resolve().parent.parent
env_file = os.path.join(BASE_DIR, ".env")
environ.Env.read_env(env_file)
env = os.environ


def mail_send(plan_name, receiver_email):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = env.get("EMAIL_HOST_USER")
    message = """\
            Subject: Plan subscription

            Hello!
            
            You have successfully subscribed to the """ + plan_name + """ plan."""
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, env.get("EMAIL_HOST_PASSWORD"))
        server.sendmail(sender_email, receiver_email, message)