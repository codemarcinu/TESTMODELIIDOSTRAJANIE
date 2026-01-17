#!/usr/bin/env python3
"""
Extract OCR text from sample receipt images
Support: Google Vision API
"""

import json
import logging
from pathlib import Path
from typing import Optional
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SampleReceiptOCRExtractor:
    """Extract OCR from sample receipt images."""

    def __init__(self, google_credentials: Optional[str] = None):
        self.google_credentials = google_credentials
        self.client = None
        self._init_google_vision()

    def _init_google_vision(self):
        """Initialize Google Vision client."""
        try:
            from google.cloud import vision
            self.client = vision.ImageAnnotatorClient()
            logger.info("Google Vision initialized")
        except ImportError:
            logger.warning("google-cloud-vision not installed")
            self.client = None

    def extract_from_image(self, image_path: str) -> dict:
        """Extract OCR text from receipt image."""
        image_path = Path(image_path)
        
        if not image_path.exists():
            logger.error(f"File not found: {image_path}")
            return {"error": "File not found"}

        logger.info(f"Extracting from: {image_path}")

        if self.client:
            return self._extract_google_vision(str(image_path))
        else:
            return self._extract_mock(str(image_path))

    def _extract_google_vision(self, image_path: str) -> dict:
        """Extract using Google Vision API."""
        try:
            with open(image_path, "rb") as f:
                content = f.read()

            image = {"content": content}
            request = {"image": image, "features": [{"type_": 1}]}

            response = self.client.document_text_detection(request)
            text = response.full_text_annotation.text if response.full_text_annotation else ""

            return {
                "success": True,
                "image_path": image_path,
                "ocr_text": text,
                "provider": "google_vision",
                "confidence": "high"
            }

        except Exception as e:
            logger.error(f"Google Vision error: {e}")
            return {"success": False, "error": str(e)}

    def _extract_mock(self, image_path: str) -> dict:
        """Mock extraction (use this when API not available)."""
        filename = Path(image_path).name.lower()
        
        # Mock OCR results based on filename
        mock_data = {
            "lidl20250131": """LIDL sp. z o. o.
Poznańska 48, Jankowice
62-080 Tarnowo Podgórne
www.lidl.pl

2025-01-31 06:33

Reklamówka mała rec.     0,79
Pierożki Gyoza x2           14,98
Skyr pitniy naturali        10,99
Czekolada b.z orzech x3     20,97
Kramersy Dobry Chrup         5,29
Nektyr miód                 2,99
Banany luz                   6,99
Bulka graham x4              7,96
Kiat sak x3                  5,97

Razem: 83,05 PLN
Nr: 22402
Karta płatnicza
""",
            "20250626lidl": """LIDL sp. z o. o.
Poznańska 48, Jankowice
62-080 Tarnowo Podgórne

2025-05-26 14:32

Reklamówka mała rec.     0,79
Pierożki Gyoza x2           14,98
Skyr pitniy naturali        10,99
Czekolada b.z orzech x3     20,97
Kramersy Dobry Chrup         5,29
Nektyr miód                 2,99
Banany luz                   6,99

Subtotal:                   45,80
VAT 20%:                    14,74
VAT 5%:                      1,87
VAT (inna):                 39,20

Razem: 53,94 PLN
Nr: 45949
Karta płatnicza
""",
            "20250121": """AUCHAN

2025-01-21 06:33

Sty piuw natural.            8,99
Jaja kurze                   4,99
Koreizfassias F1            10,74
Banan ewf                    6,99
Pierożki Gyoza x2           14,98
Skyr pitniy naturali        10,99
Czekolada b.z orzech x3     20,97

Subtotal:                   70,35
VAT 23%:                    12,70

Razem: 83,05 PLN
Nr: 44825
Karta płatnicza
""",
            "auchan": """AUCHAN

2025-01-21

Sty piuw natural.            8,99
Jaja kurze                   4,99
Koreizfassias F1            10,74
Banan ewf                    6,99
Pierożki Gyoza x2           14,98
Skyr pitniy naturali        10,99
Czekolada b.z orzech x3     20,97

Razem: 83,05 PLN
""",
            "biedra": """BIEDRONKA
ul. Radzymińska
03-694 Warszawa

2025-11-18 18:01

Reklamówka mała rec.     0,79
Pierożki Gyoza x2           14,98
Skyr pitniy naturali        10,99
Czekolada b.z orzech x3     20,97
Kramersy Dobry Chrup         5,29
Nektyr miód                 2,99
Banany luz                   6,99

Rabat TANIEI:               -1,06

Razem: 53,94 PLN
Nr: 90
"""
        }

        ocr_text = ""
        for key, text in mock_data.items():
            if key in filename.replace(".", ""):
                ocr_text = text
                break

        if not ocr_text:
            ocr_text = "[Mock OCR - enable Google Vision API]"

        return {
            "success": True,
            "image_path": image_path,
            "ocr_text": ocr_text,
            "provider": "mock",
            "confidence": "medium",
            "note": "Mock data - use Google Vision for real extraction"
        }

    def extract_batch(self, image_dir: str, output_dir: str = "."):
        """Extract OCR from all images in directory."""
        image_dir = Path(image_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        images = list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.jpeg")) + list(image_dir.glob("*.png"))
        logger.info(f"Found {len(images)} images")

        results = []
        for img_path in images:
            result = self.extract_from_image(str(img_path))
            results.append(result)

            # Save individual OCR
            if result.get("success"):
                ocr_file = output_dir / f"{img_path.stem}_ocr.txt"
                with open(ocr_file, "w") as f:
                    f.write(result.get("ocr_text", ""))

        # Save summary
        summary = output_dir / "ocr_extraction_summary.json"
        with open(summary, "w") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"Results saved to {output_dir}")
        return results


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    # Extract from all samples
    extractor = SampleReceiptOCRExtractor(
        google_credentials=os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    )

    results = extractor.extract_batch(
        image_dir="test_receipts",
        output_dir="ocr_results"
    )

    print(f"\n✓ Extracted {len(results)} receipts")
    for r in results:
        if r.get("success"):
            print(f"  - {Path(r['image_path']).name}: {len(r['ocr_text'])} chars")
