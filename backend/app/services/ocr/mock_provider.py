import os
import random
from typing import List, Dict, Any
from backend.app.services.ocr.base import BaseOCRProvider, OCRResult, OCRToken


class MockSmartOCRProvider(BaseOCRProvider):
    """
    Intelligent Mock OCR Provider for SIH hackathon.
    Simulates real-world OCR on historical Indian land deeds (Patta deeds, 7/12 extracts, Khasra).
    Generates realistic spatial bounding boxes, OCR tokens, and confidence variations.
    """

    async def extract_text_and_boxes(self, file_path: str, file_bytes: bytes) -> OCRResult:
        filename = os.path.basename(file_path).lower()

        # Check if the file is the smudged demo deed (triggers low confidence and human verification)
        if "smudge" in filename or "demo" in filename or "low_conf" in filename or "1988" in filename:
            return self._generate_smudged_deed_result()
        elif "pune" in filename or "maharashtra" in filename or "7_12" in filename:
            return self._generate_maharashtra_deed_result()
        elif "up" in filename or "lucknow" in filename or "khasra" in filename:
            return self._generate_up_deed_result()
        else:
            # Default authentic Telangana deed
            return self._generate_default_telangana_deed_result()

    def _generate_smudged_deed_result(self) -> OCRResult:
        raw_text = """
GOVERNMENT OF TELANGANA - REVENUE DEPARTMENT
RECORD OF RIGHTS (ROR) / PATTADAR PASSBOOK EXTRACT
District: Ranga Reddy | Mandal: Shamshabad | Village: Mamidipally
Pattadar / Landowner Name: Sri K. Venkat Reddy
Father/Husband Name: Ramaiah
Survey No: 124/? (Ink smudge on original paper)
Khasra No: 124/KH-4
Khata No: 408
Plot No: P-12
Extent / Land Area: 2.45 Acres
Classification: Agricultural - Dry (Patta)
Ownership Type: Pattadar
Mutation Order No: MUT-2018-09823
Registration No: 4521/1988
Registration Date: 1988-10-14
Remarks: Ancestral partition deed. Original paper stamped at Shamshabad Sub-Registrar.
        """.strip()

        tokens = [
            OCRToken(text="GOVERNMENT", confidence=0.98, box={"x": 20, "y": 5, "w": 25, "h": 3, "page": 1}),
            OCRToken(text="State: Telangana", confidence=0.96, box={"x": 10, "y": 12, "w": 30, "h": 3, "page": 1}),
            OCRToken(text="District: Ranga Reddy", confidence=0.95, box={"x": 10, "y": 16, "w": 35, "h": 3, "page": 1}),
            OCRToken(text="Mandal: Shamshabad", confidence=0.94, box={"x": 10, "y": 20, "w": 35, "h": 3, "page": 1}),
            OCRToken(text="Village: Mamidipally", confidence=0.96, box={"x": 10, "y": 24, "w": 35, "h": 3, "page": 1}),
            OCRToken(text="Landowner: Sri K. Venkat Reddy", confidence=0.92, box={"x": 10, "y": 30, "w": 45, "h": 4, "page": 1}),
            # The smudged low-confidence survey number token!
            OCRToken(text="Survey No: 124/?", confidence=0.54, box={"x": 10, "y": 36, "w": 32, "h": 4, "page": 1}),
            OCRToken(text="Khasra No: 124/KH-4", confidence=0.88, box={"x": 50, "y": 36, "w": 35, "h": 4, "page": 1}),
            OCRToken(text="Khata No: 408", confidence=0.91, box={"x": 10, "y": 42, "w": 25, "h": 3, "page": 1}),
            OCRToken(text="Plot No: P-12", confidence=0.89, box={"x": 50, "y": 42, "w": 25, "h": 3, "page": 1}),
            OCRToken(text="Land Area: 2.45 Acres", confidence=0.94, box={"x": 10, "y": 48, "w": 38, "h": 3, "page": 1}),
            OCRToken(text="Classification: Agricultural - Dry", confidence=0.93, box={"x": 10, "y": 54, "w": 50, "h": 3, "page": 1}),
            OCRToken(text="Ownership Type: Pattadar", confidence=0.95, box={"x": 10, "y": 60, "w": 40, "h": 3, "page": 1}),
            OCRToken(text="Mutation No: MUT-2018-09823", confidence=0.89, box={"x": 10, "y": 66, "w": 45, "h": 3, "page": 1}),
            OCRToken(text="Registration No: 4521/1988", confidence=0.91, box={"x": 10, "y": 72, "w": 42, "h": 3, "page": 1}),
            OCRToken(text="Registration Date: 1988-10-14", confidence=0.90, box={"x": 10, "y": 78, "w": 45, "h": 3, "page": 1})
        ]

        return OCRResult(
            raw_text=raw_text,
            provider_name="MockSmartOCR-HighResSimulator",
            tokens=tokens,
            metadata={"skew_angle": 0.4, "dpi": 300, "smudge_detected": True}
        )

    def _generate_default_telangana_deed_result(self) -> OCRResult:
        raw_text = """
GOVERNMENT OF TELANGANA - REVENUE DEPARTMENT
DHARANI PORTAL COMPLIANT EXTRACT
State: Telangana
District: Ranga Reddy
Mandal: Shamshabad
Village: Mamidipally
Pattadar Name: Smt. Anasuya Devi
Survey No: 148/2
Khasra No: 148/A
Khata No: 512
Plot No: PL-08
Area Extent: 3.20 Acres
Land Nature: Agricultural - Dry
Ownership: Pattadar
Mutation Number: MUT-2021-00452
Registration Number: 7812/2005
Registration Date: 2005-04-12
Remarks: Title clear. Non-assigned private patta.
        """.strip()

        tokens = [
            OCRToken(text="State: Telangana", confidence=0.99, box={"x": 10, "y": 12, "w": 30, "h": 3, "page": 1}),
            OCRToken(text="District: Ranga Reddy", confidence=0.98, box={"x": 10, "y": 16, "w": 35, "h": 3, "page": 1}),
            OCRToken(text="Mandal: Shamshabad", confidence=0.97, box={"x": 10, "y": 20, "w": 35, "h": 3, "page": 1}),
            OCRToken(text="Village: Mamidipally", confidence=0.98, box={"x": 10, "y": 24, "w": 35, "h": 3, "page": 1}),
            OCRToken(text="Landowner: Smt. Anasuya Devi", confidence=0.96, box={"x": 10, "y": 30, "w": 45, "h": 4, "page": 1}),
            OCRToken(text="Survey No: 148/2", confidence=0.96, box={"x": 10, "y": 36, "w": 32, "h": 4, "page": 1}),
            OCRToken(text="Khasra No: 148/A", confidence=0.95, box={"x": 50, "y": 36, "w": 35, "h": 4, "page": 1}),
            OCRToken(text="Khata No: 512", confidence=0.97, box={"x": 10, "y": 42, "w": 25, "h": 3, "page": 1}),
            OCRToken(text="Plot No: PL-08", confidence=0.94, box={"x": 50, "y": 42, "w": 25, "h": 3, "page": 1}),
            OCRToken(text="Land Area: 3.20 Acres", confidence=0.98, box={"x": 10, "y": 48, "w": 38, "h": 3, "page": 1}),
            OCRToken(text="Classification: Agricultural - Dry", confidence=0.96, box={"x": 10, "y": 54, "w": 50, "h": 3, "page": 1}),
            OCRToken(text="Ownership Type: Pattadar", confidence=0.98, box={"x": 10, "y": 60, "w": 40, "h": 3, "page": 1}),
            OCRToken(text="Mutation No: MUT-2021-00452", confidence=0.95, box={"x": 10, "y": 66, "w": 45, "h": 3, "page": 1}),
            OCRToken(text="Registration No: 7812/2005", confidence=0.97, box={"x": 10, "y": 72, "w": 42, "h": 3, "page": 1}),
            OCRToken(text="Registration Date: 2005-04-12", confidence=0.96, box={"x": 10, "y": 78, "w": 45, "h": 3, "page": 1})
        ]

        return OCRResult(
            raw_text=raw_text,
            provider_name="MockSmartOCR-CleanScan",
            tokens=tokens,
            metadata={"skew_angle": 0.0, "dpi": 300}
        )

    def _generate_maharashtra_deed_result(self) -> OCRResult:
        raw_text = """
GOVERNMENT OF MAHARASHTRA - REVENUE & FOREST DEPARTMENT
FORM VII-XII (7/12 EXTRACT)
State: Maharashtra
District: Pune
Mandal/Tehsil: Haveli
Village: Wagholi
Bhogvatdar / Landowner: Rajeshwar Dattatray Patil
Gat / Survey Number: 88/1A
Khata Number: 184
Total Area: 1.75 Hectares
Land Usage: Jirayat (Agricultural)
Ownership: Sole Proprietor (Class 1)
Ferfar / Mutation No: MUT-MH-2019-112
Dast / Registration No: 2014-9981
Registration Date: 2014-06-20
Remarks: Clear title as per Mahabhulekh records.
        """.strip()

        tokens = [
            OCRToken(text="State: Maharashtra", confidence=0.98, box={"x": 10, "y": 12, "w": 30, "h": 3, "page": 1}),
            OCRToken(text="District: Pune", confidence=0.98, box={"x": 10, "y": 16, "w": 25, "h": 3, "page": 1}),
            OCRToken(text="Tehsil: Haveli", confidence=0.97, box={"x": 10, "y": 20, "w": 25, "h": 3, "page": 1}),
            OCRToken(text="Village: Wagholi", confidence=0.98, box={"x": 10, "y": 24, "w": 30, "h": 3, "page": 1}),
            OCRToken(text="Landowner: Rajeshwar Dattatray Patil", confidence=0.95, box={"x": 10, "y": 30, "w": 55, "h": 4, "page": 1}),
            OCRToken(text="Survey No: 88/1A", confidence=0.96, box={"x": 10, "y": 36, "w": 30, "h": 4, "page": 1}),
            OCRToken(text="Khata No: 184", confidence=0.95, box={"x": 10, "y": 42, "w": 25, "h": 3, "page": 1}),
            OCRToken(text="Land Area: 1.75 Hectares", confidence=0.97, box={"x": 10, "y": 48, "w": 40, "h": 3, "page": 1}),
            OCRToken(text="Classification: Agricultural - Jirayat", confidence=0.96, box={"x": 10, "y": 54, "w": 45, "h": 3, "page": 1}),
            OCRToken(text="Ownership Type: Sole Proprietor", confidence=0.97, box={"x": 10, "y": 60, "w": 40, "h": 3, "page": 1}),
            OCRToken(text="Mutation No: MUT-MH-2019-112", confidence=0.94, box={"x": 10, "y": 66, "w": 45, "h": 3, "page": 1}),
            OCRToken(text="Registration No: 2014-9981", confidence=0.95, box={"x": 10, "y": 72, "w": 40, "h": 3, "page": 1}),
            OCRToken(text="Registration Date: 2014-06-20", confidence=0.96, box={"x": 10, "y": 78, "w": 45, "h": 3, "page": 1})
        ]

        return OCRResult(
            raw_text=raw_text,
            provider_name="MockSmartOCR-Mahabhulekh",
            tokens=tokens
        )

    def _generate_up_deed_result(self) -> OCRResult:
        raw_text = """
GOVERNMENT OF UTTAR PRADESH - REVENUE COUNCIL
KHASRA - KHATAUNI EXTRACT (BHULEKH)
State: Uttar Pradesh
District: Lucknow
Mandal/Tehsil: Mohanlalganj
Village: Bakas
Bhumidhar / Landowner: Ramcharan Verma
Gata / Survey No: 215/3
Khasra No: 215
Khata Number: 312
Land Area: 4.50 Bigha
Classification: Agricultural
Ownership: Bhumidhar with transferable rights
Mutation Number: MUT-UP-2020-0031
Registration Number: 8812/2011
Registration Date: 2011-11-05
Remarks: Non-zamindari land.
        """.strip()

        tokens = [
            OCRToken(text="State: Uttar Pradesh", confidence=0.97, box={"x": 10, "y": 12, "w": 35, "h": 3, "page": 1}),
            OCRToken(text="District: Lucknow", confidence=0.98, box={"x": 10, "y": 16, "w": 30, "h": 3, "page": 1}),
            OCRToken(text="Tehsil: Mohanlalganj", confidence=0.97, box={"x": 10, "y": 20, "w": 35, "h": 3, "page": 1}),
            OCRToken(text="Village: Bakas", confidence=0.98, box={"x": 10, "y": 24, "w": 25, "h": 3, "page": 1}),
            OCRToken(text="Landowner: Ramcharan Verma", confidence=0.96, box={"x": 10, "y": 30, "w": 45, "h": 4, "page": 1}),
            OCRToken(text="Survey No: 215/3", confidence=0.95, box={"x": 10, "y": 36, "w": 30, "h": 4, "page": 1}),
            OCRToken(text="Khasra No: 215", confidence=0.94, box={"x": 50, "y": 36, "w": 25, "h": 4, "page": 1}),
            OCRToken(text="Khata No: 312", confidence=0.96, box={"x": 10, "y": 42, "w": 25, "h": 3, "page": 1}),
            OCRToken(text="Land Area: 4.50 Bigha", confidence=0.97, box={"x": 10, "y": 48, "w": 35, "h": 3, "page": 1}),
            OCRToken(text="Classification: Agricultural", confidence=0.96, box={"x": 10, "y": 54, "w": 40, "h": 3, "page": 1}),
            OCRToken(text="Ownership Type: Bhumidhar", confidence=0.97, box={"x": 10, "y": 60, "w": 40, "h": 3, "page": 1}),
            OCRToken(text="Mutation No: MUT-UP-2020-0031", confidence=0.93, box={"x": 10, "y": 66, "w": 45, "h": 3, "page": 1}),
            OCRToken(text="Registration No: 8812/2011", confidence=0.95, box={"x": 10, "y": 72, "w": 40, "h": 3, "page": 1}),
            OCRToken(text="Registration Date: 2011-11-05", confidence=0.96, box={"x": 10, "y": 78, "w": 45, "h": 3, "page": 1})
        ]

        return OCRResult(
            raw_text=raw_text,
            provider_name="MockSmartOCR-UPBhulekh",
            tokens=tokens
        )
