import cv2
import os

from src.qr.qr import QRReader


class QRReaderCV2(QRReader):

    def __init__(self):
        self.detector = cv2.QRCodeDetector()

    def read(self, path: str) -> str:
        abs_path = os.path.abspath(path)
        img = cv2.imread(abs_path)
        data, bbox, straight_qrcode = self.detector.detectAndDecode(img)
        if bbox is None:
            raise ValueError("Cannot read QR code")

        return data