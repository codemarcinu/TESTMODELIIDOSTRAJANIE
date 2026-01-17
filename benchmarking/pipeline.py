#!/usr/bin/env python3
"""
Complete OCR Processing Pipeline
Paragon -> Google Vision (raw text) -> GPT-4o mini (JSON) -> DeepSeek R1 (optimized JSON)
"""

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PipelineStage:
    """Result from each pipeline stage."""
    stage_name: str
    input_data: Any
    output_data: Any
    processing_time: float
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    error: Optional[str] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class ReceiptProcessingResult:
    """Complete result from all pipeline stages."""
    receipt_id: str
    image_path: str
    
    # Pipeline stages
    google_vision_stage: PipelineStage  # Raw OCR text
    gpt4o_mini_stage: PipelineStage     # JSON extraction
    deepseek_r1_stage: PipelineStage    # Optimized JSON
    
    # Final result
    final_json: Dict[str, Any]
    total_processing_time: float
    total_cost: float
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class GoogleVisionOCRStage:
    """Stage 1: Extract raw text from receipt image using Google Vision API."""

    def __init__(self):
        try:
            from google.cloud import vision
            self.client = vision.ImageAnnotatorClient()
            self.available = True
        except ImportError:
            logger.warning("google-cloud-vision not installed - skipping Google Vision")
            self.available = False

    def process(self, image_path: str) -> PipelineStage:
        """Extract raw text from receipt image."""
        start_time = time.time()
        
        if not self.available:
            return PipelineStage(
                stage_name="google_vision",
                input_data=image_path,
                output_data="",
                processing_time=0,
                error="Google Vision not available"
            )

        try:
            with open(image_path, "rb") as image_file:
                content = image_file.read()

            image = {"content": content}
            request = {"image": image, "features": [{"type_": 1, "max_results": 10}]}

            response = self.client.document_text_detection(request)
            raw_text = response.full_text_annotation.text if response.full_text_annotation else ""

            processing_time = time.time() - start_time

            logger.info(f"Google Vision extracted {len(raw_text)} characters in {processing_time:.2f}s")

            return PipelineStage(
                stage_name="google_vision",
                input_data=image_path,
                output_data=raw_text,
                processing_time=processing_time,
                cost=0.0015,  # Google Vision pricing
            )

        except Exception as e:
            logger.error(f"Google Vision error: {e}")
            return PipelineStage(
                stage_name="google_vision",
                input_data=image_path,
                output_data="",
                processing_time=0,
                error=str(e)
            )


class GPT4oMiniExtractionStage:
    """Stage 2: Convert raw OCR text to structured JSON using GPT-4o mini."""

    def __init__(self, api_key: Optional[str] = None):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            self.available = True
        except ImportError:
            logger.warning("openai not installed - skipping GPT-4o mini")
            self.available = False

    def process(self, raw_ocr_text: str) -> PipelineStage:
        """Convert raw OCR text to structured JSON."""
        start_time = time.time()
        
        if not self.available:
            return PipelineStage(
                stage_name="gpt4o_mini",
                input_data=raw_ocr_text[:100],
                output_data={},
                processing_time=0,
                error="GPT-4o mini not available"
            )

        try:
            prompt = self._get_extraction_prompt(raw_ocr_text)

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at extracting receipt data from OCR text and returning valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=2048,
            )

            processing_time = time.time() - start_time
            response_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            # Parse JSON
            extracted_json = self._parse_json_response(response_text)

            # Calculate cost: $0.00015 per input token, $0.0006 per output token
            input_tokens = int(tokens_used * 0.6)
            output_tokens = tokens_used - input_tokens
            cost = (input_tokens * 0.00015) + (output_tokens * 0.0006)

            logger.info(f"GPT-4o mini processed in {processing_time:.2f}s, tokens: {tokens_used}, cost: ${cost:.4f}")

            return PipelineStage(
                stage_name="gpt4o_mini",
                input_data=raw_ocr_text[:100],
                output_data=extracted_json,
                processing_time=processing_time,
                tokens_used=tokens_used,
                cost=cost,
            )

        except Exception as e:
            logger.error(f"GPT-4o mini error: {e}")
            return PipelineStage(
                stage_name="gpt4o_mini",
                input_data=raw_ocr_text[:100],
                output_data={},
                processing_time=0,
                error=str(e)
            )

    def _get_extraction_prompt(self, raw_ocr_text: str) -> str:
        """Get GPT-4o mini extraction prompt."""
        return f"""Extract structured receipt data from this OCR text and return ONLY valid JSON:

OCR TEXT:
{raw_ocr_text}

Return JSON with this exact structure:
{{
  "merchant_name": "Store name (required)",
  "date": "YYYY-MM-DD format (required)",
  "time": "HH:MM format (optional)",
  "total_amount": 0.00,
  "subtotal_amount": 0.00,
  "tax_amount": 0.00,
  "tax_percentage": 0.0,
  "items": [
    {{
      "description": "Item name",
      "quantity": 1.0,
      "unit_price": 0.00,
      "total": 0.00
    }}
  ],
  "payment_method": "cash/card/phone/other",
  "receipt_number": "if visible",
  "store_address": "if visible",
  "store_phone": "if visible"
}}

Rules:
- Return ONLY JSON, no other text
- Dates must be YYYY-MM-DD format
- All amounts must be numeric
- Items array must include all line items
- If field is missing, use null
- Verify that subtotal + tax = total
"""

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from GPT-4o mini response."""
        try:
            import re
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"Failed to parse JSON: {e}")
        
        return {}


class DeepSeekR1OptimizationStage:
    """Stage 3: Optimize extraction using local DeepSeek R1 via Ollama."""

    def __init__(self, ollama_host: str = "http://localhost:11434", model: str = "deepseek-r1"):
        self.ollama_host = ollama_host
        self.model = model
        self.available = False
        self._init_ollama()

    def _init_ollama(self):
        """Initialize Ollama client."""
        try:
            import ollama
            self.client = ollama.Client(host=self.ollama_host)
            # Test connection
            models = self.client.list()
            self.available = True
            logger.info(f"Ollama connected. Available models: {len(models.get('models', []))}")
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            self.available = False

    def process(self, raw_ocr_text: str, gpt4o_json: Dict[str, Any], prompt_version: str = "v1") -> PipelineStage:
        """Optimize receipt extraction using DeepSeek R1."""
        start_time = time.time()
        
        if not self.available:
            return PipelineStage(
                stage_name="deepseek_r1",
                input_data=raw_ocr_text[:100],
                output_data=gpt4o_json,  # Fallback to GPT-4o mini result
                processing_time=0,
                error="DeepSeek R1/Ollama not available"
            )

        try:
            prompt = self._get_optimization_prompt(raw_ocr_text, gpt4o_json, prompt_version)

            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=False,
                options={
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "num_predict": 2048,
                }
            )

            processing_time = time.time() - start_time
            response_text = response.get("response", "")

            # Parse JSON
            optimized_json = self._parse_json_response(response_text)
            
            # Fallback to GPT-4o result if parsing fails
            if not optimized_json:
                optimized_json = gpt4o_json

            logger.info(f"DeepSeek R1 optimized in {processing_time:.2f}s using prompt v{prompt_version}")

            return PipelineStage(
                stage_name="deepseek_r1",
                input_data=raw_ocr_text[:100],
                output_data=optimized_json,
                processing_time=processing_time,
                cost=0.00001,  # Approximate compute cost for local inference
            )

        except Exception as e:
            logger.error(f"DeepSeek R1 error: {e}")
            # Fallback to GPT-4o mini result
            return PipelineStage(
                stage_name="deepseek_r1",
                input_data=raw_ocr_text[:100],
                output_data=gpt4o_json,
                processing_time=time.time() - start_time,
                error=str(e)
            )

    def _get_optimization_prompt(self, raw_ocr_text: str, gpt4o_json: Dict[str, Any], version: str = "v1") -> str:
        """Get DeepSeek R1 optimization prompt (different versions for testing)."""
        
        if version == "v2":
            # Version 2: More detailed reasoning
            return f"""You are an expert receipt analyzer. Review this OCR text and GPT-4o mini's extraction, then provide optimized JSON.

OCR TEXT:
{raw_ocr_text}

GPT-4o MINI EXTRACTION:
{json.dumps(gpt4o_json, indent=2)}

Analyze and optimize:
1. Verify merchant name is accurate
2. Check date format is YYYY-MM-DD
3. Validate all items are listed
4. Ensure math: subtotal + tax = total
5. Fix any obvious OCR errors
6. Return corrected JSON only

JSON FORMAT:
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
  "payment_method": "...",
  "receipt_number": null,
  "store_address": null,
  "store_phone": null
}}

Return ONLY valid JSON."""
        
        elif version == "v3":
            # Version 3: Chain-of-thought reasoning
            return f"""Let's analyze this receipt step by step.

OCR TEXT:
{raw_ocr_text}

Previous extraction (GPT-4o mini):
{json.dumps(gpt4o_json, indent=2)}

Step 1: Extract merchant name from OCR
Step 2: Find transaction date
Step 3: List all items with quantities and prices
Step 4: Calculate subtotal from items
Step 5: Identify tax amount
Step 6: Verify: subtotal + tax = total
Step 7: Return corrected JSON

RETURN JSON ONLY in this format:
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
}}"""
        
        else:  # v1 - default
            return f"""Extract and optimize receipt data from OCR text.

OCR TEXT:
{raw_ocr_text}

GPT-4o EXTRACTION:
{json.dumps(gpt4o_json, indent=2)}

Optimize and return corrected JSON:
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

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from DeepSeek R1 response."""
        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"Failed to parse DeepSeek JSON: {e}")
        
        return {}


class OCRProcessingPipeline:
    """Complete OCR processing pipeline orchestrator."""

    def __init__(self, openai_key: Optional[str] = None, ollama_host: str = "http://localhost:11434"):
        self.google_vision_stage = GoogleVisionOCRStage()
        self.gpt4o_stage = GPT4oMiniExtractionStage(api_key=openai_key)
        self.deepseek_stage = DeepSeekR1OptimizationStage(ollama_host=ollama_host)

    def process_receipt(
        self,
        image_path: str,
        deepseek_prompt_version: str = "v1"
    ) -> ReceiptProcessingResult:
        """Process receipt through complete pipeline."""
        receipt_id = Path(image_path).stem
        logger.info(f"Processing receipt: {receipt_id}")

        # Stage 1: Google Vision OCR
        logger.info("Stage 1: Google Vision OCR extraction...")
        google_stage = self.google_vision_stage.process(image_path)
        raw_ocr_text = google_stage.output_data

        # Stage 2: GPT-4o mini JSON extraction
        logger.info("Stage 2: GPT-4o mini JSON extraction...")
        gpt4o_stage = self.gpt4o_stage.process(raw_ocr_text)
        gpt4o_json = gpt4o_stage.output_data

        # Stage 3: DeepSeek R1 optimization
        logger.info(f"Stage 3: DeepSeek R1 optimization (prompt v{deepseek_prompt_version})...")
        deepseek_stage = self.deepseek_stage.process(
            raw_ocr_text,
            gpt4o_json,
            prompt_version=deepseek_prompt_version
        )
        optimized_json = deepseek_stage.output_data

        # Calculate totals
        total_time = (
            google_stage.processing_time +
            gpt4o_stage.processing_time +
            deepseek_stage.processing_time
        )
        total_cost = (
            (google_stage.cost or 0) +
            (gpt4o_stage.cost or 0) +
            (deepseek_stage.cost or 0)
        )

        result = ReceiptProcessingResult(
            receipt_id=receipt_id,
            image_path=image_path,
            google_vision_stage=google_stage,
            gpt4o_mini_stage=gpt4o_stage,
            deepseek_r1_stage=deepseek_stage,
            final_json=optimized_json,
            total_processing_time=total_time,
            total_cost=total_cost,
        )

        logger.info(f"Completed {receipt_id} in {total_time:.2f}s, cost: ${total_cost:.4f}")
        return result

    def process_batch(
        self,
        image_dir: Path,
        output_dir: Path,
        deepseek_prompt_version: str = "v1"
    ) -> list:
        """Process multiple receipts from directory."""
        image_dir = Path(image_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        images = list(image_dir.glob("*.png")) + list(image_dir.glob("*.jpg"))
        logger.info(f"Processing {len(images)} receipts...")

        results = []
        for image_path in images:
            try:
                result = self.process_receipt(str(image_path), deepseek_prompt_version)
                results.append(result)

                # Save individual result
                output_file = output_dir / f"{result.receipt_id}.json"
                with open(output_file, "w") as f:
                    json.dump(asdict(result), f, indent=2, default=str)

            except Exception as e:
                logger.error(f"Error processing {image_path}: {e}")

        # Save summary
        summary = self._generate_summary(results)
        with open(output_dir / "pipeline_summary.json", "w") as f:
            json.dump(summary, f, indent=2)

        return results

    def _generate_summary(self, results: list) -> Dict[str, Any]:
        """Generate processing summary."""
        import numpy as np
        
        if not results:
            return {"total_receipts": 0}

        return {
            "total_receipts": len(results),
            "total_time": sum(r.total_processing_time for r in results),
            "total_cost": sum(r.total_cost for r in results),
            "avg_time_per_receipt": np.mean([r.total_processing_time for r in results]),
            "avg_cost_per_receipt": np.mean([r.total_cost for r in results]),
            "google_vision_cost": sum(r.google_vision_stage.cost or 0 for r in results),
            "gpt4o_mini_cost": sum(r.gpt4o_mini_stage.cost or 0 for r in results),
            "deepseek_cost": sum(r.deepseek_r1_stage.cost or 0 for r in results),
            "timestamp": datetime.now().isoformat(),
        }


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    # Initialize pipeline
    pipeline = OCRProcessingPipeline(
        openai_key=os.getenv("OPENAI_API_KEY"),
        ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434")
    )

    # Process single receipt
    if Path("test_receipts").exists():
        images = list(Path("test_receipts").glob("*.png"))
        if images:
            result = pipeline.process_receipt(str(images[0]))
            print(json.dumps(asdict(result), indent=2, default=str))
