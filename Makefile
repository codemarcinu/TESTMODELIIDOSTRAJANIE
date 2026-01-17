.PHONY: install setup test pipeline batch tune benchmark clean help

help:
	@echo "OCR Benchmarking & Tuning - Available commands:"
	@echo ""
	@echo "Setup:"
	@echo "  make install       - Install all dependencies"
	@echo "  make setup         - Setup directories and test data"
	@echo ""
	@echo "Testing:"
	@echo "  make pipeline      - Process single test receipt"
	@echo "  make batch         - Process batch of receipts"
	@echo "  make test-prompts  - Test all 6 DeepSeek prompt versions"
	@echo "  make tune          - Run tuning with ground truth"
	@echo ""
	@echo "Benchmarking:"
	@echo "  make benchmark     - Run full OCR provider benchmark"
	@echo "  make benchmark-gpt - Benchmark GPT-4o mini only"
	@echo "  make benchmark-ds  - Benchmark DeepSeek R1 only"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean         - Clean generated files"
	@echo "  make clean-all     - Clean everything including results"

install:
	@echo "Installing dependencies..."
	cd benchmarking && pip install -r requirements.txt
	cd ../optimization && pip install -r requirements.txt
	@echo "✓ Dependencies installed"

setup:
	@echo "Setting up test environment..."
	cd benchmarking && python setup_test_data.py
	@echo "✓ Test environment ready"

pipeline:
	@echo "Processing single receipt..."
	python main.py pipeline --image benchmarking/test_receipts/receipt_001.png --prompt-version v2

batch:
	@echo "Processing batch..."
	python main.py batch --input-dir benchmarking/test_receipts --output results/

test-prompts:
	@echo "Testing all 6 prompt versions..."
	python main.py test-prompts --versions v1 v2 v3 v4 v5 v6 --output optimization/results/

tune:
	@echo "Running prompt tuning..."
	python main.py tune --ground-truth-dir benchmarking/ground_truth --output optimization/results/

benchmark:
	@echo "Running full benchmark..."
	python main.py benchmark --providers gpt4o_mini deepseek_r1 --output benchmarking/results/

benchmark-gpt:
	@echo "Benchmarking GPT-4o mini..."
	python main.py benchmark --providers gpt4o_mini --output benchmarking/results/

benchmark-ds:
	@echo "Benchmarking DeepSeek R1..."
	python main.py benchmark --providers deepseek_r1 --output benchmarking/results/

clean:
	@echo "Cleaning Python cache..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✓ Cache cleaned"

clean-all: clean
	@echo "Cleaning results..."
	rm -rf benchmarking/results/* 2>/dev/null || true
	rm -rf optimization/results/* 2>/dev/null || true
	@echo "✓ All cleaned"
