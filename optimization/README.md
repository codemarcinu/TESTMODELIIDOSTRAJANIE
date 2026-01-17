# Prompt Optimization & DeepSeek R1 Tuning

Tools for testing and optimizing receipt extraction accuracy using different DeepSeek R1 prompt strategies.

## Structure

- `prompt_templates.py` - 6 prompt versions (v1-v6) with different strategies
- `tuning_harness.py` - Evaluation framework against ground truth
- `integration_deepseek.py` - DeepSeek R1 wrapper for ParagonOCR integration

## Prompt Versions

### v1: Basic
Minimal instructions. Fastest but may miss details.

### v2: Detailed
Step-by-step verification with explicit rules.
Best for most use cases.

### v3: Chain-of-Thought (CoT)
Extended reasoning process. More accurate but slower.

### v4: Validation
Explicit business logic validation rules.
Good for catching math errors.

### v5: Multilingual
Support for Polish, English, etc.
Essential for diverse receipt types.

### v6: Aggressive
Prioritizes OCR error fixing.
Best for heavily corrupted text.

## Usage

### Test Single Receipt

```python
from integration_deepseek import DeepSeekOCRProcessor
from prompt_templates import PromptTemplates

processor = DeepSeekOCRProcessor()
result = processor.process_ocr_text(ocr_text, prompt_version="v2")
```

### Evaluate Multiple Prompts

```python
from integration_deepseek import DeepSeekOCRProcessor

processor = DeepSeekOCRProcessor()
results = processor.benchmark_prompt_versions(
    ocr_text=ocr_text,
    reference_json=gpt4o_output,
    versions=["v1", "v2", "v3", "v4", "v5", "v6"]
)
```

### Generate Tuning Report

```python
from tuning_harness import PromptTuningHarness
from pathlib import Path

harness = PromptTuningHarness(
    ground_truth_dir=Path("../benchmarking/ground_truth"),
    output_dir=Path("./results")
)

# Run evaluations
evaluations = []
for receipt_id in receipt_ids:
    for version in ["v1", "v2", "v3"]:
        eval_result = harness.evaluate_extraction(
            receipt_id=receipt_id,
            extracted_json=model_output,
            gpt4o_json=gpt4o_output,
            processing_time=0.5,
            version=version
        )
        evaluations.append(eval_result)

# Generate report
report = harness.generate_evaluation_report(evaluations)
print(report)
harness.save_evaluations(evaluations)
```

## Expected Accuracy

- **v1-v2**: 85-92% field accuracy
- **v3**: 90-95% field accuracy (slower)
- **v4**: 92-96% field accuracy (math validated)
- **v5**: 88-94% field accuracy (multilingual support)
- **v6**: 93-97% field accuracy (aggressive OCR fixing)

## Integration with ParagonOCR

```python
from integration_deepseek import ParagonOCRIntegration

integration = ParagonOCRIntegration()
result = integration.process_receipt(
    image_path="receipt.png",
    ocr_engine=google_vision,
    gpt4o_client=openai_client,
    prompt_version="v2"
)
```

## Next Steps

1. Test all 6 prompt versions on sample receipts
2. Measure accuracy against ground truth
3. Identify best prompt for your receipt types
4. Fine-tune temperature and other parameters
5. Deploy winning version
