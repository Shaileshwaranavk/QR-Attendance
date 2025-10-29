import os
import qrcode
from datetime import datetime


def generate_session_qr(subject_code, session_id, topic, class_date, start_time):
    """
    Generates a QR code for a class session.
    The QR encodes: subject_code,session_id,topic,class_date,start_time
    and stores it in 'media/qrcodes/'.
    """
    try:
        # ✅ Ensure directory exists
        folder = "media/qrcodes"
        os.makedirs(folder, exist_ok=True)

        # ✅ Prepare data string
        qr_data = f"{subject_code},{session_id},{topic},{class_date},{start_time}"

        # ✅ Generate QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # ✅ Save file
        filename = f"{subject_code}_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        file_path = os.path.join(folder, filename)
        img.save(file_path)

        print("✅ QR Code generated successfully!")
        print(f"📁 Saved at: {file_path}")
        print(f"🔹 Data encoded: {qr_data}")

        return file_path
    except Exception as e:
        print(f"❌ Error generating QR: {e}")
        return None
