import cv2

from src.qr.qr import QRReader


class QRReaderCV2(QRReader):

    def __init__(self):
        self.detector = cv2.QRCodeDetector()

    def read(self, path: str) -> str:
        img = cv2.imread(path)
        data, bbox, straight_qrcode = self.detector.detectAndDecode(img)
        if bbox is None:
            raise ValueError("Cannot read QR code")

        return data