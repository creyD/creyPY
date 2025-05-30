import os

import boto3
from botocore.exceptions import ClientError
from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

AWS_CLIENT_ID = os.getenv("AWS_CLIENT_ID")
AWS_CLIENT_SECRET = os.getenv("AWS_CLIENT_SECRET")
AWS_SENDER_EMAIL = os.getenv("AWS_SENDER_EMAIL")
AWS_REGION = os.getenv("AWS_REGION", "eu-central-1")


async def send_email_ses(recipient_email, subject, template, html_data):
    ses_client = boto3.client(
        "ses",
        aws_access_key_id=AWS_CLIENT_ID,
        aws_secret_access_key=AWS_CLIENT_SECRET,
        region_name=AWS_REGION,
    )

    html_body = await render_html_template(template, html_data)
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


async def render_html_template(template, data):
    jinja_env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR), autoescape=select_autoescape(["html", "xml"])
    )
    template = jinja_env.get_template(template)
    html_body = template.render(**data)
    return html_body
