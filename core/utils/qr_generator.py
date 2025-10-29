import qrcode
from io import BytesIO
from django.http import HttpResponse

def generate_session_qr_response(subject_code, session_id, topic, class_date, start_time):
    """
    Generates and returns a QR code image (as HttpResponse with image/png).
    """
    qr_data = f"{subject_code},{session_id},{topic},{class_date},{start_time}"

    # Generate the QR
    qr_img = qrcode.make(qr_data)

    # Convert QR to bytes
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)

    # Return as image response
    response = HttpResponse(buffer.getvalue(), content_type="image/png")
    response["Content-Disposition"] = f'inline; filename="qr_{subject_code}_{session_id}.png"'
    return response
