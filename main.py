import os
import time
from datetime import datetime

from dotenv import load_dotenv

from gmail_service import (
    authenticate_google,
    authenticate_gmail,
    read_new_emails,
    send_email,
    extract_email_address,
    mark_as_read
)

from gemini_service import analyze_email

from sheets_service import (
    authenticate_sheets,
    append_to_sheet
)


load_dotenv()


def create_sheet_row(email, analysis, reply_status):
    """
    Creates one row for Google Sheets.

    Columns:
    A Timestamp
    B Name
    C Phone
    D Email
    E Order Number
    F Product
    G Request Type
    H Urgency
    I Review Status
    J Reply Status
    K Reply
    """

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    return [
        timestamp,
        analysis.name or "",
        analysis.phone or "",
        analysis.email or "",
        analysis.order_number or "",
        analysis.product or "",
        analysis.request_type,
        analysis.urgency,
        analysis.review_status,
        reply_status,
        analysis.reply or ""
    ]


def clean_reply(reply):
    """
    Cleans the Gemini-generated reply before sending it.

    Ensures proper line breaks and removes unnecessary
    whitespace.
    """

    if not reply:
        return None

    # Normalize different newline formats
    reply = reply.replace("\r\n", "\n")
    reply = reply.replace("\r", "\n")

    # Remove excessive spaces at line endings
    lines = []

    for line in reply.split("\n"):
        lines.append(line.strip())

    # Remove excessive blank lines
    cleaned_lines = []

    previous_blank = False

    for line in lines:

        if line == "":
            if not previous_blank:
                cleaned_lines.append("")

            previous_blank = True

        else:
            cleaned_lines.append(line)
            previous_blank = False

    reply = "\n".join(cleaned_lines).strip()

    return reply


def process_email(
    gmail_service,
    sheets_service,
    email
):
    """
    Process one incoming email.
    """

    print("\n" + "=" * 70)

    print("Processing email:")
    print("Subject:", email["subject"])
    print("From:", email["sender"])

   
    # GEMINI ANALYSIS
    

    try:

        analysis = analyze_email(
            subject=email["subject"],
            sender=email["sender"],
            body=email["body"]
        )

    except Exception as e:

        print("Gemini analysis failed:")
        print(e)

        # Leave email unread so it can be retried
        return

   
    # USE ACTUAL GMAIL SENDER EMAIL
    

    sender_email = extract_email_address(
        email["sender"]
    )

    # Gmail From address is authoritative
    analysis.email = sender_email

    
    # CLEAN GEMINI REPLY

    analysis.reply = clean_reply(
        analysis.reply
    )

    
    # PRINT ANALYSIS
    

    print("\nAI Analysis")
    print("-" * 40)

    print("Name:", analysis.name)
    print("Phone:", analysis.phone)
    print("Email:", analysis.email)
    print("Order Number:", analysis.order_number)
    print("Product:", analysis.product)
    print("Request Type:", analysis.request_type)
    print("Urgency:", analysis.urgency)
    print("Review Status:", analysis.review_status)

    print("\nGenerated Reply:")
    print("-" * 40)

    if analysis.reply:
        print(analysis.reply)
    else:
        print("No reply")

    
    # SEND REPLY

    reply_status = ""

    # SPAM
    if analysis.request_type == "Spam":

        reply_status = "Not sent - Spam"

        # Spam must never receive an automatic reply
        analysis.reply = None

        print("\nSpam detected.")
        print("No reply will be sent.")

    # UNCLEAR
    elif analysis.review_status == "Needs human review":

        reply_status = "Not sent - Needs human review"

        # Unclear emails must go to human review
        analysis.reply = None

        print("\nEmail is unclear.")
        print("No automatic reply will be sent.")

    # CLEAR
    else:

        recipient = analysis.email

        if recipient and analysis.reply:

            try:

                print("\nSending reply to:", recipient)

                send_email(
                    gmail_service,
                    recipient,
                    "Re: " + email["subject"],
                    analysis.reply
                )

                reply_status = "Sent"

                print("Reply sent successfully.")

            except Exception as e:

                reply_status = "Failed"

                print("Reply failed:")
                print(e)

        else:

            reply_status = "Not sent - No reply"

            print("No reply generated.")

    
    # SAVE TO GOOGLE SHEETS
    

    row = create_sheet_row(
        email,
        analysis,
        reply_status
    )

    try:

        append_to_sheet(
            sheets_service,
            row
        )

        print("\nSaved to Google Sheets.")

    except Exception as e:

        print("\nGoogle Sheets update failed:")
        print(e)

        print(
            "Email will remain unread so it can be retried."
        )

        return

    
    # MARK EMAIL AS READ

    try:

        mark_as_read(
            gmail_service,
            email["id"]
        )

        print("Email marked as read.")

    except Exception as e:

        print("Could not mark email as read:")
        print(e)

    print("=" * 70)


def main():

    print("=" * 70)
    print("DIGITEK AI CUSTOMER SUPPORT AUTOMATION")
    print("=" * 70)

    
    # GOOGLE AUTHENTICATION

    print("\nAuthenticating Google services...")

    creds = authenticate_google()

    gmail_service = authenticate_gmail()

    sheets_service = authenticate_sheets(creds)

    print("Authentication successful.")

    
    # POLL INTERVAL
    

    poll_interval = int(
        os.getenv("POLL_INTERVAL", "10")
    )

    print(
        f"\nChecking unread incoming emails every "
        f"{poll_interval} seconds."
    )

    print(
        "Maximum emails checked per cycle: 10"
    )

    print(
        "Waiting for incoming customer emails..."
    )

    
    # CONTINUOUS EMAIL MONITORING
    

    while True:

        try:

            emails = read_new_emails(
                gmail_service,
                max_results=10
            )

            if emails:

                print(
                    f"\nFound {len(emails)} unread email(s)."
                )

                for email in emails:

                    process_email(
                        gmail_service,
                        sheets_service,
                        email
                    )

            else:

                print(
                    "\nNo new unread emails."
                )

        except Exception as e:

            print(
                "\nError while checking emails:"
            )

            print(e)

        print(
            f"\nNext check in {poll_interval} seconds..."
        )

        time.sleep(poll_interval)


if __name__ == "__main__":
    main()