#!/usr/bin/env python3
"""
DeepSeek R1 Integration with ParagonOCR
Wrapper for using DeepSeek locally via Ollama for receipt processing
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeepSeekOCRProcessor:
    """DeepSeek R1 wrapper for ParagonOCR integration."""

    def __init__(
        self,
        ollama_host: str = "http://localhost:11434",
        model: str = "deepseek-r1",
        temperature: float = 0.1
    ):
        self.ollama_host = ollama_host
        self.model = model
        self.temperature = temperature
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initialize Ollama client."""
        try:
            import ollama
            self.client = ollama.Client(host=self.ollama_host)
            logger.info(f"DeepSeek processor initialized with {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize DeepSeek: {e}")
            raise

    def process_ocr_text(
        self,
        ocr_text: str,
        prompt_version: str = "v1",
        reference_json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process OCR text and return structured JSON."""
        from .prompt_templates import PromptTemplates

        reference = reference_json or {}
        prompt = PromptTemplates.get_prompt(prompt_version, ocr_text, reference)

        try:
            start_time = time.time()
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=False,
                options={
                    "temperature": self.temperature,
                    "top_p": 0.9,
                    "num_predict": 2048,
                }
            )
            processing_time = time.time() - start_time

            response_text = response.get("response", "")
            result = self._parse_json_response(response_text)

            logger.info(f"DeepSeek processed receipt in {processing_time:.2f}s (v{prompt_version})")
            return result

        except Exception as e:
            logger.error(f"DeepSeek processing error: {e}")
            return reference or {}

    def process_receipt_batch(
        self,
        receipts: list,
        prompt_version: str = "v1"
    ) -> list:
        """Process multiple receipts."""
        results = []
        for i, receipt in enumerate(receipts, 1):
            logger.info(f"Processing receipt {i}/{len(receipts)}...")
            result = self.process_ocr_text(
                receipt.get("ocr_text", ""),
                prompt_version=prompt_version,
                reference_json=receipt.get("reference_json")
            )
            results.append({
                "receipt_id": receipt.get("id", f"receipt_{i}"),
                "extraction": result
            })
        return results

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Extract JSON from response."""
        import re
        try:
            match = re.search(r'\{[\s\S]*\}', response_text)
            if match:
                return json.loads(match.group())
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"JSON parse error: {e}")
        return {}

    def benchmark_prompt_versions(
        self,
        ocr_text: str,
        reference_json: Dict[str, Any],
        versions: list
    ) -> Dict[str, Any]:
        """Test multiple prompt versions and return results."""
        from .prompt_templates import PromptVersion

        results = {}
        for version in versions:
            logger.info(f"Testing prompt {version}...")
            start = time.time()
            result = self.process_ocr_text(
                ocr_text,
                prompt_version=version,
                reference_json=reference_json
            )
            elapsed = time.time() - start
            
            results[version] = {
                "output": result,
                "time": elapsed
            }

        return results


class ParagonOCRIntegration:
    """Integration point for ParagonOCR system."""

    def __init__(self, config_file: Optional[Path] = None):
        self.config = self._load_config(config_file)
        self.deepseek = DeepSeekOCRProcessor(
            ollama_host=self.config.get("ollama_host", "http://localhost:11434"),
            model=self.config.get("model", "deepseek-r1"),
            temperature=self.config.get("temperature", 0.1)
        )

    def _load_config(self, config_file: Optional[Path]) -> Dict[str, Any]:
        """Load configuration."""
        if config_file and config_file.exists():
            with open(config_file) as f:
                return json.load(f)
        return {}

    def process_receipt(
        self,
        image_path: str,
        ocr_engine: Any,  # google.cloud.vision or similar
        gpt4o_client: Any,  # openai.OpenAI client
        use_deepseek: bool = True,
        prompt_version: str = "v1"
    ) -> Dict[str, Any]:
        """Full receipt processing pipeline."""
        logger.info(f"Processing receipt: {image_path}")

        # Step 1: OCR extraction
        logger.info("Step 1: Extracting text with OCR engine...")
        raw_text = ocr_engine.extract_text(image_path)

        # Step 2: GPT-4o mini extraction
        logger.info("Step 2: Extracting JSON with GPT-4o mini...")
        gpt4o_json = gpt4o_client.extract_json(raw_text)

        # Step 3: DeepSeek optimization (if enabled)
        if use_deepseek:
            logger.info(f"Step 3: Optimizing with DeepSeek (prompt v{prompt_version})...")
            optimized_json = self.deepseek.process_ocr_text(
                raw_text,
                prompt_version=prompt_version,
                reference_json=gpt4o_json
            )
        else:
            optimized_json = gpt4o_json

        return {
            "image_path": image_path,
            "raw_ocr_text": raw_text,
            "gpt4o_extraction": gpt4o_json,
            "deepseek_optimization": optimized_json,
            "final_extraction": optimized_json
        }


if __name__ == "__main__":
    # Example usage
    processor = DeepSeekOCRProcessor()

    # Test with sample OCR text
    sample_ocr = """
    TESCO EXPRESS
    17-JAN-2026 14:32
    
    Milk 2L            1.20
    Bread              1.50
    Coffee             3.50
    --------
    SUBTOTAL:          6.20
    VAX (20%)          1.24
    --------
    TOTAL:             7.44
    
    CARD PAYMENT
    """

    print("Testing DeepSeek processor...")
    result = processor.process_ocr_text(sample_ocr, prompt_version="v2")
    print(json.dumps(result, indent=2))
