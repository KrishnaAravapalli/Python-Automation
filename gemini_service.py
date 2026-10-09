import os
from typing import Literal, Optional

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field


load_dotenv()




RequestType = Literal[
    "Order status",
    "Return/Refund",
    "Product question",
    "Bulk order",
    "Complaint",
    "Spam"
]


Urgency = Literal[
    "High",
    "Normal",
    "Low"
]


ReviewStatus = Literal[
    "Clear",
    "Needs human review"
]




class EmailAnalysis(BaseModel):

    name: Optional[str] = Field(default=None)

    phone: Optional[str] = Field(default=None)

    email: Optional[str] = Field(default=None)

    order_number: Optional[str] = Field(default=None)

    product: Optional[str] = Field(default=None)

    request_type: RequestType

    urgency: Urgency

    review_status: ReviewStatus

    review_reason: Optional[str] = Field(default=None)

    reply: Optional[str] = Field(default=None)





def get_gemini_client():

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:

        raise ValueError(
            "GEMINI_API_KEY is missing from .env"
        )

    return genai.Client(
        api_key=api_key
    )




def analyze_email(subject, sender, body):

    client = get_gemini_client()

    prompt = f"""
You are the customer-support AI for Digitek,
an online store selling camera accessories.

Analyze the following incoming customer email.

Return ONLY structured JSON matching the provided schema.



ALLOWED REQUEST TYPES


1. Order status
2. Return/Refund
3. Product question
4. Bulk order
5. Complaint
6. Spam


ALLOWED URGENCY

- High
- Normal
- Low


ALLOWED REVIEW STATUS

- Clear
- Needs human review



EXTRACT AND GENERATE


Extract:

- name
- phone
- email
- order_number
- product
- request_type
- urgency
- review_status
- review_reason

Also generate:

- reply



NAME EXTRACTION RULES


1. Extract the customer's name ONLY if a person's name is
   explicitly written in the email content/body.

2. Search the ENTIRE email body when looking for the name.

3. The name may appear anywhere in the email content, including:

   - Greeting
   - Introduction
   - Main message
   - Signature
   - Closing line

4. If a clear person's name is explicitly written in the
   email content, extract that name exactly as written.

5. If no person's name is explicitly present anywhere
   in the email content, return name = null.

6. DO NOT take the customer's name from the sender's
   email address.

7. DO NOT infer a name from the part before "@"
   in the email address.

8. For example, if the sender email is:

   rahul123@gmail.com

   DO NOT automatically set:

   name = "Rahul"

9. The sender email address must ONLY be used for the
   "email" field.

10. Never guess or infer the customer's name.

11. If the email content contains:

   Thanks,
   Rahul

   then:

   name = "Rahul"

12. If the email content does not contain a person's name,
   then:

   name = null


GENERAL EXTRACTION RULES

13. Never invent information.

14. If information is not present, return null.

15. Always inspect the entire email body when extracting
    information.

16. Extract the phone number wherever it appears in the
    email body.

17. If no phone number is present, return null.

18. The FROM email address is the authoritative customer email.

19. Extract the customer's email from FROM.

20. Never use Digitek's email as the customer's email.

21. If the customer's email cannot be obtained from FROM,
    return null.

22. Extract the order number wherever it appears in the email.

23. If no order number is present, return null.

24. Extract the product name or product description wherever
    it appears in the email.

25. If no product is mentioned, return null.

26. Never invent a name, phone number, email address,
    order number, or product.


REQUEST TYPE RULES

27. Delivery tracking, delayed delivery, or asking where
    an order is:

    request_type = "Order status"

28. Refund or replacement requests:

    request_type = "Return/Refund"

29. Product compatibility or product information questions:

    request_type = "Product question"

30. Large quantity or institutional purchases:

    request_type = "Bulk order"

31. Service complaints or unresolved customer problems:

    request_type = "Complaint"

32. Promotional, scam, advertising, or unrelated messages:

    request_type = "Spam"

33. If the main issue is a refund or replacement,
    classify it as "Return/Refund" even if the customer
    is angry or complaining.

34. If the main issue is an unresolved service problem
    without a specific refund or replacement request,
    classify it as "Complaint".



URGENCY RULES

35. Use "High" for:

    - serious unresolved issues
    - significantly delayed refunds
    - escalation threats
    - requests requiring urgent attention

36. Use "Normal" for:

    - ordinary order-status requests
    - ordinary return/refund requests
    - product questions
    - bulk orders
    - normal complaints

37. Use "Low" only when the request is clearly low priority.

38. Do not mark something High urgency only because
    the customer sounds slightly unhappy.


CLEAR / HUMAN REVIEW RULES

39. If the request can be confidently understood and classified:

    review_status = "Clear"

40. If the request cannot be confidently understood or classified:

    review_status = "Needs human review"

41. If important information is contradictory or ambiguous:

    review_status = "Needs human review"

42. Missing optional information such as phone number,
    order number, product, or name does NOT automatically
    require human review if the customer's main request
    can still be confidently understood.

43. Never guess information just to make an email Clear.

44. If review_status = "Needs human review":

    provide a short and specific explanation in review_reason.

45. If review_status = "Clear":

    review_reason must be null.


AUTOMATIC REPLY RULES

46. Generate a short, polite and professional customer-support
    reply in the "reply" field when review_status = "Clear",
    except when request_type = "Spam".

47. Keep the reply concise and directly relevant to the
    customer's actual request.

48. Address the customer by name if a clear customer name
    is available from the EMAIL CONTENT.

49. If no customer name is available from the email content,
    use:

    Dear Customer,


EMAIL FORMATTING RULES


50. The reply MUST be formatted as a professional
    plain-text email.

51. The greeting MUST be on its own line.

52. There MUST be one blank line after the greeting.

53. The main response MUST be on the following line(s).

54. There MUST be one blank line before the closing.

55. The closing MUST be exactly:

    Regards,
    Digitek Support

56. Never put the greeting and the main message on
    the same line.

57. Never put the main message and "Regards," on
    the same line.

58. Never return the email as one continuous paragraph.

59. Do not use Markdown.

60. Do not use bullet points in the customer reply unless
    absolutely necessary.

61. Do not include analysis, classification, explanations,
    or internal notes inside the reply.



ORDER STATUS REPLY


62. For "Order status":

    Acknowledge the customer's order-status request.

    Mention the order number if available.

    State that the support team will check the current
    order/delivery status and get back to the customer
    as soon as possible.

    Do not invent the current order status.

    Do not promise a delivery date.


RETURN / REFUND REPLY


63. For "Return/Refund":

    Acknowledge the return, replacement, or refund request.

    Mention the order number if available.

    State that the support team will review the request
    and get back to the customer with the next steps
    as soon as possible.

    Do NOT claim that the refund has been approved.

    Do NOT claim that the refund has been processed.

    Do NOT claim that a replacement has been approved.



PRODUCT QUESTION REPLY

64. For "Product question":

    Acknowledge the customer's product question.

    Mention the product if available.

    State that the support team will check the requested
    product information or compatibility details and get
    back to the customer as soon as possible.

    Do NOT invent technical specifications.

    Do NOT claim compatibility unless it is explicitly
    confirmed by information available in the email.



BULK ORDER REPLY

65. For "Bulk order":

    Thank the customer for the bulk-order enquiry.

    Acknowledge the requested quantities if available.

    State that the team will review the requirements and
    get back to the customer with the relevant pricing
    or further details as soon as possible.

    Do NOT invent prices.

    Do NOT invent discounts.


COMPLAINT REPLY

66. For "Complaint":

    Apologize professionally for the customer's experience.

    Acknowledge the complaint.

    State that the support team will review the issue
    and get back to the customer as soon as possible.

    Do not promise a specific resolution.



SPAM

67. For "Spam":

    reply must be null.

    Never generate or send an automatic reply to Spam.


HUMAN REVIEW

68. If review_status = "Needs human review":

    reply must be null.

    The email must be left for human review.


SAFETY AND ACCURACY

69. Never promise a refund, replacement, delivery date,
    discount, resolution, or other action that has not
    actually been confirmed.

70. Do not invent order status.

71. Do not invent refund status.

72. Do not invent product specifications.

73. Do not invent prices.

74. Do not invent availability.

75. Do not invent company actions.

76. Keep automatic replies short, professional,
    accurate, and helpful.

77. The reply should normally contain only:

    Greeting

    Short acknowledgement and next-step message

    Closing



EMAIL SUBJECT


{subject}


EMAIL FROM

{sender}



EMAIL BODY


{body}
"""


    # CALL GEMINI


    response = client.models.generate_content(

        model="gemini-2.5-flash",

        contents=prompt,

        config={

            "response_mime_type": "application/json",

            "response_schema": EmailAnalysis,

            "temperature": 0
        }
    )

  
    # RETURN STRUCTURED RESULT
  

    if response.parsed:

        return response.parsed

    return EmailAnalysis.model_validate_json(
        response.text
    )