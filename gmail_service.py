import os
import base64
from email.message import EmailMessage
from email.utils import parseaddr

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/spreadsheets"
]




def authenticate_google():

    creds = None

    if os.path.exists("token.json"):

        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:

            creds.refresh(Request())

        else:

            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )

            creds = flow.run_local_server(
                port=0
            )

        with open("token.json", "w") as token:

            token.write(
                creds.to_json()
            )

    return creds



# GMAIL AUTHENTICATION


def authenticate_gmail():

    creds = authenticate_google()

    return build(
        "gmail",
        "v1",
        credentials=creds
    )



# EXTRACT EMAIL BODY


def get_email_body(payload):

    
    # Direct body
    

    if "body" in payload:

        data = payload["body"].get("data")

        if data:

            return base64.urlsafe_b64decode(
                data
            ).decode(
                "utf-8",
                errors="ignore"
            )

  
    # Multipart body

    if "parts" in payload:

        for part in payload["parts"]:

            mime_type = part.get(
                "mimeType",
                ""
            )

            # Prefer plain text
            if mime_type == "text/plain":

                data = part.get(
                    "body",
                    {}
                ).get("data")

                if data:

                    return base64.urlsafe_b64decode(
                        data
                    ).decode(
                        "utf-8",
                        errors="ignore"
                    )

            # Recursively search nested parts
            if "parts" in part:

                body = get_email_body(part)

                if body:

                    return body

    return ""


# GET EMAIL CONTENT

def get_email_content(
    service,
    message_id
):

    message = service.users().messages().get(
        userId="me",
        id=message_id,
        format="full"
    ).execute()

    payload = message.get(
        "payload",
        {}
    )

    headers = payload.get(
        "headers",
        []
    )

    subject = ""
    sender = ""

    for header in headers:

        name = header.get(
            "name",
            ""
        ).lower()

        value = header.get(
            "value",
            ""
        )

        if name == "subject":

            subject = value

        elif name == "from":

            sender = value

    body = get_email_body(
        payload
    )

    timestamp = message.get(
        "internalDate"
    )

    return {
        "id": message_id,
        "thread_id": message.get("threadId"),
        "subject": subject,
        "sender": sender,
        "body": body,
        "timestamp": timestamp
    }



# READ NEW UNREAD EMAILS


def read_new_emails(
    service,
    max_results=10
):

    results = service.users().messages().list(
        userId="me",
        q="is:unread -from:me",
        maxResults=max_results
    ).execute()

    messages = results.get(
        "messages",
        []
    )

    emails = []

    for message in messages:

        email = get_email_content(
            service,
            message["id"]
        )

        emails.append(
            email
        )

    return emails



# EXTRACT EMAIL ADDRESS

def extract_email_address(sender):

    name, email = parseaddr(
        sender
    )

    return email


# CLEAN OUTGOING EMAIL

def clean_email_body(body):

    if not body:
        return ""

    # Normalize different newline formats
    body = body.replace(
        "\r\n",
        "\n"
    )

    body = body.replace(
        "\r",
        "\n"
    )

    # Split into individual lines
    lines = body.split("\n")

    cleaned_lines = []

    for line in lines:

        # Remove unnecessary spaces
        cleaned_lines.append(
            line.strip()
        )

    # Remove excessive blank lines
    final_lines = []

    previous_blank = False

    for line in cleaned_lines:

        if line == "":

            if not previous_blank:

                final_lines.append("")

            previous_blank = True

        else:

            final_lines.append(line)

            previous_blank = False

    # Remove blank lines from beginning/end
    while final_lines and final_lines[0] == "":
        final_lines.pop(0)

    while final_lines and final_lines[-1] == "":
        final_lines.pop()

    return "\n".join(
        final_lines
    )


# SEND EMAIL

def send_email(
    service,
    recipient,
    subject,
    body
):

    # Clean and normalize the generated reply
    body = clean_email_body(
        body
    )

    message = EmailMessage()

    message["To"] = recipient

    message["Subject"] = subject

    # Explicit UTF-8 plain-text email
    message.set_content(
        body,
        subtype="plain",
        charset="utf-8"
    )

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    result = service.users().messages().send(
        userId="me",
        body={
            "raw": encoded_message
        }
    ).execute()

    return result



# MARK EMAIL AS READ


def mark_as_read(
    service,
    message_id
):

    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={
            "removeLabelIds": [
                "UNREAD"
            ]
        }
    ).execute()