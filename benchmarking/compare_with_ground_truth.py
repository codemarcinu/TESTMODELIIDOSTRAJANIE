#!/usr/bin/env python3
"""
Compare extracted OCR/JSON with ground truth
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any
from difflib import SequenceMatcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GroundTruthComparator:
    """Compare extraction results with ground truth."""

    def __init__(self, ground_truth_dir: Path):
        self.ground_truth_dir = Path(ground_truth_dir)

    def load_ground_truth(self, receipt_id: str) -> Dict[str, Any]:
        """Load ground truth JSON."""
        gt_file = self.ground_truth_dir / f"{receipt_id}.json"
        if gt_file.exists():
            with open(gt_file) as f:
                return json.load(f)
        return {}

    def compare_fields(self, extracted: Dict, receipt_id: str) -> Dict[str, float]:
        """Compare key fields and return accuracy scores."""
        ground_truth = self.load_ground_truth(receipt_id)
        
        if not ground_truth:
            logger.warning(f"No ground truth found for {receipt_id}")
            return {}

        results = {}
        
        # String fields
        for field in ["merchant_name", "date", "payment_method"]:
            extracted_val = (extracted.get(field) or "").lower().strip()
            gt_val = (ground_truth.get(field) or "").lower().strip()
            
            if extracted_val == gt_val:
                results[f"{field}_accuracy"] = 1.0
            else:
                ratio = SequenceMatcher(None, extracted_val, gt_val).ratio()
                results[f"{field}_accuracy"] = ratio

        # Numeric fields
        for field in ["total_amount", "subtotal_amount"]:
            extracted_val = float(extracted.get(field) or 0)
            gt_val = float(ground_truth.get(field) or 0)
            
            if gt_val == 0:
                results[f"{field}_accuracy"] = 1.0 if extracted_val == 0 else 0.0
            else:
                error = abs(extracted_val - gt_val) / gt_val
                results[f"{field}_accuracy"] = max(0, 1 - error)

        # Items count
        extracted_items = len(extracted.get("items") or [])
        gt_items = len(ground_truth.get("items") or [])
        
        if gt_items == 0:
            results["items_count_accuracy"] = 1.0 if extracted_items == 0 else 0.0
        else:
            error = abs(extracted_items - gt_items) / gt_items
            results["items_count_accuracy"] = max(0, 1 - error)

        return results

    def generate_report(self, comparisons: Dict[str, Dict]) -> str:
        """Generate comparison report."""
        report = []
        report.append("="*80)
        report.append("GROUND TRUTH COMPARISON REPORT")
        report.append("="*80)
        report.append("")

        for receipt_id, scores in comparisons.items():
            report.append(f"Receipt: {receipt_id}")
            report.append("-" * 40)
            
            if not scores:
                report.append("  No ground truth data")
            else:
                avg_accuracy = sum(scores.values()) / len(scores)
                report.append(f"  Average accuracy: {avg_accuracy*100:.1f}%")
                for field, accuracy in sorted(scores.items()):
                    report.append(f"    {field}: {accuracy*100:.1f}%")
            
            report.append("")

        return "\n".join(report)


if __name__ == "__main__":
    # Example usage
    comparator = GroundTruthComparator(Path("ground_truth"))

    # Mock extracted data
    extracted = {
        "merchant_name": "Lidl",
        "date": "2025-05-26",
        "total_amount": 53.94,
        "subtotal_amount": 45.80,
        "items": [{}, {}, {}, {}, {}, {}, {}],  # 7 items
        "payment_method": "card"
    }

    scores = comparator.compare_fields(extracted, "lidl_20250526")
    print(json.dumps(scores, indent=2))
