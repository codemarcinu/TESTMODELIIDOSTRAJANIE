#!/usr/bin/env python3
"""
Main Entry Point - OCR Pipeline with DeepSeek R1 Tuning

Usage:
  python main.py --mode pipeline --image receipt.png --prompt-version v2
  python main.py --mode tune --ground-truth-dir benchmarking/ground_truth --output results
  python main.py --mode benchmark --providers deepseek gpt4o
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from benchmarking.pipeline import OCRProcessingPipeline
from optimization.tuning_harness import PromptTuningHarness
from optimization.integration_deepseek import DeepSeekOCRProcessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()


def cmd_pipeline(args):
    """Run full OCR pipeline: Google Vision -> GPT-4o mini -> DeepSeek R1."""
    logger.info("Starting OCR Pipeline...")
    logger.info(f"Image: {args.image}")
    logger.info(f"Prompt version: {args.prompt_version}")

    pipeline = OCRProcessingPipeline(
        openai_key=os.getenv("OPENAI_API_KEY"),
        ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434")
    )

    result = pipeline.process_receipt(
        image_path=args.image,
        deepseek_prompt_version=args.prompt_version
    )

    # Display result
    print("\n" + "="*80)
    print("PIPELINE RESULT")
    print("="*80)
    print(f"Receipt ID: {result.receipt_id}")
    print(f"Total processing time: {result.total_processing_time:.2f}s")
    print(f"Total cost: ${result.total_cost:.4f}")
    print("\nFinal Extraction:")
    print(json.dumps(result.final_json, indent=2))

    # Save result
    output_file = Path(args.output) / f"{result.receipt_id}_result.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        from dataclasses import asdict
        json.dump(asdict(result), f, indent=2, default=str)
    logger.info(f"Result saved to {output_file}")


def cmd_batch(args):
    """Process batch of receipts."""
    logger.info(f"Processing batch from {args.input_dir}")

    pipeline = OCRProcessingPipeline(
        openai_key=os.getenv("OPENAI_API_KEY"),
        ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434")
    )

    results = pipeline.process_batch(
        image_dir=Path(args.input_dir),
        output_dir=Path(args.output),
        deepseek_prompt_version=args.prompt_version
    )

    logger.info(f"Processed {len(results)} receipts")
    print(f"\n✓ Batch processing complete: {len(results)} receipts")
    print(f"Results saved to {args.output}")


def cmd_tune(args):
    """Tune DeepSeek prompt using ground truth."""
    logger.info("Starting prompt tuning evaluation...")
    logger.info(f"Ground truth: {args.ground_truth_dir}")

    harness = PromptTuningHarness(
        ground_truth_dir=Path(args.ground_truth_dir),
        output_dir=Path(args.output)
    )

    # TODO: Integrate with actual DeepSeek processor
    print("Prompt tuning harness initialized.")
    print(f"Ground truth directory: {args.ground_truth_dir}")
    print(f"Output directory: {args.output}")
    print("\nTo run tuning:")
    print("1. Generate receipts with benchmarking/run_benchmark.py")
    print("2. Test prompt versions with optimization/tuning_harness.py")


def cmd_test_prompts(args):
    """Test different DeepSeek prompt versions."""
    logger.info("Testing DeepSeek prompt versions...")

    processor = DeepSeekOCRProcessor(
        ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-r1")
    )

    # Sample OCR text
    sample_ocr = """
    TESCO EXPRESS
    17-JAN-2026 14:32
    
    Milk 2L            1.20
    Bread              1.50  
    Coffee             3.50
    --------
    SUBTOTAL:          6.20
    VAT (20%):         1.24
    --------
    TOTAL:             7.44
    
    CARD PAYMENT
    Thank you!
    """

    sample_reference = {
        "merchant_name": "Tesco Express",
        "date": "2026-01-17",
        "total_amount": 7.44
    }

    versions = args.versions or ["v1", "v2", "v3", "v4", "v5", "v6"]
    logger.info(f"Testing versions: {versions}")

    results = processor.benchmark_prompt_versions(
        ocr_text=sample_ocr,
        reference_json=sample_reference,
        versions=versions
    )

    print("\n" + "="*80)
    print("PROMPT VERSION COMPARISON")
    print("="*80)

    for version, data in results.items():
        print(f"\n{version}:")
        print(f"  Time: {data['time']:.3f}s")
        print(f"  Output: {json.dumps(data['output'], indent=4)}")

    # Save results
    output_file = Path(args.output) / "prompt_comparison.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    logger.info(f"Comparison saved to {output_file}")


def cmd_benchmark(args):
    """Run full benchmarking suite."""
    logger.info("Starting benchmark...")
    # Delegate to run_benchmark.py
    import subprocess
    cmd = [
        sys.executable,
        "benchmarking/run_benchmark.py",
        "--image-dir", args.input_dir or "benchmarking/test_receipts",
        "--output-dir", args.output,
        "--providers"] + (args.providers or ["gpt4o_mini", "deepseek_r1"])
    subprocess.run(cmd)


def main():
    parser = argparse.ArgumentParser(
        description="OCR Pipeline with DeepSeek R1 Tuning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single receipt
  python main.py --mode pipeline --image receipt.png --prompt-version v2
  
  # Process batch
  python main.py --mode batch --input-dir receipts/ --output results/
  
  # Test prompt versions
  python main.py --mode test-prompts --versions v1 v2 v3 --output results/
  
  # Tune with ground truth
  python main.py --mode tune --ground-truth-dir benchmarking/ground_truth
  
  # Run benchmarking
  python main.py --mode benchmark --providers gpt4o_mini deepseek_r1
        """
    )

    subparsers = parser.add_subparsers(dest="mode", help="Operation mode")
    subparsers.required = True

    # Pipeline mode
    pipeline_parser = subparsers.add_parser("pipeline", help="Run OCR pipeline on single receipt")
    pipeline_parser.add_argument("--image", required=True, help="Receipt image path")
    pipeline_parser.add_argument(
        "--prompt-version", 
        default="v2",
        choices=["v1", "v2", "v3", "v4", "v5", "v6"],
        help="DeepSeek prompt version"
    )
    pipeline_parser.add_argument("--output", default="./results", help="Output directory")
    pipeline_parser.set_defaults(func=cmd_pipeline)

    # Batch mode
    batch_parser = subparsers.add_parser("batch", help="Process batch of receipts")
    batch_parser.add_argument("--input-dir", required=True, help="Input receipts directory")
    batch_parser.add_argument("--output", default="./results", help="Output directory")
    batch_parser.add_argument(
        "--prompt-version",
        default="v2",
        choices=["v1", "v2", "v3", "v4", "v5", "v6"],
        help="DeepSeek prompt version"
    )
    batch_parser.set_defaults(func=cmd_batch)

    # Tuning mode
    tune_parser = subparsers.add_parser("tune", help="Tune DeepSeek with ground truth")
    tune_parser.add_argument("--ground-truth-dir", required=True, help="Ground truth directory")
    tune_parser.add_argument("--output", default="./optimization/results", help="Output directory")
    tune_parser.set_defaults(func=cmd_tune)

    # Test prompts
    test_parser = subparsers.add_parser("test-prompts", help="Test DeepSeek prompt versions")
    test_parser.add_argument(
        "--versions",
        nargs="+",
        choices=["v1", "v2", "v3", "v4", "v5", "v6"],
        help="Versions to test"
    )
    test_parser.add_argument("--output", default="./optimization/results", help="Output directory")
    test_parser.set_defaults(func=cmd_test_prompts)

    # Benchmark
    bench_parser = subparsers.add_parser("benchmark", help="Run full benchmarking suite")
    bench_parser.add_argument("--input-dir", help="Input receipts directory")
    bench_parser.add_argument("--output", default="./benchmarking/results", help="Output directory")
    bench_parser.add_argument(
        "--providers",
        nargs="+",
        choices=["google_vision", "gpt4o_mini", "deepseek_r1"],
        help="Providers to benchmark"
    )
    bench_parser.set_defaults(func=cmd_benchmark)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
