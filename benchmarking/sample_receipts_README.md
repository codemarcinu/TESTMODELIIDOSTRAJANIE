# Rzeczywiste Paragony Polskie

To są rzeczywiste paragony ze sklepów Lidl, Auchan i Biedronka (dane zmodyfikowane).

## Pliki

### Zdjęcia (test_receipts/)
- `Lidl20250131.jpeg` - Lidl z 31.01.2025, razem: 83,05 PLN
- `20250626LIDL.jpeg` - Lidl z 26.05.2025, razem: 53,94 PLN
- `20250121_063301.pdf` - Auchan z 21.01.2025
- `auchan.pdf` - Auchan
- `Biedra20251118.pdf` - Biedronka z 18.11.2025

### Ground Truth JSON (ground_truth/)
- `lidl_20250131.json`
- `lidl_20250526.json` 
- `auchan_20250121.json`
- `biedronka_20251118.json`

## Cechy Paragonów

### Lidl
- Format: czytelny, jasny
- Struktura: nazwa → towary → rabaty → razem
- Specjalność: Lidl Plus kupony, promocje
- VAT: Rozbite na PTU_A i PTU_C

### Auchan
- Format: standard
- Struktura: klasyczna
- Specjalność: rabaty

### Biedronka
- Format: rozbity na promocje
- Struktura: rabat TANIEI
- Specjalność: liczne promocje i kody rabatowe

## Użycie do Testów

```bash
# Test OCR extraction
python benchmarking/extract_ocr_from_samples.py

# Test pipeline na rzeczywistych danych
python main.py pipeline --image benchmarking/test_receipts/Lidl20250131.jpeg

# Testuj prompt versions
python main.py test-prompts --versions v1 v2 v3 v4 v5 v6

# Porównaj z ground truth
python main.py tune --ground-truth-dir benchmarking/ground_truth
```

## Metryki

Uż teraz możesz zmierzyć **rzeczywistą dokładność** na polskich paragonach!

- **Merchant name**: Lidl vs LidI vs LIDL (OCR errors)
- **Date**: 2025-05-26 vs 2025-26-05 (format variations)
- **Items**: ~7-9 produktów per receipt
- **Tax**: VAT 20-23% (różne sklepach)
- **Total**: 53,94 PLN - 83,05 PLN

## Następne Kroki

1. Konwertuj zdjęcia na OCR text (Google Vision)
2. Testuj wszystkie 6 prompt versions
3. Zmierz accuracy vs ground truth
4. Wybierz najlepszy prompt
5. Deploy do ParagonOCR
