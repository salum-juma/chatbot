import requests
import logging
from base64 import b64encode


def send_sms(phone, message):
    return True
    try:
        # Clean phone number: remove non-digits
        phone = ''.join(filter(str.isdigit, phone))

        # Handle Tanzania country code prefix '255'
        if phone.startswith('0'):
            phone = '255' + phone[1:]
        if not phone.startswith('255'):
            phone = '255' + phone

        username = "developer_nkya"
        password = "123123@1"

        url = "https://messaging-service.co.tz/api/sms/v1/text/single"
        post_data = {
            "from": "SCHOOL",
            "to": phone,
            "text": message,
        }

        # Prepare HTTP Basic Auth header
        credentials = f"{username}:{password}"
        encoded_credentials = b64encode(credentials.encode('utf-8')).decode('utf-8')
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {encoded_credentials}",
        }

        response = requests.post(url, json=post_data, headers=headers)

        if response.ok:
            logging.info(f"SMS sent successfully to {phone}: {response.text}")
            return True
        else:
            logging.error(f"Failed to send SMS to {phone}: {response.status_code} {response.text}")
            return False

    except Exception as e:
        logging.error(f"Exception while sending SMS: {str(e)}")
        return False
