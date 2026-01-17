#!/usr/bin/env python3
"""
Prompt Tuning Harness - Test and evaluate different prompt versions
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, asdict
import statistics

from .prompt_templates import PromptTemplates, PromptVersion

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PromptEvaluation:
    """Result of testing a prompt version."""
    version: str
    receipt_id: str
    
    # Accuracy metrics
    merchant_accuracy: float  # 0-1
    date_accuracy: float
    items_count_accuracy: float
    total_amount_accuracy: float
    math_validation: bool  # subtotal + tax = total
    
    # Comparison metrics
    vs_gpt4o: Dict[str, Any]  # Differences from GPT-4o result
    
    # Meta
    processing_time: float
    output_valid_json: bool


class PromptTuningHarness:
    """Evaluate different prompt versions against ground truth."""

    def __init__(self, ground_truth_dir: Path, output_dir: Path):
        self.ground_truth_dir = Path(ground_truth_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_ground_truth(self, receipt_id: str) -> Dict[str, Any]:
        """Load ground truth for a receipt."""
        gt_file = self.ground_truth_dir / f"{receipt_id}.json"
        if gt_file.exists():
            with open(gt_file) as f:
                return json.load(f)
        return {}

    def evaluate_field_accuracy(
        self,
        extracted: Any,
        ground_truth: Any,
        field_name: str
    ) -> float:
        """Evaluate accuracy for a single field (0-1)."""
        if extracted == ground_truth:
            return 1.0
        
        # Fuzzy matching for strings
        if isinstance(extracted, str) and isinstance(ground_truth, str):
            from difflib import SequenceMatcher
            ratio = SequenceMatcher(None, extracted.lower(), ground_truth.lower()).ratio()
            return ratio
        
        # Numeric fuzzy matching (within 5% tolerance)
        if isinstance(extracted, (int, float)) and isinstance(ground_truth, (int, float)):
            if ground_truth == 0:
                return 1.0 if extracted == 0 else 0.0
            error = abs(extracted - ground_truth) / abs(ground_truth)
            return max(0, 1 - error)
        
        return 0.0

    def evaluate_extraction(
        self,
        receipt_id: str,
        extracted_json: Dict[str, Any],
        gpt4o_json: Dict[str, Any],
        processing_time: float,
        version: str
    ) -> PromptEvaluation:
        """Evaluate extraction against ground truth."""
        ground_truth = self.load_ground_truth(receipt_id)

        # Validate JSON structure
        valid_json = isinstance(extracted_json, dict)

        # Field accuracy
        merchant_acc = self.evaluate_field_accuracy(
            extracted_json.get("merchant_name", ""),
            ground_truth.get("merchant_name", ""),
            "merchant_name"
        )

        date_acc = self.evaluate_field_accuracy(
            extracted_json.get("date", ""),
            ground_truth.get("date", ""),
            "date"
        )

        items_extracted = len(extracted_json.get("items", []))
        items_gt = len(ground_truth.get("items", []))
        items_acc = 1.0 if items_extracted == items_gt else (
            max(0, 1 - abs(items_extracted - items_gt) / max(items_gt, 1))
        )

        total_acc = self.evaluate_field_accuracy(
            extracted_json.get("total_amount", 0),
            ground_truth.get("total_amount", 0),
            "total_amount"
        )

        # Math validation: subtotal + tax ≈ total
        subtotal = extracted_json.get("subtotal_amount", 0)
        tax = extracted_json.get("tax_amount", 0)
        total = extracted_json.get("total_amount", 0)
        math_valid = abs((subtotal + tax) - total) < 0.01

        # Compare with GPT-4o
        differences = {}
        for key in ["merchant_name", "date", "total_amount"]:
            if extracted_json.get(key) != gpt4o_json.get(key):
                differences[key] = {
                    "extracted": extracted_json.get(key),
                    "gpt4o": gpt4o_json.get(key),
                    "ground_truth": ground_truth.get(key)
                }

        return PromptEvaluation(
            version=version,
            receipt_id=receipt_id,
            merchant_accuracy=merchant_acc,
            date_accuracy=date_acc,
            items_count_accuracy=items_acc,
            total_amount_accuracy=total_acc,
            math_validation=math_valid,
            vs_gpt4o=differences,
            processing_time=processing_time,
            output_valid_json=valid_json
        )

    def generate_evaluation_report(self, evaluations: List[PromptEvaluation]) -> str:
        """Generate comprehensive evaluation report."""
        if not evaluations:
            return "No evaluations to report."

        # Group by version
        by_version = {}
        for ev in evaluations:
            if ev.version not in by_version:
                by_version[ev.version] = []
            by_version[ev.version].append(ev)

        report = []
        report.append("="*80)
        report.append("PROMPT TUNING EVALUATION REPORT")
        report.append("="*80)
        report.append("")

        for version in sorted(by_version.keys()):
            evals = by_version[version]
            report.append(f"\nPROMPT VERSION: {version}")
            report.append("-" * 40)
            report.append(f"Receipts tested: {len(evals)}")
            report.append("")

            # Calculate metrics
            metrics = {
                "merchant_accuracy": [e.merchant_accuracy for e in evals],
                "date_accuracy": [e.date_accuracy for e in evals],
                "items_count_accuracy": [e.items_count_accuracy for e in evals],
                "total_amount_accuracy": [e.total_amount_accuracy for e in evals],
            }

            report.append("Accuracy Metrics (0-1 scale):")
            for metric, values in metrics.items():
                avg = statistics.mean(values)
                std = statistics.stdev(values) if len(values) > 1 else 0
                report.append(f"  {metric}: {avg:.3f} ± {std:.3f}")

            report.append("")
            report.append(f"Math validation (subtotal+tax=total): {sum(1 for e in evals if e.math_validation)}/{len(evals)}")
            report.append(f"Valid JSON output: {sum(1 for e in evals if e.output_valid_json)}/{len(evals)}")
            report.append(f"Avg processing time: {statistics.mean([e.processing_time for e in evals]):.3f}s")
            report.append("")

        report.append("="*80)
        return "\n".join(report)

    def save_evaluations(self, evaluations: List[PromptEvaluation]):
        """Save evaluations to JSON."""
        output_file = self.output_dir / "prompt_evaluations.json"
        with open(output_file, "w") as f:
            json.dump([asdict(e) for e in evaluations], f, indent=2)
        logger.info(f"Evaluations saved to {output_file}")


if __name__ == "__main__":
    # Example usage
    harness = PromptTuningHarness(
        ground_truth_dir=Path("../benchmarking/ground_truth"),
        output_dir=Path("./results")
    )

    # Would evaluate different prompt versions here
    print("Prompt tuning harness ready. Use PromptTuningHarness.evaluate_extraction()")
