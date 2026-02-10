---
schema: "2.0"
name: data-pipeline
workdir: pipeline-output
---

# Data Processing Pipeline

A notebook mixing shell commands and AI tasks for data processing.

<shell id="setup-dirs">
mkdir -p pipeline-output/{raw,processed,reports}
echo "Directory structure created"
</shell>

<task id="generate-data">
Create a sample CSV file at pipeline-output/raw/sales.csv with:
- Headers: date, product, quantity, price, region
- 50 rows of realistic sales data
- Dates spanning the last 30 days
- Products: Widget, Gadget, Gizmo, Thingamajig
- Regions: North, South, East, West
- Prices between $10-$500
- Quantities between 1-100
</task>

<shell id="preview-data">
echo "=== Raw Data Preview ==="
head -10 pipeline-output/raw/sales.csv
echo ""
echo "=== Row Count ==="
wc -l pipeline-output/raw/sales.csv
</shell>

<task id="transform">
Create a Node.js script at pipeline-output/transform.js that:
- Reads raw/sales.csv
- Adds a 'total' column (quantity * price)
- Adds a 'month' column extracted from date
- Filters out any rows with quantity < 5
- Writes the result to processed/sales-transformed.csv
- Prints summary statistics (total rows, total revenue)
</task>

<shell id="run-transform">
cd pipeline-output && node transform.js
</shell>

<task id="analyze">
Create a Python script at pipeline-output/analyze.py that:
- Reads processed/sales-transformed.csv
- Generates summary statistics:
  - Total revenue by product
  - Total revenue by region
  - Average order value
  - Top 5 highest value transactions
- Outputs results to reports/summary.json
- Also creates a simple text report at reports/summary.txt
</task>

<shell id="run-analysis">
cd pipeline-output && python analyze.py
</shell>

<shell id="show-results">
echo "=== Analysis Results ==="
cat pipeline-output/reports/summary.txt
echo ""
echo "=== JSON Output ==="
cat pipeline-output/reports/summary.json | head -30
</shell>

<note id="done">
## Pipeline Complete!

**Generated files:**
- `raw/sales.csv` - Original data (50 rows)
- `processed/sales-transformed.csv` - Cleaned & enriched data
- `reports/summary.json` - Machine-readable analysis
- `reports/summary.txt` - Human-readable report
- `transform.js` - Node.js transformation script
- `analyze.py` - Python analysis script

**Rerun anytime:**
```bash
cd pipeline-output
node transform.js && python analyze.py
```
</note>
