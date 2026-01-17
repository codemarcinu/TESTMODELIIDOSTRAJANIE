#!/usr/bin/env python3
"""
OCR Benchmark Runner - CLI interface for benchmarking OCR providers
"""
import argparse
import json
import logging
from pathlib import Path
from typing import Optional, List

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from ocr_benchmark_engine import (
    OCRBenchmark,
    OCRProvider,
    GoogleVisionExtractor,
    GPT4oMiniExtractor,
    DeepSeekR1Extractor,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BenchmarkReporter:
    """Generate reports and visualizations."""

    def __init__(self, results_dir: Path):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def generate_comparison_report(self, summary: dict) -> str:
        """Generate comprehensive comparison report."""
        report = []
        report.append("="*80)
        report.append("OCR BENCHMARKING REPORT")
        report.append("="*80)
        report.append("")

        # Overall statistics
        report.append("BENCHMARK OVERVIEW")
        report.append("-" * 40)
        report.append(f"Total Tests: {summary['total_tests']}")
        report.append(f"Timestamp: {summary['timestamp']}")
        report.append("")

        # Provider comparison
        report.append("PROVIDER COMPARISON")
        report.append("-" * 40)

        providers_data = []
        for provider_name, metrics in summary["providers"].items():
            providers_data.append({
                "Provider": provider_name,
                "Tests": metrics["count"],
                "Field Accuracy": f"{metrics['avg_field_accuracy']*100:.2f}%",
                "Fuzzy Accuracy": f"{metrics['avg_fuzzy_accuracy']*100:.2f}%",
                "Avg Time (s)": f"{metrics['avg_processing_time']:.3f}",
                "Total Cost": f"${metrics['total_cost']:.4f}",
                "Consistency": f"{metrics['avg_consistency_score']:.2f}",
            })

        df = pd.DataFrame(providers_data)
        report.append(df.to_string(index=False))
        report.append("")
        report.append("="*80)

        return "\n".join(report)

    def create_visualizations(self, summary: dict):
        """Create visualization plots."""
        if not summary["providers"]:
            logger.warning("No data to visualize")
            return

        providers = list(summary["providers"].keys())
        metrics = summary["providers"]

        # Create figure with subplots
        fig, axes = plt.subplots(2, 3, figsize=(14, 10))
        fig.suptitle("OCR Benchmark Comparison", fontsize=16, fontweight="bold")

        # 1. Accuracy comparison
        ax = axes[0, 0]
        field_acc = [metrics[p]["avg_field_accuracy"] * 100 for p in providers]
        ax.bar(providers, field_acc, color="steelblue")
        ax.set_ylabel("Accuracy (%)")
        ax.set_title("Field-Level Accuracy")
        ax.set_ylim(0, 105)

        # 2. Fuzzy accuracy
        ax = axes[0, 1]
        fuzzy_acc = [metrics[p]["avg_fuzzy_accuracy"] * 100 for p in providers]
        ax.bar(providers, fuzzy_acc, color="darkgreen")
        ax.set_ylabel("Accuracy (%)")
        ax.set_title("Fuzzy Matching Accuracy")
        ax.set_ylim(0, 105)

        # 3. Processing time
        ax = axes[0, 2]
        proc_time = [metrics[p]["avg_processing_time"] for p in providers]
        ax.bar(providers, proc_time, color="orange")
        ax.set_ylabel("Time (seconds)")
        ax.set_title("Average Processing Time")

        # 4. Cost comparison
        ax = axes[1, 0]
        costs = [metrics[p]["total_cost"] for p in providers]
        ax.bar(providers, costs, color="crimson")
        ax.set_ylabel("Cost ($)")
        ax.set_title("Total Cost")

        # 5. Field completeness
        ax = axes[1, 1]
        completeness = [metrics[p]["avg_field_completeness"] * 100 for p in providers]
        ax.bar(providers, completeness, color="mediumslateblue")
        ax.set_ylabel("Completeness (%)")
        ax.set_title("Field Extraction Completeness")
        ax.set_ylim(0, 105)

        # 6. Consistency score
        ax = axes[1, 2]
        consistency = [metrics[p]["avg_consistency_score"] for p in providers]
        ax.bar(providers, consistency, color="darkviolet")
        ax.set_ylabel("Score (0-1)")
        ax.set_title("Business Logic Consistency")
        ax.set_ylim(0, 1.1)

        plt.tight_layout()
        plt.savefig(self.results_dir / "benchmark_comparison.png", dpi=300, bbox_inches="tight")
        logger.info(f"Visualization saved to {self.results_dir / 'benchmark_comparison.png'}")
        plt.close()


def main():
    parser = argparse.ArgumentParser(description="Run OCR benchmarking suite")
    parser.add_argument(
        "--image-dir",
        type=Path,
        default=Path("benchmarking/test_receipts"),
        help="Directory with test receipt images"
    )
    parser.add_argument(
        "--ground-truth-dir",
        type=Path,
        default=Path("benchmarking/ground_truth"),
        help="Directory with ground truth JSON files"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("benchmarking/results"),
        help="Output directory for results and reports"
    )
    parser.add_argument(
        "--providers",
        nargs="+",
        choices=["google_vision", "gpt4o_mini", "deepseek_r1"],
        default=["gpt4o_mini", "deepseek_r1"],
        help="Providers to benchmark"
    )
    parser.add_argument(
        "--skip-visualization",
        action="store_true",
        help="Skip visualization generation"
    )
    parser.add_argument(
        "--openai-key",
        type=str,
        help="OpenAI API key"
    )

    args = parser.parse_args()

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Starting OCR benchmark...")

    # Initialize benchmark
    benchmark = OCRBenchmark(ground_truth_dir=args.ground_truth_dir)

    # Register selected providers
    provider_map = {
        "gpt4o_mini": (
            OCRProvider.GPT4O_MINI,
            lambda: GPT4oMiniExtractor(api_key=args.openai_key)
        ),
        "deepseek_r1": (
            OCRProvider.DEEPSEEK_R1,
            lambda: DeepSeekR1Extractor()
        ),
        "google_vision": (
            OCRProvider.GOOGLE_VISION,
            lambda: GoogleVisionExtractor()
        ),
    }

    for provider_key in args.providers:
        if provider_key in provider_map:
            provider, extractor_fn = provider_map[provider_key]
            try:
                benchmark.register_extractor(provider, extractor_fn())
            except Exception as e:
                logger.warning(f"Failed to initialize {provider_key}: {e}")

    # Run benchmark
    try:
        results = benchmark.run_benchmark(
            image_dir=args.image_dir,
            output_dir=args.output_dir
        )

        # Generate reports
        reporter = BenchmarkReporter(args.output_dir)
        report = reporter.generate_comparison_report(results)
        
        # Save report
        report_file = args.output_dir / "benchmark_report.txt"
        with open(report_file, "w") as f:
            f.write(report)
        
        print(report)
        logger.info(f"Report saved to {report_file}")

        # Generate visualizations
        if not args.skip_visualization:
            try:
                reporter.create_visualizations(results)
            except Exception as e:
                logger.error(f"Visualization failed: {e}")

    except Exception as e:
        logger.error(f"Benchmark failed: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
