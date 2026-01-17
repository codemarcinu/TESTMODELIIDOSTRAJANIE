.PHONY: install setup test-gpt test-deepseek benchmark clean help

help:
	@echo "Available commands:"
	@echo "  make install       - Install all dependencies"
	@echo "  make setup         - Setup directories and config"
	@echo "  make test-gpt      - Test GPT-4o mini only"
	@echo "  make test-deepseek - Test DeepSeek R1 only"
	@echo "  make benchmark     - Run full benchmark"
	@echo "  make clean         - Clean generated files"

install:
	cd benchmarking && pip install -r requirements.txt

setup:
	cd benchmarking && cp .env.example .env && python setup_test_data.py

test-gpt:
	cd benchmarking && python run_benchmark.py --providers gpt4o_mini

test-deepseek:
	cd benchmarking && python run_benchmark.py --providers deepseek_r1

benchmark:
	cd benchmarking && python run_benchmark.py --providers gpt4o_mini deepseek_r1

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf benchmarking/results/*
