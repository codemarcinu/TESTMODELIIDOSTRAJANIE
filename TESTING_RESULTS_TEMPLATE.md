# Wyniki Testow - Rzeczywiste Paragony

**Data:** 2026-01-17  
**Tester:** Marcin  
**Samples:** 4 rzeczywiste paragony (Lidl x2, Auchan, Biedronka)

---

## 📊 Podsumowanie

| Metryka | Wartosc |
|---------|----------|
| Total receipts tested | 4 |
| Prompts tested | 6 (v1-v6) |
| Avg accuracy | TBD |
| Best prompt | TBD |
| Avg processing time | TBD |
| Total cost | TBD |

---

## 🎯 Wyniki per Paragon

### Lidl 20250131 (83,05 PLN)

**Ground Truth:**
- Merchant: Lidl sp. z o. o.
- Date: 2025-01-31
- Items: 9
- Total: 83,05 PLN

**Prompt Accuracy:**

| Prompt | Accuracy | Time | Notes |
|--------|----------|------|-------|
| v1 | TBD % | TBD s | |
| v2 | TBD % | TBD s | ⭐ Recommended |
| v3 | TBD % | TBD s | |
| v4 | TBD % | TBD s | |
| v5 | TBD % | TBD s | |
| v6 | TBD % | TBD s | |

### Lidl 20250526 (53,94 PLN)

**Ground Truth:**
- Merchant: Lidl sp. z o. o.
- Date: 2025-05-26
- Items: 7
- Total: 53,94 PLN

**Prompt Accuracy:**

| Prompt | Accuracy | Time | Notes |
|--------|----------|------|-------|
| v1 | TBD % | TBD s | |
| v2 | TBD % | TBD s | |
| v3 | TBD % | TBD s | |
| v4 | TBD % | TBD s | |
| v5 | TBD % | TBD s | |
| v6 | TBD % | TBD s | |

### Auchan 20250121 (83,05 PLN)

**Ground Truth:**
- Merchant: Auchan
- Date: 2025-01-21
- Items: 7
- Total: 83,05 PLN

**Prompt Accuracy:**

| Prompt | Accuracy | Time | Notes |
|--------|----------|------|-------|
| v1 | TBD % | TBD s | |
| v2 | TBD % | TBD s | |
| v3 | TBD % | TBD s | |
| v4 | TBD % | TBD s | |
| v5 | TBD % | TBD s | |
| v6 | TBD % | TBD s | |

### Biedronka 20251118 (53,94 PLN)

**Ground Truth:**
- Merchant: Biedronka
- Date: 2025-11-18  
- Items: 7
- Total: 53,94 PLN

**Prompt Accuracy:**

| Prompt | Accuracy | Time | Notes |
|--------|----------|------|-------|
| v1 | TBD % | TBD s | |
| v2 | TBD % | TBD s | |
| v3 | TBD % | TBD s | |
| v4 | TBD % | TBD s | |
| v5 | TBD % | TBD s | |
| v6 | TBD % | TBD s | |

---

## 📈 Field-Level Accuracy

| Field | v1 | v2 | v3 | v4 | v5 | v6 |
|-------|----|----|----|----|----|---------|
| merchant_name | TBD | TBD | TBD | TBD | TBD | TBD |
| date | TBD | TBD | TBD | TBD | TBD | TBD |
| total_amount | TBD | TBD | TBD | TBD | TBD | TBD |
| items_count | TBD | TBD | TBD | TBD | TBD | TBD |
| payment_method | TBD | TBD | TBD | TBD | TBD | TBD |

---

## 🔍 Analiza Błędów

### Najczęstsze Błędy:
- TBD

### OCR Issues:
- TBD

### DeepSeek Hallucinations:
- TBD

### Math Validation:
- TBD

---

## 💰 Cost Analysis

```
Google Vision API:   TBD (4 receipts × $0.0015)
GPT-4o mini:         TBD (4 receipts × avg tokens)
DeepSeek R1:         FREE (local inference)
───────────────────────────────
Total per receipt:   TBD
Total for 4:         TBD
```

---

## ⏱️ Performance

```
Google Vision:    TBD s avg
GPT-4o mini:      TBD s avg
DeepSeek R1:      TBD s avg (v1-v6 varies)
───────────────────────────
Total pipeline:   TBD s avg
Throughput:       TBD receipts/hour
```

---

## ✅ Rekomendacje

1. **Best Overall**: v** (accuracy TBD%, time TBD s)
2. **Best for Speed**: v** (TBD s)
3. **Best for Accuracy**: v** (TBD %)
4. **Best Cost/Benefit**: v** (TBD)

---

## 🎯 Next Steps

- [ ] Deploy chosen prompt (v**) to production
- [ ] Monitor accuracy on new receipts
- [ ] Collect more samples if accuracy <90%
- [ ] Fine-tune prompt if needed
- [ ] Integrate with ParagonOCR

---

**Status:** [TESTING / DRAFT / READY FOR DEPLOYMENT]
