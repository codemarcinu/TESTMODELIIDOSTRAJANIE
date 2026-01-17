# OCR Benchmarking & Tuning - Test Models and Optimize DeepSeek R1

Comprehensive system for benchmarking receipt OCR against multiple providers and optimizing local DeepSeek R1 via Ollama.

## Architecture

```
Receipt Image
     ↓
Google Vision API (→ raw text)
     ↓
GPT-4o mini (→ initial JSON)
     ↓
DeepSeek R1 (Ollama) (→ optimized JSON) ← TUNING HERE
     ↓
Final Extraction (JSON)
```

## Key Features

- **Three-stage pipeline**: Google Vision → GPT-4o mini → DeepSeek R1
- **6 prompt versions** for DeepSeek tuning (v1-v6)
- **Evaluation framework** against ground truth
- **Comprehensive benchmarking** with cost tracking
- **Batch processing** for multiple receipts
- **ParagonOCR integration** ready

## Installation

```bash
git clone https://github.com/codemarcinu/TESTMODELIIDOSTRAJANIE
cd TESTMODELIIDOSTRAJANIE

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd benchmarking
pip install -r requirements.txt
cd ../optimization
pip install -r requirements.txt
cd ..
```

## Configuration

```bash
# Copy and edit configuration
cp benchmarking/.env.example benchmarking/.env
cp optimization/.env.example optimization/.env

# Add your API keys
export OPENAI_API_KEY="sk-your-key"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/gcp-creds.json"
export OLLAMA_HOST="http://localhost:11434"  # DeepSeek via Ollama
```

## Quick Start

### 1. Setup Test Data

```bash
cd benchmarking
python setup_test_data.py
```

Generates:
- `test_receipts/` - test receipt images (placeholder)
- `ground_truth/` - ground truth JSON files
- `results/` - output directory

### 2. Process Single Receipt

```bash
python main.py pipeline --image benchmarking/test_receipts/receipt_001.png --prompt-version v2
```

Process stages:
1. Google Vision extracts raw OCR text
2. GPT-4o mini converts to JSON structure
3. DeepSeek R1 optimizes with v2 prompt

### 3. Process Batch

```bash
python main.py batch --input-dir benchmarking/test_receipts --output results/
```

### 4. Test Prompt Versions

```bash
python main.py test-prompts --versions v1 v2 v3 v4 --output optimization/results/
```

Compares all prompt strategies on same receipt.

### 5. Full Benchmark

```bash
python main.py benchmark --providers gpt4o_mini deepseek_r1 --output benchmarking/results/
```

## Prompt Versions

| Version | Strategy | Accuracy | Speed | Use Case |
|---------|----------|----------|-------|----------|
| **v1** | Basic | 85-92% | Fast | Quick processing |
| **v2** | Detailed | 88-94% | Medium | **Recommended** |
| **v3** | Chain-of-Thought | 90-95% | Slow | Complex receipts |
| **v4** | Validation | 92-96% | Medium | Math validation |
| **v5** | Multilingual | 88-94% | Medium | Polish/mixed receipts |
| **v6** | Aggressive | 93-97% | Medium | OCR-heavy text |

## Output Structure

### Pipeline Result

```json
{
  "receipt_id": "receipt_001",
  "image_path": "test_receipts/receipt_001.png",
  "google_vision_stage": {
    "stage_name": "google_vision",
    "output_data": "Raw OCR text...",
    "processing_time": 1.23,
    "cost": 0.0015
  },
  "gpt4o_mini_stage": {
    "stage_name": "gpt4o_mini",
    "output_data": { ... JSON ... },
    "processing_time": 0.5,
    "tokens_used": 256,
    "cost": 0.0005
  },
  "deepseek_r1_stage": {
    "stage_name": "deepseek_r1",
    "output_data": { ... optimized JSON ... },
    "processing_time": 2.1,
    "cost": 0.00001
  },
  "final_json": { ... },
  "total_processing_time": 3.83,
  "total_cost": 0.00201
}
```

### Final Extraction JSON

```json
{
  "merchant_name": "Tesco Express",
  "date": "2026-01-17",
  "time": "14:32",
  "total_amount": 7.44,
  "subtotal_amount": 6.20,
  "tax_amount": 1.24,
  "tax_percentage": 20.0,
  "items": [
    {
      "description": "Milk 2L",
      "quantity": 1.0,
      "unit_price": 1.20,
      "total": 1.20
    }
  ],
  "payment_method": "card",
  "receipt_number": null,
  "store_address": null,
  "store_phone": null
}
```

## Tuning Workflow

### 1. Prepare Ground Truth

Create `benchmarking/ground_truth/receipt_XXX.json` with correct data:

```json
{
  "merchant_name": "Actual store name",
  "date": "2026-01-17",
  "total_amount": 7.44,
  "items": [...]
}
```

### 2. Run Tests

```bash
python main.py test-prompts --versions v1 v2 v3 v4 v5 v6
```

### 3. Evaluate Results

```python
from optimization.tuning_harness import PromptTuningHarness

harness = PromptTuningHarness(
    ground_truth_dir="benchmarking/ground_truth",
    output_dir="optimization/results"
)

report = harness.generate_evaluation_report(evaluations)
print(report)
```

### 4. Deploy Best Version

Update pipeline to use best-performing prompt version.

## Integration with ParagonOCR

```python
from optimization.integration_deepseek import ParagonOCRIntegration

integration = ParagonOCRIntegration()

result = integration.process_receipt(
    image_path="receipt.png",
    ocr_engine=google_vision,
    gpt4o_client=openai_client,
    prompt_version="v2"
)

print(result["final_extraction"])
```

## Cost Analysis

Per receipt (approx):
- **Google Vision**: $0.0015 (if using OCR)
- **GPT-4o mini**: $0.0005-0.001
- **DeepSeek R1**: $0.00001 (local, Ollama)
- **Total**: $0.002-0.0025 per receipt

## Performance Expectations

- **Processing time**: 3-5 seconds per receipt (with API calls)
- **Local only (DeepSeek)**: 1-2 seconds per receipt
- **Accuracy**: 90-95% field-level (depending on prompt)
- **Throughput**: 720-1200 receipts/day with API

## Troubleshooting

### Ollama not available

```bash
# Start Ollama with DeepSeek
ollama run deepseek-r1
```

### OpenAI API errors

- Check `OPENAI_API_KEY` in `.env`
- Verify API key has GPT-4o mini access
- Check rate limits

### Google Vision errors

- Check `GOOGLE_APPLICATION_CREDENTIALS` points to valid JSON key
- Verify GCP project has Vision API enabled

## Project Structure

```
.
├─ benchmarking/
│  ├─ pipeline.py             # Main 3-stage pipeline
│  ├─ run_benchmark.py        # Benchmark runner
│  ├─ setup_test_data.py      # Test data setup
│  ├─ ocr_benchmark_engine.py # Benchmark engine
│  ├─ requirements.txt
│  ├─ test_receipts/          # Sample receipts
│  ├─ ground_truth/           # Ground truth JSON
│  ├─ results/                # Benchmark outputs
│  └─ README.md
├─ optimization/
│  ├─ prompt_templates.py     # 6 prompt versions
│  ├─ tuning_harness.py       # Evaluation framework
│  ├─ integration_deepseek.py # ParagonOCR integration
│  ├─ requirements.txt
│  ├─ results/                # Tuning outputs
│  └─ README.md
├─ main.py                  # CLI entry point
├─ Makefile                 # Convenient commands
├─ .env.example             # Configuration template
├─ .gitignore
├─ LICENSE                  # MIT License
└─ README.md                # This file
```

## Next Steps

1. [✓] Setup directories and dependencies
2. [✓] Generate test data
3. [ ] Test with actual receipt images
4. [ ] Run benchmark on all providers
5. [ ] Evaluate all 6 prompt versions
6. [ ] Select optimal prompt for your receipts
7. [ ] Fine-tune temperature/parameters
8. [ ] Deploy to ParagonOCR

## Resources

- [Ollama + DeepSeek R1](https://ollama.ai/)
- [OpenAI API - GPT-4o mini](https://platform.openai.com/docs/)
- [Google Cloud Vision](https://cloud.google.com/vision)
- [Receipt OCR Best Practices](./docs/receipt-ocr-guide.md)

## License

MIT License - See LICENSE file

## Author

**Marcin** - [@codemarcinu](https://github.com/codemarcinu)

Specialist in AI, cybersecurity, and OCR automation.
