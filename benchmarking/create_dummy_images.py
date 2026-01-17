
import os
from pathlib import Path
from PIL import Image

def create_dummy_images(ground_truth_dir, image_dir):
    """Creates dummy white PNG images for each ground truth JSON file."""
    ground_truth_dir = Path(ground_truth_dir)
    image_dir = Path(image_dir)
    image_dir.mkdir(exist_ok=True)

    if not ground_truth_dir.exists():
        print(f"Error: Ground truth directory not found at {ground_truth_dir}")
        return

    json_files = list(ground_truth_dir.glob("*.json"))
    if not json_files:
        print("No ground truth JSON files found.")
        return

    print(f"Found {len(json_files)} ground truth files. Creating dummy images...")

    for json_file in json_files:
        receipt_id = json_file.stem
        # Use .png as the benchmark script looks for this
        image_path = image_dir / f"{receipt_id}.png"
        
        if not image_path.exists():
            # Create a small white dummy image
            img = Image.new('RGB', (100, 100), color = 'white')
            img.save(image_path)
            print(f"Created dummy image: {image_path.name}")
        else:
            print(f"Dummy image already exists: {image_path.name}")

if __name__ == "__main__":
    create_dummy_images("ground_truth", "test_receipts")
    print("Dummy image creation complete.")
