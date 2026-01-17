# OCR Benchmarking Suite

Comprehensive benchmarking system comparing Google Vision API, GPT-4o mini, and DeepSeek R1.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Setup configuration
cp .env.example .env
# Edit .env with your API keys

# Generate test data
python setup_test_data.py

# Run benchmark
python run_benchmark.py --image-dir test_receipts --output-dir results
```

## Providers

- **Google Vision** - Cloud-based, accurate, costs $0.0015/image
- **GPT-4o mini** - Benchmark model, costs $0.001-0.002/image
- **DeepSeek R1** - Local model, free, ~91-94% accuracy target

## Metrics

- Field Accuracy - Exact match on key fields
- Fuzzy Accuracy - >80% similarity matches
- Processing Time - Seconds per receipt
- Cost - Total API/compute cost
- Consistency - Business rule validation
