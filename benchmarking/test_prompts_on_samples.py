#!/usr/bin/env python3
"""
Test all 6 prompt versions on real Polish receipt samples
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_prompts_on_samples():
    """Test all 6 DeepSeek prompts on real samples."""
    from integration_deepseek import DeepSeekOCRProcessor
    from extract_ocr_from_samples import SampleReceiptOCRExtractor
    from compare_with_ground_truth import GroundTruthComparator

    # Extract OCR from samples
    logger.info("Step 1: Extracting OCR from sample images...")
    extractor = SampleReceiptOCRExtractor()
    
    samples = {
        "lidl_20250131": "test_receipts/Lidl20250131.jpeg",
        "lidl_20250526": "test_receipts/20250626LIDL.jpeg",
        "auchan_20250121": "test_receipts/20250121_063301.pdf",
        "biedronka_20251118": "test_receipts/Biedra20251118.pdf"
    }

    ocr_results = {}
    for receipt_id, image_path in samples.items():
        if Path(image_path).exists():
            result = extractor.extract_from_image(image_path)
            ocr_results[receipt_id] = result.get("ocr_text", "")
            logger.info(f"Extracted {receipt_id}: {len(result.get('ocr_text', ''))} chars")

    # Test prompts
    logger.info("\nStep 2: Testing 6 prompt versions...")
    processor = DeepSeekOCRProcessor(
        ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434")
    )

    comparator = GroundTruthComparator(Path("ground_truth"))
    all_results = {}

    for receipt_id, ocr_text in ocr_results.items():
        logger.info(f"\nProcessing {receipt_id}...")
        all_results[receipt_id] = {}

        for version in ["v1", "v2", "v3", "v4", "v5", "v6"]:
            logger.info(f"  Testing prompt {version}...")
            
            result = processor.process_ocr_text(
                ocr_text,
                prompt_version=version,
                reference_json=None
            )

            # Compare with ground truth
            comparison = comparator.compare_fields(result, receipt_id)
            
            all_results[receipt_id][version] = {
                "extraction": result,
                "comparison": comparison,
                "avg_accuracy": sum(comparison.values()) / len(comparison) if comparison else 0
            }

    # Save results
    output_dir = Path("results/prompt_tests_on_samples")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)

    # Generate summary
    summary = {}
    for receipt_id, versions in all_results.items():
        summary[receipt_id] = {}
        for version, data in versions.items():
            summary[receipt_id][version] = data["avg_accuracy"]

    print("\n" + "="*80)
    print("PROMPT TESTING SUMMARY - REAL POLISH RECEIPTS")
    print("="*80)
    
    for receipt_id, versions in summary.items():
        print(f"\n{receipt_id}:")
        best_version = max(versions, key=versions.get)
        for version in sorted(versions.keys()):
            accuracy = versions[version]
            marker = "⭐" if version == best_version else "  "
            print(f"  {marker} {version}: {accuracy*100:6.1f}%")

    print("\n" + "="*80)
    print(f"Results saved to {output_dir}")


if __name__ == "__main__":
    test_prompts_on_samples()
