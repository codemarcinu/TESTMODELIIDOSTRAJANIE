#!/usr/bin/env python3
"""
Prompt Templates for DeepSeek R1 Tuning
Different prompt versions for receipt extraction optimization
"""

import json
from typing import Dict, Any
from enum import Enum


class PromptVersion(Enum):
    """Available prompt versions for testing."""
    V1_BASIC = "v1"
    V2_DETAILED = "v2"
    V3_COT = "v3"
    V4_VALIDATION = "v4"
    V5_MULTILINGUAL = "v5"
    V6_AGGRESSIVE = "v6"


class PromptTemplates:
    """Prompt templates for different optimization strategies."""

    @staticmethod
    def get_prompt(version: str, raw_ocr: str, gpt4o_json: Dict[str, Any]) -> str:
        """Get prompt for specific version."""
        
        if version == "v1":
            return PromptTemplates.v1_basic(raw_ocr, gpt4o_json)
        elif version == "v2":
            return PromptTemplates.v2_detailed(raw_ocr, gpt4o_json)
        elif version == "v3":
            return PromptTemplates.v3_cot(raw_ocr, gpt4o_json)
        elif version == "v4":
            return PromptTemplates.v4_validation(raw_ocr, gpt4o_json)
        elif version == "v5":
            return PromptTemplates.v5_multilingual(raw_ocr, gpt4o_json)
        elif version == "v6":
            return PromptTemplates.v6_aggressive(raw_ocr, gpt4o_json)
        else:
            return PromptTemplates.v1_basic(raw_ocr, gpt4o_json)

    @staticmethod
    def v1_basic(raw_ocr: str, gpt4o_json: Dict[str, Any]) -> str:
        """V1: Basic prompt - minimal instructions."""
        return f"""Extract and optimize receipt data from OCR text.

OCR TEXT:
{raw_ocr}

GPT-4o EXTRACTION:
{json.dumps(gpt4o_json, indent=2)}

Return corrected JSON:
{{
  "merchant_name": "Store name",
  "date": "YYYY-MM-DD",
  "time": "HH:MM",
  "total_amount": 0.00,
  "subtotal_amount": 0.00,
  "tax_amount": 0.00,
  "tax_percentage": 0.0,
  "items": [{{
    "description": "Item",
    "quantity": 1.0,
    "unit_price": 0.00,
    "total": 0.00
  }}],
  "payment_method": null,
  "receipt_number": null,
  "store_address": null,
  "store_phone": null
}}

Return ONLY JSON."""

    @staticmethod
    def v2_detailed(raw_ocr: str, gpt4o_json: Dict[str, Any]) -> str:
        """V2: Detailed prompt - step-by-step verification."""
        return f"""You are an expert receipt analyzer. Review this OCR text and GPT-4o mini's extraction, then provide optimized JSON.

OCR TEXT:
{raw_ocr}

GPT-4o MINI EXTRACTION:
{json.dumps(gpt4o_json, indent=2)}

Verify and optimize:
1. Merchant name: Is it accurate? Fix any OCR errors (e.g., "5tesco" → "Tesco")
2. Date: Must be YYYY-MM-DD. Look for common formats: DD/MM/YYYY, MM-DD-YYYY
3. Items: Are all items listed? Check quantities and prices match OCR
4. Math verification:
   - Calculate items sum
   - Add tax if applicable
   - Verify: subtotal + tax = total (within 0.01 rounding)
5. Payment method: Look for "CARD", "CASH", "CONTACTLESS"
6. OCR errors: Common mistakes - "0" → "O", "1" → "l"

Return corrected JSON with this structure:
{{
  "merchant_name": "Store name (exact)",
  "date": "YYYY-MM-DD",
  "time": "HH:MM",
  "total_amount": 0.00,
  "subtotal_amount": 0.00,
  "tax_amount": 0.00,
  "tax_percentage": 0.0,
  "items": [{{
    "description": "Item description",
    "quantity": 1.0,
    "unit_price": 0.00,
    "total": 0.00
  }}],
  "payment_method": "card/cash/contactless/other",
  "receipt_number": null,
  "store_address": null,
  "store_phone": null
}}

Rules:
- Return ONLY valid JSON, no other text
- Do NOT include markdown code blocks
- All numeric values must be valid numbers
- Dates must be exactly YYYY-MM-DD format
- If unsure about a field, use null
"""

    @staticmethod
    def v3_cot(raw_ocr: str, gpt4o_json: Dict[str, Any]) -> str:
        """V3: Chain-of-thought reasoning."""
        return f"""Let's analyze this receipt step by step using careful reasoning.

OCR TEXT:
{raw_ocr}

Previous extraction (GPT-4o mini):
{json.dumps(gpt4o_json, indent=2)}

=== STEP-BY-STEP ANALYSIS ===

Step 1: IDENTIFY MERCHANT NAME
Look for store name in OCR text. Common locations: top line, large text, before items.
Check for OCR errors: "5tesco" → "Tesco", "J0HN" → "JOHN"
Current value: {gpt4o_json.get('merchant_name', 'UNKNOWN')}
Corrected value: [extract from OCR]

Step 2: FIND TRANSACTION DATE
Look for date patterns: "17-Jan-2026", "17/01/2026", "2026-01-17"
Convert all to YYYY-MM-DD format
Current value: {gpt4o_json.get('date', 'UNKNOWN')}
Corrected value: [extract and convert]

Step 3: LIST ALL ITEMS
For each item, record:
- Description (product name)
- Quantity (usually 1, but could be multiple)
- Unit price (price per item)
- Total (quantity × unit_price)

Step 4: VERIFY SUBTOTAL
Calculate: sum of all item totals
Should match "SUBTOTAL" line in receipt (if present)

Step 5: IDENTIFY TAX
Look for "TAX", "VAT", "GST" lines
Calculate tax percentage if possible
Example: if subtotal is £10 and tax is £2, then tax_percentage = 20%

Step 6: VERIFY TOTAL
Formula: subtotal + tax = total (within ±0.01 for rounding)
If formula doesn't match, re-check all values

Step 7: EXTRACT PAYMENT METHOD
Look for: "CARD", "CASH", "CONTACTLESS", "PHONE", "CHIP", "VISA", "MASTERCARD"

=== FINAL JSON ===

Return ONLY this JSON structure (no markdown, no explanation):
{{
  "merchant_name": "...",
  "date": "YYYY-MM-DD",
  "time": "HH:MM",
  "total_amount": 0.00,
  "subtotal_amount": 0.00,
  "tax_amount": 0.00,
  "tax_percentage": 0.0,
  "items": [{{
    "description": "...",
    "quantity": 1.0,
    "unit_price": 0.00,
    "total": 0.00
  }}],
  "payment_method": null,
  "receipt_number": null,
  "store_address": null,
  "store_phone": null
}}"""

    @staticmethod
    def v4_validation(raw_ocr: str, gpt4o_json: Dict[str, Any]) -> str:
        """V4: With explicit validation rules."""
        return f"""Extract receipt data and validate using business rules.

OCR TEXT:
{raw_ocr}

Current extraction:
{json.dumps(gpt4o_json, indent=2)}

=== VALIDATION RULES ===

Rule 1: Merchant Name
✓ Non-empty string
✓ Length 2-100 characters
✓ No leading/trailing spaces
✗ All caps (likely OCR error) - convert to Title Case
✗ Numbers only - probably incorrect

Rule 2: Date
✓ Format: YYYY-MM-DD
✓ Year 2000-2030
✓ Month 01-12
✓ Day 01-31
✗ Future date - likely error
✗ Very old date (>2 years ago) - verify

Rule 3: Items
✓ At least 1 item
✓ Each item has description, quantity, unit_price, total
✓ All amounts > 0
✓ Quantities reasonable (0.1 - 999.9)
✓ total = quantity × unit_price (±0.01)

Rule 4: Math Verification
✓ subtotal = sum of all item totals
✓ tax_percentage in range 0-25 (typical sales tax)
✓ tax_amount ≈ subtotal × (tax_percentage / 100)
✓ total ≈ subtotal + tax_amount
✓ total > subtotal (always positive)

Rule 5: Payment Method
✓ One of: "cash", "card", "contactless", "phone", "other"
✗ Misspelled or abbreviated - standardize

=== OUTPUT ===

Return ONLY valid JSON:
{{
  "merchant_name": "Store name",
  "date": "YYYY-MM-DD",
  "time": "HH:MM",
  "total_amount": 0.00,
  "subtotal_amount": 0.00,
  "tax_amount": 0.00,
  "tax_percentage": 0.0,
  "items": [{{
    "description": "Item",
    "quantity": 1.0,
    "unit_price": 0.00,
    "total": 0.00
  }}],
  "payment_method": null,
  "receipt_number": null,
  "store_address": null,
  "store_phone": null
}}

Validate all rules before returning."""

    @staticmethod
    def v5_multilingual(raw_ocr: str, gpt4o_json: Dict[str, Any]) -> str:
        """V5: Multilingual support (Polish, English, etc)."""
        return f"""Extract receipt data - multilingual support.

OCR TEXT:
{raw_ocr}

Current extraction:
{json.dumps(gpt4o_json, indent=2)}

=== MULTILINGUAL KEYWORDS ===

English:
- Store names: Tesco, Sainsbury's, Asda, Boots, Costa
- Date: Date, Transaction Date
- Items: Item, Product, Description, Qty, Quantity
- Total: Total, Grand Total, Amount Due
- Tax: Tax, VAT, Sales Tax, GST
- Payment: Payment, Method, Card, Cash

Polski:
- Sklep: Biedronka, Lidl, Carrefour, Rossmann, Żabka
- Data: Data, Data transakcji
- Towary: Towar, Produkt, Nazwa, Ilość
- Razem: Razem, Łącznie, Suma
- Podatek: Podatek, VAT
- Płatność: Płatność, Metoda, Karta, Gotówka

Rules:
- Convert all dates to YYYY-MM-DD regardless of source format
- Standardize payment method to English lowercase: "cash", "card", "contactless"
- Keep merchant name in original language
- All amounts must be numeric

=== FINAL JSON ===
{{
  "merchant_name": "Store name",
  "date": "YYYY-MM-DD",
  "time": "HH:MM",
  "total_amount": 0.00,
  "subtotal_amount": 0.00,
  "tax_amount": 0.00,
  "tax_percentage": 0.0,
  "items": [{{
    "description": "Item",
    "quantity": 1.0,
    "unit_price": 0.00,
    "total": 0.00
  }}],
  "payment_method": null,
  "receipt_number": null,
  "store_address": null,
  "store_phone": null
}}

Return ONLY JSON."""

    @staticmethod
    def v6_aggressive(raw_ocr: str, gpt4o_json: Dict[str, Any]) -> str:
        """V6: Aggressive correction - prioritize OCR fixing."""
        return f"""Aggressively extract and correct receipt data. Fix ALL OCR errors.

OCR TEXT:
{raw_ocr}

Previous extraction:
{json.dumps(gpt4o_json, indent=2)}

=== AGGRESSIVE OCR ERROR FIXING ===

Common OCR Errors:
0 (zero) → O (letter O) - check context
1 (one) → l (lowercase L), I (uppercase i) - verify with context
l (lowercase L) → 1 (one) - check context
B (letter) → 8 (eight) - verify
S (letter) → 5 (five) - verify
O (letter) → 0 (zero) - verify
@ → a (at sign)
£ → L (pound symbol)
€ → E (euro symbol)

Context-based fixes:
- If field is "5tesco", correct to "Tesco" (store name context)
- If field is "l2,34", correct to "12.34" (price context)
- If field is "O1/O2/2O26", correct to "01/02/2026" (date context)

=== AGGRESSIVE EXTRACTION ===

1. MERCHANT: Fix OCR, standardize to Title Case
2. DATE: Convert any format to YYYY-MM-DD (aggressive date parsing)
3. ITEMS: Extract ALL items, even if partially visible
4. PRICES: Fix decimal errors (0.2 might be 0.20 or 2.0)
5. QUANTITIES: Assume 1 if not specified
6. TAX: Infer from total-subtotal difference if not explicit
7. PAYMENT: Infer from keywords, default to null if unknown

=== OUTPUT ===
{{
  "merchant_name": "Store name (OCR corrected)",
  "date": "YYYY-MM-DD",
  "time": "HH:MM",
  "total_amount": 0.00,
  "subtotal_amount": 0.00,
  "tax_amount": 0.00,
  "tax_percentage": 0.0,
  "items": [{{
    "description": "Item (OCR corrected)",
    "quantity": 1.0,
    "unit_price": 0.00,
    "total": 0.00
  }}],
  "payment_method": null,
  "receipt_number": null,
  "store_address": null,
  "store_phone": null
}}

Return ONLY JSON. Aggressively fix ALL visible errors."""
