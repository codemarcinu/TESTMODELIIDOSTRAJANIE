#!/usr/bin/env python3
"""
Tune DeepSeek R1 to match GPT-4o mini's output.

This script runs the full OCR pipeline for each of the 6 DeepSeek prompt versions
on a set of real receipts. It then compares the final DeepSeek JSON output
to the intermediate GPT-4o mini JSON output to see which prompt version
makes DeepSeek behave most like GPT-4o mini.
"""

import json
import logging
from pathlib import Path
import os
import tempfile
from typing import Dict, Any

from dotenv import load_dotenv
from fuzzywuzzy import fuzz
from pdf2image import convert_from_path

from benchmarking.pipeline import OCRProcessingPipeline

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def compare_json_outputs(gpt4o_json: Dict[str, Any], deepseek_json: Dict[str, Any]) -> float:
    """
    Compares two JSON objects and returns a similarity score (0-1).
    """
    if not gpt4o_json or not deepseek_json:
        return 0.0

    score = 0
    num_fields = 0

    # Compare top-level fields
    for key in gpt4o_json.keys():
        if key not in ['items', 'raw_text']: # Items are compared separately
            num_fields += 1
            gpt_val = str(gpt4o_json.get(key, ''))
            ds_val = str(deepseek_json.get(key, ''))
            score += fuzz.ratio(gpt_val.lower(), ds_val.lower()) / 100

    # Compare items (description only for simplicity)
    gpt_items = [str(item.get('description', '')) for item in gpt4o_json.get('items', [])]
    ds_items = [str(item.get('description', '')) for item in deepseek_json.get('items', [])]
    
    if gpt_items:
        num_fields += 1
        # Simple set comparison of item descriptions
        gpt_set = set(i.lower() for i in gpt_items)
        ds_set = set(i.lower() for i in ds_items)
        score += len(gpt_set.intersection(ds_set)) / len(gpt_set) if gpt_set else 1.0


    return score / num_fields if num_fields > 0 else 0.0


def find_receipt_files():
    """Finds pairs of receipt images/pdfs and their ground truth json."""
    gt_dir = Path("benchmarking/ground_truth")
    receipts_dir = Path("benchmarking/test_receipts")
    
    found_files = {}
    
    if not gt_dir.exists() or not receipts_dir.exists():
        logger.error("Ground truth or receipts directory not found.")
        return found_files

    for gt_file in gt_dir.glob("*.json"):
        receipt_id = gt_file.stem
        found_receipt = False
        for ext in ['.png', '.jpeg', '.jpg', '.pdf']:
            receipt_path = receipts_dir / f"{receipt_id}{ext}"
            if receipt_path.exists():
                found_files[receipt_id] = str(receipt_path)
                found_receipt = True
                break
        if not found_receipt:
            logger.warning(f"Could not find a matching receipt for ground truth: {gt_file.name}")
            
    return found_files


def tune_deepseek_to_gpt():
    """
    Main function to run the tuning process.
    """
    sample_images = find_receipt_files()
    
    if not sample_images:
        logger.error("No matching receipt and ground truth files found. Exiting.")
        return
    
    pipeline = OCRProcessingPipeline(
        openai_key=os.getenv("OPENAI_API_KEY"),
        ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434")
    )
    
    all_results = {}

    first_receipt_processed = False
    for receipt_id, image_path_str in sample_images.items():
        if first_receipt_processed:
            break # Process only the first receipt for this test
        first_receipt_processed = True

        original_path = Path(image_path_str)
        if not original_path.exists():
            logger.warning(f"File not found: {original_path}. Skipping.")
            continue
            
        logger.info(f"\\nProcessing receipt: {receipt_id}")
        all_results[receipt_id] = {}
        
        # Handle PDF conversion
        processing_path = original_path
        temp_image_file = None

        if original_path.suffix.lower() == '.pdf':
            logger.info(f"  Converting PDF to image...")
            try:
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_f:
                    temp_image_file = temp_f.name
                    images = convert_from_path(original_path, first_page=1, last_page=1)
                    if images:
                        images[0].save(temp_image_file, 'PNG')
                        processing_path = Path(temp_image_file)
                    else:
                        logger.error(f"Could not convert PDF: {original_path}")
                        continue
            except Exception as e:
                logger.error(f"PDF conversion failed for {original_path}: {e}")
                continue
        
        for version in [f"v{i}" for i in range(1, 7)]:
            logger.info(f"  Testing DeepSeek prompt version: {version}")
            
            # Run the full pipeline
            result = pipeline.process_receipt(
                image_path=str(processing_path),
                deepseek_prompt_version=version
            )
            
            gpt4o_output = result.gpt4o_mini_stage.output_data
            deepseek_output = result.deepseek_r1_stage.output_data
            
            # Compare the outputs
            similarity_score = compare_json_outputs(gpt4o_output, deepseek_output)
            
            all_results[receipt_id][version] = {
                'similarity_to_gpt4o': similarity_score,
                'gpt4o_json': gpt4o_output,
                'deepseek_json': deepseek_output
            }
            logger.info(f"  -> Similarity score to GPT-4o: {similarity_score:.2f}")

        # Clean up temporary file
        if temp_image_file:
            os.remove(temp_image_file)
            logger.info(f"  Cleaned up temporary file: {temp_image_file}")

    # --- Summary ---
    print("\n" + "="*80)
    print("DEEPSEEK TUNING SUMMARY (Similarity to GPT-4o mini)")
    print("="*80)
    
    for receipt_id, versions in all_results.items():
        print(f"\nReceipt: {receipt_id}")
        # Sort versions by similarity score, descending
        sorted_versions = sorted(versions.items(), key=lambda item: item[1]['similarity_to_gpt4o'], reverse=True)
        
        for i, (version, data) in enumerate(sorted_versions):
            marker = "⭐" if i == 0 else "  "
            score = data['similarity_to_gpt4o']
            print(f"  {marker} {version}: {score*100:6.1f}%")
            
    # Save detailed results
    output_file = Path("optimization/results/tuning_to_gpt4o_results.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    logger.info("\nDetailed results saved to {output_file}")


if __name__ == "__main__":
    tune_deepseek_to_gpt()
