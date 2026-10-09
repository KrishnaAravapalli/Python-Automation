# Python Automation for Customer Support

## Overview

This project is an AI-powered customer support email automation system built using Python and Google Gemini. It automates the process of analyzing customer emails, classifying requests, extracting important information, and organizing the results in Google Sheets.

The goal is to reduce manual work, improve response organization, and help customer support teams handle incoming emails more efficiently.

## Features

- **Email Classification:** Categorizes customer emails into:
  - Order Status
  - Return/Refund
  - Product Question
  - Bulk Order
  - Complaint
  - Spam

- **Information Extraction:** Extracts available customer details, including:
  - Customer name
  - Phone number
  - Email address
  - Order number
  - Product name
  - Urgency level

- **AI-Powered Analysis:** Uses Google Gemini to understand email content and generate structured results.

- **Google Sheets Integration:** Stores extracted information and classification results in a structured spreadsheet for easy tracking and review.

- **Urgency Detection:** Identifies high-priority requests that may require faster attention.

- **Structured Output:** Organizes email information into consistent fields for easier management.

## Technology Stack

- **Programming Language:** Python
- **AI Model/API:** Google Gemini API
- **Data Storage:** Google Sheets API
- **Environment Management:** Python virtual environment
- **Configuration:** Environment variables using `python-dotenv`

## Workflow

1. Receive or retrieve a customer support email.
2. Process the email content using Python.
3. Send the relevant email text to Google Gemini for analysis.
4. Classify the request and extract available customer details.
5. Identify the urgency level.
6. Validate and organize the extracted information.
7. Store the results in Google Sheets for customer support review.

## Project Structure

```text
Python-Automation/
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

*Adjust the filenames above to match the actual files in your repository.*

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

Replace the repository URL with your own GitHub repository URL.

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project directory and add the required API configuration:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Add any other credentials required by your implementation. Never commit your `.env` file or private credentials to GitHub.

### 5. Configure Google Sheets access

Enable the required Google Sheets API and configure the authentication method used by your project. Make sure the Google account or service account has the required spreadsheet permissions.

### 6. Run the automation

```bash
python main.py
```

Use the actual Python entry-point filename if it differs from `main.py`.

## Expected Output

For each processed email, the system aims to produce structured information such as:

| Field | Description |
|---|---|
| Request Type | Category assigned to the email |
| Customer Name | Extracted name, if available |
| Phone Number | Extracted phone number, if available |
| Email Address | Customer's email address |
| Order Number | Order reference, if available |
| Product | Product mentioned in the email |
| Urgency | Priority assigned to the request |

The extracted information is recorded in Google Sheets when the integration is configured successfully.

## Limitations and Future Improvements

- Improve accuracy when emails contain ambiguous or incomplete information.
- Add duplicate email detection and error logging.
- Introduce confidence-based human review for uncertain classifications.
- Integrate with authorized order-management systems to verify order status.
- Add controlled email replies with human approval.
- Expand testing across different email formats and customer scenarios.

## Security

- API keys and credentials must be stored in environment variables.
- Private credentials, access tokens, and real customer emails should not be uploaded to the repository.
- Customer data should be handled securely and only accessed with appropriate authorization.

## Disclaimer

This project demonstrates AI-assisted customer support automation. Actual capabilities depend on the configured APIs, authentication permissions, and connected services. Order verification, refund processing, and automatic email replies require additional integrations if they are not already implemented.

## Author

Developed as a Python automation project exploring AI-powered email classification, information extraction, and customer support workflow optimization.
