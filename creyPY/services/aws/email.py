import os

import boto3
from botocore.exceptions import ClientError

AWS_CLIENT_ID = os.getenv("AWS_CLIENT_ID")
AWS_CLIENT_SECRET = os.getenv("AWS_CLIENT_SECRET")
AWS_SENDER_EMAIL = os.getenv("AWS_SENDER_EMAIL")
AWS_REGION = os.getenv("AWS_REGION", "eu-central-1")


async def send_email_ses(recipient_email, subject, html_body):
    ses_client = boto3.client(
        "ses",
        aws_access_key_id=AWS_CLIENT_ID,
        aws_secret_access_key=AWS_CLIENT_SECRET,
        region_name=AWS_REGION,
    )
    email_message = {
        "Source": AWS_SENDER_EMAIL,
        "Destination": {"ToAddresses": [recipient_email]},
        "Message": {
            "Subject": {"Data": subject, "Charset": "UTF-8"},
            "Body": {"Html": {"Data": html_body, "Charset": "UTF-8"}},
        },
    }

    try:
        response = ses_client.send_email(**email_message)
        return response["MessageId"]
    except ClientError as e:
        return None
