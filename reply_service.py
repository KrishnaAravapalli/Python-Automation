def create_reply(analysis):

    name = analysis.name or "Customer"
    order_number = analysis.order_number or "your order"

    
    # ORDER STATUS
    
    if analysis.request_type == "Order status":

        return f"""Dear {name},

Thank you for contacting Digitek.

We have received your request regarding {order_number}. Our support team will check the current order and delivery status and get back to you as soon as possible.

Regards,
Digitek Support"""


    
    # RETURN / REFUND
    
    if analysis.request_type == "Return/Refund":

        return f"""Dear {name},

Thank you for contacting Digitek.

We have received your return/refund request regarding {order_number}. Our support team will review your request and get back to you with the next steps as soon as possible.

Regards,
Digitek Support"""


    
    # PRODUCT QUESTION
    
    if analysis.request_type == "Product question":

        return f"""Dear {name},

Thank you for contacting Digitek.

We have received your product enquiry. Our support team will review the requested product information and compatibility details and get back to you as soon as possible.

Regards,
Digitek Support"""


   
    # BULK ORDER
   
    if analysis.request_type == "Bulk order":

        return f"""Dear {name},

Thank you for your interest in Digitek.

We have received your bulk-order enquiry and noted your requirements. Our team will review the requested quantities and get back to you with the relevant pricing and further details as soon as possible.

Regards,
Digitek Support"""


    
    # COMPLAINT
   
    if analysis.request_type == "Complaint":

        return f"""Dear {name},

We sincerely apologize for the inconvenience you have experienced.

Your complaint has been received and our support team will review the issue on priority. We will get back to you as soon as possible with the next steps.

Regards,
Digitek Support"""


    
    # SPAM
    
    if analysis.request_type == "Spam":
        return None


    
    # UNKNOWN REQUEST TYPE
    
    return None