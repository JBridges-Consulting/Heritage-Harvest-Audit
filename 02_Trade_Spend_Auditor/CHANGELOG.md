[2026-01-15] Initial project structure created. Defined business objectives and created pricing_master.csv in Shared_Assets.
[2026-01-15 - PM Session] Integrated 'thefuzz' library. Implemented fuzzy matching logic to map customer intent to SKU master data.
## [1.1.0] - 2026-01-15

### Added
- Created core `audit_negotiation` logic to calculate deal profitability.
- Integrated `find_best_sku_match` for fuzzy product identification.
- Added automated test block to verify CSV data loading and margin calculations.

### Changed
- **Architecture Pivot:** Replaced `pandas` dependency with Python's built-in `csv` module to improve portability and resolve environment-specific installation conflicts on Apple Silicon.
- Updated path handling to use `os.path.join` for better cross-platform compatibility between local development and portfolio deployment.

### Fixed
- Resolved `ModuleNotFoundError` by removing heavy external dependencies.
- Fixed `Errno 2` file path errors by implementing relative directory detection.
## [1.2.0] - 2026-01-15

### Added
- **Bulk Audit Engine:** Implemented a portfolio-wide audit loop that iterates through all SKUs in the pricing master database.
- **Visual Reporting:** Added status icons (✅/❌) and aligned terminal formatting for professional, at-a-glance deal review.
- **Automated Summary:** Included a final tally of Approved vs. Denied deals to provide high-level commercial visibility.

### Changed
- **Logic Refinement:** Shifted from single-SKU testing to dynamic iteration using the `load_pricing_data` result set.
- **Improved UX:** Optimized terminal output with column padding for better readability of product names and margin percentages.

### Fixed
- Resolved `if __name__ == "__main__":` redundancy to ensure the full audit loop executes correctly.
- Stabilized directory navigation by standardizing the `cd` execution path.

## [1.4.0] - 2026-01-15

### Added
- **Enterprise Data Schema:** Expanded CSV architecture to include `upc` (GTIN-12) and internal `sku_id`, aligning the tool with industry-standard retail data requirements.
- **Brand Identity:** Integrated "Heritage Harvest Snacks" branding across all automated outputs to simulate a realistic corporate environment.
- **Consolidated Notification Logic:** Refactored email engine to generate a single "Portfolio Approval" report, reducing communication friction and improving email deliverability to Outlook/Corporate clients.
- **Advanced UX Reporting:** Enhanced the HTML dashboard with multi-column support for SKU/UPC tracking and auto-launch capabilities.

### Changed
- **Salty Snacks Focus:** Refined the data set to a specific category (Salty Snacks) to simulate a realistic Account Manager/Buyer negotiation scenario.
- **SMTP Optimization:** Upgraded email headers (Priority, Display Names) to improve inbox placement and professional presentation.

### Fixed
- **Indentation & Syntax:** Resolved execution blocks that were causing terminal crashes during bulk processing.
- **Character Encoding:** Standardized UTF-8 across all file I/O to prevent ASCII-related email crashes.
# Changelog - Heritage Harvest Trade Auditor

All notable changes to the "Agent 02" Trade Spend Auditor will be documented in this file.

## [1.2.0] - 2026-01-15
### Added
- **Cloud Database Integration**: Migrated from local `pricing_master.csv` to live Google Sheets API.
- **Secure Authentication**: Implemented Google Service Account (JSON) for encrypted backend access to commercial data.
- **Interactive Sales Portal**: Developed `app.py` using Streamlit to provide a web-based UI for sales reps.
- **Live SKU Lookups**: UI now dynamically pulls UPC, SKU ID, and Margin thresholds from the cloud.

### Fixed
- **API Connectivity**: Resolved "403: Sheets API Not Enabled" error by activating Google Sheets service in GCP Console.
- **Path Management**: Corrected file naming and directory issues for `service_account.json` and `app.py`.
- **Environment Isolation**: Configured Python 3.15 virtual environment (.venv) to prevent dependency conflicts.

### Security
- **Credential Protection**: Added `service_account.json` and `.venv/` to `.gitignore` to prevent private key exposure on public repositories.