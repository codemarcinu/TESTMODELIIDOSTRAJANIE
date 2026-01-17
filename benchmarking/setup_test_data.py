#!/usr/bin/env python3
"""
Test Data Setup - Prepares directories and validates ground truth
"""
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestDataValidator:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.test_receipts_dir = self.base_dir / "test_receipts"
        self.ground_truth_dir = self.base_dir / "ground_truth"
        self.results_dir = self.base_dir / "results"

    def setup_directories(self):
        """Create required directory structure."""
        dirs = [self.test_receipts_dir, self.ground_truth_dir, self.results_dir]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")

    def generate_sample_ground_truth(self, num_samples: int = 5):
        """Generate sample ground truth files for testing."""
        merchants = ["Tesco Express", "Sainsbury's", "Costa Coffee", "McDonald's", "Boots"]
        items_pool = [("Milk", 1, 1.20), ("Bread", 1, 1.50), ("Coffee", 1, 3.50)]

        for i in range(num_samples):
            receipt_id = f"receipt_{i+1:03d}"
            merchant = random.choice(merchants)
            num_items = random.randint(2, 6)
            selected_items = random.sample(items_pool, min(num_items, len(items_pool)))
            
            items = []
            items_total = 0
            for description, quantity, unit_price in selected_items:
                item_total = quantity * unit_price
                items_total += item_total
                items.append({
                    "description": description,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total": round(item_total, 2),
                })

            tax = round(items_total * 0.20, 2)
            total = round(items_total + tax, 2)
            receipt_date = (datetime.now() - timedelta(days=random.randint(0, 30))).date()
            receipt_time = f"{random.randint(8, 20):02d}:{random.randint(0, 59):02d}"

            ground_truth = {
                "merchant_name": merchant,
                "date": str(receipt_date),
                "time": receipt_time,
                "total_amount": total,
                "tax_amount": tax,
                "items": items,
                "payment_method": random.choice(["card", "cash"]),
                "raw_text": f"[OCR text for {receipt_id}]",
            }

            gt_file = self.ground_truth_dir / f"{receipt_id}.json"
            with open(gt_file, "w") as f:
                json.dump(ground_truth, f, indent=2)
            logger.info(f"Generated: {receipt_id}")

def main():
    validator = TestDataValidator(Path("."))
    validator.setup_directories()
    validator.generate_sample_ground_truth(10)
    print("\n✓ Test data setup complete")

if __name__ == "__main__":
    main()
