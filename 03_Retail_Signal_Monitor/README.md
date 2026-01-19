# Heritage Harvest | Field Intelligence ROI Engine 🥔

A strategic retail intelligence tool designed for National Account Managers to convert competitor shelf voids into Heritage Harvest revenue.

## 🚀 Overview
This application uses **GPT-4o Vision** to perform a real-time category visibility scan. It identifies competitor out-of-stocks (OOS), maps them to Heritage Harvest SKUs, and calculates the weekly revenue loss based on master pricing data.

## 🛠️ Key Features
* **Visual Signal Monitoring:** Detects shelf gaps and identifies competitor failures.
* **Master Data Integration:** Pulls exact `list_price` and `weekly_velocity` from `pricing_master_UPSPW.csv`.
* **Quantifiable Buyer Pitch:** Generates a data-driven "Challenger Sale" pitch for retailers.
* **Automated Delivery:** Sends a personalized Executive Summary directly to the Category Buyer.

## 📦 Setup
1. Clone this repository.
2. Ensure `pricing_master_UPSPW.csv` is in the root directory.
3. Add your `OPENAI_API_KEY` and SMTP email credentials to `.streamlit/secrets.toml`.
4. Run locally: `streamlit run app.py`