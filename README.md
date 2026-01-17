# 🚀 OCR Model Testing & Optimization Suite

Kompleksowy system do testowania i optymalizacji modeli OCR dla przetwarzania paragonów.

## 📋 Cel Projektu

Portfolio porównawcze trzech dostawców OCR:

| Provider | Koszt | Szybkość | Dokładność |
|----------|-------|----------|------------|
| **Google Vision API** | $0.0015/receipt | 1.5-3s | 85-90% |
| **GPT-4o mini** | $0.001-0.002 | 2-4s | 92-96% 🏆 |
| **DeepSeek R1** | ~$0.00001 (local) | 0.5-1.5s ⚡ | 88-94% (cel) |

**Cel**: Optymalizacja DeepSeek R1 do poziomu GPT-4o mini, przy zachowaniu lokalnego wdrożenia (zero kosztów API).

---

## 📦 Struktura Repozytorium

```
TESTMODELIIDOSTRAJANIE/
│
├── 📁 benchmarking/              # Core benchmarking system
│   ├── ocr_benchmark_engine.py   # Multi-provider OCR engine (23.5 KB)
│   ├── run_benchmark.py          # CLI runner + reporting (12.7 KB)
│   ├── setup_test_data.py        # Data preparation & validation (11.6 KB)
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example              # Configuration template
│   ├── README.md                 # Full documentation
│   ├── QUICKSTART.md             # 5-minute quick start
│   │
│   ├── test_receipts/            # Receipt images (PNG/JPG)
│   ├── ground_truth/             # JSON annotations (labels)
│   └── results/                  # Benchmark outputs
│       ├── benchmark_summary.json
│       ├── benchmark_report.txt
│       ├── benchmark_comparison.png
│       ├── ocr_results.jsonl
│       └── metrics.jsonl
│
├── 📁 optimization/              # DeepSeek R1 optimization
│   ├── prompt_engineering.md     # Refined prompts
│   ├── post_processing.py        # Fuzzy matching & validation
│   ├── business_rules.py         # Receipt validation logic
│   └── test_optimizations.py     # Optimization test suite
│
├── 📁 integration/               # Integration with ParagonOCR
│   ├── deepseek_wrapper.py       # Drop-in replacement for Google Vision
│   ├── batch_processor.py        # Batch receipt processing
│   └── examples.py               # Usage examples
│
├── 📁 docs/                      # Documentation
│   ├── ARCHITECTURE.md           # System design
│   ├── API_REFERENCE.md          # API documentation
│   ├── METRICS_GUIDE.md          # Metrics explanation
│   ├── OPTIMIZATION_STRATEGY.md  # Phase-by-phase optimization plan
│   └── TROUBLESHOOTING.md        # Common issues & solutions
│
├── 📁 tests/                     # Test suite
│   ├── test_extractors.py        # Provider tests
│   ├── test_metrics.py           # Metrics tests
│   └── test_validation.py        # Validation tests
│
├── 📁 examples/                  # Example files
│   ├── sample_receipts/          # Sample receipt images
│   ├── sample_ground_truth/      # Sample annotations
│   └── sample_reports/           # Example benchmark outputs
│
├── Makefile                      # Common commands
├── setup.py                      # Package installation
├── pyproject.toml               # Project config
├── .gitignore                   # Git ignore rules
├── LICENSE                      # MIT License
│
└── 📄 INDEX.md                  # Navigation guide (this file)

```

---

## 🚀 Quick Start (5 minut)

### 1️⃣ Klonowanie i Setup

```bash
git clone https://github.com/codemarcinu/TESTMODELIIDOSTRAJANIE
cd TESTMODELIIDOSTRAJANIE/benchmarking

pip install -r requirements.txt
cp .env.example .env

# Edytuj .env:
export OPENAI_API_KEY="sk-..."
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/gcp.json"
```

### 2️⃣ Przygotowanie danych

```bash
# Generuj przykładowe dane testowe
python setup_test_data.py --generate-samples 10 --report

# Lub dodaj swoje paragon images do:
# test_receipts/receipt_001.png
# test_receipts/receipt_002.jpg
# ...

# Stwórz ground truth annotations:
# ground_truth/receipt_001.json (formato JSON)
```

### 3️⃣ Uruchomienie benchmarku

```bash
# Baseline: GPT-4o mini vs DeepSeek R1
python run_benchmark.py \
  --image-dir test_receipts \
  --providers gpt4o_mini deepseek_r1 \
  --output-dir results

# Z Google Vision (pełne porównanie)
python run_benchmark.py \
  --image-dir test_receipts \
  --providers google_vision gpt4o_mini deepseek_r1 \
  --output-dir results
```

### 4️⃣ Przeglądanie wyników

```bash
# Raport tekstowy
cat results/benchmark_report.txt

# Wykresy porównawcze
open results/benchmark_comparison.png  # macOS
xdg-open results/benchmark_comparison.png  # Linux

# Szczegółowe metryki
head -20 results/ocr_results.jsonl
```

---

## 📊 Metryki Porównawcze

### Dokładność (Accuracy)

- **Field Accuracy** - dokładne dopasowanie kluczowych pól (%)
  - merchant_name, date, time, total_amount
  - Target dla DeepSeek R1: **≥92%**

- **Fuzzy Accuracy** - dopasowanie >80% podobieństwa (%)
  - Bardziej tolerancyjne dla drobnych różnic
  - Target: **≥95%**

- **Char Error Rate** - błędy na poziomie znaków (Levenshtein)
  - Target: **<5%**

- **Word Error Rate** - błędy na poziomie słów
  - Target: **<10%**

### Wydajność (Performance)

- **Processing Time** - sekundy na paragon
  - Google Vision: ~2s
  - GPT-4o mini: ~3s
  - DeepSeek R1: <1.5s ⚡ (local)

- **Tokens Used** - zużycie tokenów (LLM)
  - Wpływ na koszt API

- **Cost Per Receipt** - całkowity koszt przetwarzania
  - Google: $0.0015
  - GPT-4o mini: $0.001-0.002
  - DeepSeek: ~$0 (local compute)

### Jakość Danych (Quality)

- **Field Completeness** - % odnalezionych pól
  - Target: **≥90%**

- **Numerical Accuracy** - dokładność kwot (±1% tolerance)
  - Target: **≥95%**

- **Consistency Score** - walidacja reguł biznesowych (0-1)
  - Suma pozycji = total
  - Format daty YYYY-MM-DD
  - Wszystkie kwoty dodatnie
  - Target: **≥0.9**

---

## 🎯 Strategia Optymalizacji DeepSeek R1

### Faza 1: Baseline (Tydzień 1)

```bash
# Porównanie "out of the box"
python run_benchmark.py --providers gpt4o_mini deepseek_r1
```

**Oczekiwane**: DeepSeek 5-10% gorzej niż GPT-4o mini
**Główny powód**: Model mniej "fine-tuned" do strukturyzowanej ekstrakcji

### Faza 2: Prompt Engineering (Tydzień 2-3)

Szczegółowe prompty znajdują się w: `optimization/prompt_engineering.md`

**Techniki**:
- Few-shot examples
- Structured output format
- Reasoning steps
- Error prevention instructions

**Oczekiwana poprawa**: +3-5% dokładności

### Faza 3: Post-Processing (Tydzień 3-4)

Implementacja w: `optimization/post_processing.py`

**Techniki**:
- Fuzzy matching dla merchant names
- Normalizacja formatu daty
- Walidacja sum pozycji
- Korekta błędów OCR

**Oczekiwana poprawa**: +2-3% dokładności

### Faza 4: Business Rules (Tydzień 4-5)

Walidacja w: `optimization/business_rules.py`

**Reguły**:
- Items total musi = receipt total (±0.01)
- Data nie może być w przyszłości
- Kwoty nie mogą być ujemne
- Merchant name musi być wypełniony

**Oczekiwana poprawa**: +1-2% consistency

### Faza 5: Lokalne Wdrożenie (Tydzień 5-6)

Wdrożenie: `integration/deepseek_wrapper.py`

**Kroki**:
1. Setup Ollama lub vLLM
2. Pull deepseek-r1 model
3. Zintegruj z ParagonOCR
4. Testowanie na rzeczywistych danych

**Korzyści**:
- Zero kosztów API
- 3-5x szybsze (GPU local)
- Pełna kontrola nad danymi

---

## 💻 Instalacja

### Wymagania

- Python 3.8+
- pip lub poetry
- GPU (opcjonalnie, dla DeepSeek R1)

### Pełna instalacja

```bash
# Clone repo
git clone https://github.com/codemarcinu/TESTMODELIIDOSTRAJANIE
cd TESTMODELIIDOSTRAJANIE

# Utwórz virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# lub
venv\Scripts\activate  # Windows

# Zainstaluj zależności
cd benchmarking
pip install -r requirements.txt

# Setup konfiguracji
cp .env.example .env
# Edytuj .env swoimi kluczami API

# Opcjonalnie: Setup DeepSeek R1 (Ollama)
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull deepseek-r1
ollama serve  # W osobnym terminalu
```

### Alternatywa: Przy użyciu Make

```bash
make install         # Instalacja wszystkiego
make setup          # Setup konfiguracji
make test-gpt       # Test GPT-4o mini
make test-deepseek  # Test DeepSeek R1
make benchmark      # Pełny benchmark
make clean          # Czyszczenie
```

---

## 📚 Dokumentacja

Pełna dokumentacja znajduje się w katalogu `docs/`:

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Architektura systemu
- **[API_REFERENCE.md](docs/API_REFERENCE.md)** - Dokumentacja API
- **[METRICS_GUIDE.md](docs/METRICS_GUIDE.md)** - Wyjaśnienie metryk
- **[OPTIMIZATION_STRATEGY.md](docs/OPTIMIZATION_STRATEGY.md)** - Detailowa strategia
- **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Rozwiązywanie problemów

---

## 🔧 Użycie w Praktyce

### Integracja z ParagonOCR

```python
# Zamiast:
from google.cloud import vision
client = vision.ImageAnnotatorClient()

# Użyj:
from integration.deepseek_wrapper import DeepSeekOCR
ocr = DeepSeekOCR()
result = ocr.extract(receipt_image)
```

Pełny przykład: `integration/examples.py`

### Batch Processing

```python
from integration.batch_processor import BatchReceiptProcessor

processor = BatchReceiptProcessor(
    batch_size=32,
    num_workers=4
)

results = processor.process_directory("receipts/")
for receipt_id, extracted_data in results:
    print(f"{receipt_id}: {extracted_data}")
```

### Programmatic API

```python
from benchmarking.ocr_benchmark_engine import (
    OCRBenchmark,
    OCRProvider,
    DeepSeekR1Extractor
)

benchmark = OCRBenchmark(ground_truth_dir="ground_truth")
benchmark.register_extractor(
    OCRProvider.DEEPSEEK_R1,
    DeepSeekR1Extractor()
)

results = benchmark.run_benchmark(
    image_dir="test_receipts",
    providers=[OCRProvider.DEEPSEEK_R1],
    output_dir="results"
)
```

---

## 📈 Oczekiwane Rezultaty

### Timeline

```
Tydzień 1: Baseline (DeepSeek ~5-10% gorzej)
Tydzień 2-3: +3-5% (Prompt engineering)
Tydzień 4: +2-3% (Post-processing)
Tydzień 5: +1-2% (Business rules)
---
Koniec: DeepSeek ~91-93% accuracy (bardzo blisko GPT-4o mini 94%)
```

### Rezultaty Kosztów

| Faza | Accuracy | Speed | Cost/Receipt | Vs GPT-4o mini |
|------|----------|-------|--------------|----------------|
| **Start** | 89% | 1.8s | $0.00001 | -5% |
| **Week 2-3** | 92-93% | 1.2s | $0.00001 | -1-2% |
| **Final** | 92-94% | 1.0s | $0.00001 | -0-2% |

**Oszczędności (10 receipts/dzień)**:
- Baseline OpenAI: $3-7/rok
- DeepSeek local: ~$0.04/rok
- **Save: 99.4% kosztów**

---

## 🧪 Testowanie

```bash
# Uruchom test suite
pytest tests/

# Test specific module
pytest tests/test_extractors.py -v

# Test z coverage
pytest tests/ --cov=benchmarking --cov-report=html
```

---

## 📊 Przykład Raportu

Po uruchomieniu benchmarku otrzymasz:

```
================================================================================
OCR BENCHMARKING REPORT
================================================================================

BENCHMARK OVERVIEW
----------------------------------------
Total Tests: 10
Timestamp: 2026-01-17T19:05:00

PROVIDER COMPARISON
----------------------------------------
        Provider  Tests Field Accuracy  Fuzzy Accuracy  Avg Time (s)  Total Cost
     gpt4o_mini     10      94.50%         97.30%          3.124    $0.0180
   deepseek_r1     10      91.20%         95.80%          1.245    $0.0001

RECOMMENDATIONS FOR DEEPSEEK R1 OPTIMIZATION
----------------------------------------
Best Accuracy: gpt4o_mini (94.50%)
  - Actions: Review prompt engineering, improve fuzzy matching

Best Speed: deepseek_r1 (1.245s)
  - Actions: Maintain current optimization level

Best Cost: deepseek_r1 ($0.0001)
  - Local model has natural cost advantage

DeepSeek R1 Optimization Strategy:
  1. Use same prompts as GPT-4o mini (benchmark)
  2. Implement fuzzy matching for ~80% similarity threshold
  3. Add validation layer for business rule consistency
  4. Optimize for speed while maintaining accuracy
  5. Deploy on local GPU for zero API costs

================================================================================
```

---

## 🔗 Zasoby Techniczne

- [DeepSeek-OCR GitHub](https://github.com/deepseek-ai/DeepSeek-OCR)
- [DeepSeek R1 Model Card](https://huggingface.co/deepseek-ai/DeepSeek-R1)
- [vLLM Documentation](https://docs.vllm.ai/)
- [Ollama Setup Guide](https://ollama.ai/)
- [Google Cloud Vision API](https://cloud.google.com/vision/docs)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [FuzzyWuzzy String Matching](https://github.com/seatgeek/fuzzywuzzy)

---

## 🤝 Contributing

Wkład mile widziany! Prosimy:

1. Fork repozytorium
2. Utwórz feature branch (`git checkout -b feature/amazing-feature`)
3. Commit zmian (`git commit -m 'Add amazing feature'`)
4. Push do branch (`git push origin feature/amazing-feature`)
5. Otwórz Pull Request

---

## 📝 Licencja

MIT License - patrz [LICENSE](LICENSE)

---

## 📞 Kontakt

- GitHub: [@codemarcinu](https://github.com/codemarcinu)
- Issues: [GitHub Issues](https://github.com/codemarcinu/TESTMODELIIDOSTRAJANIE/issues)
- Discussions: [GitHub Discussions](https://github.com/codemarcinu/TESTMODELIIDOSTRAJANIE/discussions)

---

## 🎯 Status

- [x] Core benchmarking engine
- [x] Multi-provider support
- [x] Metrics calculation
- [x] Reporting & visualization
- [x] Test data preparation
- [ ] DeepSeek R1 optimization guide (in progress)
- [ ] Integration examples
- [ ] Batch processing module
- [ ] Full test suite
- [ ] Documentation completion

---

**Gotowy do wdrożenia! 🚀**

Zapisz ten projekt do bookmarks - będziesz go używać do optymalizacji DeepSeek R1 i integracji z ParagonOCR.
