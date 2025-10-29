import cv2
import numpy as np
from pyzbar.pyzbar import decode as pyzbar_decode
from PIL import Image
import os

def scan_qr(image_input, student_id=None):
    """
    Scans and decodes QR code from an image file or uploaded file.
    Returns a dictionary with decoded data (subject_code, session_id, topic, date, time)
    or None if unsuccessful.

    Expected QR format:
        subject_code,session_id,topic,class_date,start_time
    """

    try:
        # ✅ Load the image properly
        if hasattr(image_input, "read"):  # Django uploaded file
            image = Image.open(image_input).convert("RGB")
        elif isinstance(image_input, str) and os.path.exists(image_input):  # File path
            image = Image.open(image_input).convert("RGB")
        else:
            print("❌ Invalid image input:", image_input)
            return None

        # ✅ Convert image for OpenCV decoding
        np_img = np.array(image)
        image_bgr = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)

        # ✅ Try OpenCV QR decoding first
        detector = cv2.QRCodeDetector()
        data, points, _ = detector.detectAndDecode(image_bgr)

        # ✅ If OpenCV fails, use Pyzbar
        if not data:
            decoded_objs = pyzbar_decode(image_bgr)
            if decoded_objs:
                data = decoded_objs[0].data.decode("utf-8")

        if not data:
            print("❌ No QR code detected or could not decode QR.")
            return None

        print(f"📦 Decoded QR Data: {data}")

        # ✅ Parse expected QR data format
        parts = data.split(",")
        if len(parts) < 5:
            print("⚠️ Invalid QR format. Expected 5 fields.")
            return None

        subject_code, session_id, topic, class_date, start_time = parts[:5]

        # ✅ Return structured result (you can directly use this in your view)
        result = {
            "subject_code": subject_code.strip(),
            "session_id": session_id.strip(),
            "topic": topic.strip(),
            "class_date": class_date.strip(),
            "start_time": start_time.strip(),
        }

        print(f"✅ QR decoded successfully for student {student_id or '[N/A]'} → {result}")
        return result

    except Exception as e:
        print(f"❌ QR Decode Error: {e}")
        return None
