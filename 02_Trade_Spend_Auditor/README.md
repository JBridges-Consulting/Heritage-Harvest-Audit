📊 Heritage Harvest | Automated Trade Spend Auditor
Agent 02 of the CPG Agentic Workflows Portfolio

🎯 The Business Challenge
In the fast-moving Salty Snacks category, manual trade-spend auditing is often the bottleneck between a Sales Rep and a Retail Buyer. Inconsistent margin calculations lead to "margin leakage" and delays in Joint Business Planning (JBP).

🚀 The Agentic Solution
This agent acts as a Commercial Logic Gate. It replaces manual spreadsheets with a cloud-synced dashboard that validates pricing against live COGS (Cost of Goods Sold) and margin guardrails.

Margin Guardrails: Instantly validates SKU-level profitability, forcing a professional 59.2% margin standard for approved items.

Live Cloud Integration: Syncs directly with Google Sheets (GCP), allowing sales teams to push local pricing updates to the dashboard with one click.

Automated Buyer Communication: Generates professional approval emails featuring explicit SKU ID and UPC identifiers for retail procurement teams.

🏗️ Technical Deep Dive
Frontend: Streamlit (Web UI) for real-time sales visibility.

Backend: Python 3.x using the Google Discovery API v4 for hardened data retrieval.

Security: Implemented Service Account authentication and specialized SSL handshake protocols to resolve complex decryption failures in enterprise environments.

Data Export: High-fidelity CSV/Excel engine for offline audit record-keeping.

📈 Evolution: Version 1.5.0
The latest build represents a "Production Hardened" version that solved critical deployment issues:

Fixed: SSL: WRONG_VERSION_NUMBER errors by enforcing specific API discovery endpoints.

Fixed: Margin display logic to ensure 0.60 precision appears correctly as a rounded 59.2% percentage string.

Added: "Submit" functionality for local-to-cloud data synchronization.