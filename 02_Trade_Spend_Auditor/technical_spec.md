# Technical Specification: Trade Spend Auditor

## 1. System Overview
A deterministic logic engine that validates commercial deal viability by combining LLM-based intent recognition with Python-based financial calculation.

## 2. Data Schema (pricing_master.csv)
- `list_price`: Standard wholesale price.
- `cogs`: Total cost of goods sold.
- `min_margin_threshold`: The "Floor" margin (decimal).
- `max_allowable_discount`: The "Ceiling" for trade spend (decimal).

## 3. Logic Gates (The Guardrails)
These gates ensure the agent remains "Internally Honest" and protects the P&L.

### Gate 1: Identification Confidence
- **Threshold:** 70% Fuzzy Match score.
- **Action:** If score < 70%, the agent triggers a `ClarificationRequest` instead of proceeding with math.

### Gate 2: Margin Protection
- **Formula:** `(Net_Price - COGS) / Net_Price`
- **Rule:** Must be ≥ `min_margin_threshold`.
- **Action:** If failed, trigger `CounterOfferLogic`.

### Gate 3: Discount Ceiling
- **Rule:** `requested_discount` must be ≤ `max_allowable_discount`.
- **Action:** Prevents brand erosion even if the margin is healthy.