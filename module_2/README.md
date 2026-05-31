# JHU Software Concepts – Module 2

## Graduate Admissions Data Pipeline: Scraping, Cleaning, and LLM Standardization

### Overview

This project implements an end-to-end data processing pipeline for graduate admissions results collected from The Grad Cafe.

The workflow consists of three major stages:

1. **Web Scraping** – Collect admissions records from The Grad Cafe.
2. **Data Cleaning** – Normalize fields and recover structured information from free-text comments using regular expressions.
3. **LLM Standardization** – Use a local Large Language Model (TinyLlama 1.1B) to generate standardized program and university names.

The final dataset contains **35,000 applicant records**.

---

## Workflow

```text
The Grad Cafe
      ↓
   scrape.py
      ↓
applicant_data.json
      ↓
    clean.py
      ↓
cleaned_applicant_data.json
      ↓
 TinyLlama Standardizer
      ↓
llm_extend_applicant_data.jsonl
```

---

# Stage 1 – Web Scraping

## Strategy

The scraper collects admission records from The Grad Cafe survey pages and extracts structured information from the website.

Fields collected include:

* Program
* University
* Degree
* Admission Status
* GPA
* GRE Scores
* Application Term
* Comments
* Original Result URL

---

## Discovering Structured Data Inside the HTML

During development, the first approach considered was traditional HTML scraping using CSS selectors and BeautifulSoup.

Inspection of the page source revealed that the admissions results were already embedded inside a JSON payload stored in:

```html
<div id="app" data-page="...">
```

The `data-page` attribute contains a large JSON object describing the page contents, including the admissions records displayed on the page.

Instead of extracting individual fields from rendered HTML elements, the scraper:

1. Locates the `div` with `id="app"`.
2. Extracts the `data-page` attribute.
3. Decodes HTML entities.
4. Parses the JSON using Python's `json` library.
5. Retrieves admissions records directly from the structured JSON.

Workflow:

```text
HTML Page
    ↓
<div id="app" data-page="...">
    ↓
Extract data-page
    ↓
HTML decode
    ↓
json.loads()
    ↓
Admissions records
```

### Why This Approach Was Chosen

Using the embedded JSON offered several advantages:

* More reliable than parsing visual HTML elements
* Less sensitive to website layout changes
* Cleaner extraction of structured fields
* Reduced parsing complexity
* Direct access to metadata not visible on the page

For example, internal IDs, decision dates, and additional metadata were already available within the JSON payload and could be preserved inside the `raw_record` field.

This approach treats the webpage as a structured data source rather than a visual document and results in a more robust scraper.

---

# robots.txt Compliance

Before scraping, the website's robots.txt file was reviewed.

Evidence is included in this repository as:

```text
screenshot.jpg
```

The robots.txt file can be found at:

```text
https://www.thegradcafe.com/robots.txt
```

The scraper only accesses publicly available survey pages:

```text
https://www.thegradcafe.com/survey?page=...
```

During review of robots.txt, several restricted paths were identified, including:

```text
/signin
/register
/forgot-password
/reset-password
/confirm-password
/verify-email
/profile
```

The scraper does not access any of these restricted paths.

The robots.txt file does not disallow access to:

```text
/survey
/result
```

which are the public pages used in this project.

The scraper only requests publicly available survey pages and extracts admissions records embedded in the page source. No login-protected content, private information, CAPTCHAs, access controls, or rate-limit bypass techniques were used.

To reduce load on the website, the scraper includes:

* A delay between requests
* Retry logic for temporary server-side failures
* Resume functionality to avoid unnecessary re-scraping

Therefore, the scraper was designed to operate within the permissions expressed by the site's robots.txt file.

---

## Reliability Improvements

Large scraping jobs occasionally encountered temporary server-side failures (HTTP 500 errors).

To improve reliability, the scraper was enhanced with:

* Automatic retry logic
* Delays between requests
* Incremental saving after each page
* Resume capability after interruption

Resume functionality allows the scraper to continue from the last successful page rather than restarting from page one.

These improvements proved essential because long scraping runs occasionally failed after collecting thousands of records.

Using the resume functionality, the scraper successfully recovered and ultimately collected the full dataset of 35,000 records.

---

# Stage 2 – Data Cleaning

## Cleaning Strategy

Before applying an LLM, a lightweight rule-based cleaning approach was used.

Cleaning steps included:

* Whitespace normalization
* Comment text cleanup
* Missing value handling
* GPA extraction from comments using regular expressions

The original applicant information is preserved. Additional cleaned fields are added without overwriting the source data.

---

## Why Use Regex?

Regular expressions are:

* Fast
* Deterministic
* Easy to validate
* Computationally inexpensive

Many common patterns can be extracted more reliably using simple rules than by invoking an LLM.

Examples:

```text
GPA 3.75
GPA: 3.9/4
Grad GPA 3.85
```

can be detected with high precision using regular expressions.

For this reason, regex was used as the first stage of cleaning before introducing a more expensive LLM-based approach.

---

## Cleaning Results

| Metric                       | Result |
| ---------------------------- | ------ |
| Input Records                | 35,000 |
| Output Records               | 35,000 |
| Records Prepared for LLM     | 35,000 |
| Comment Fields Cleaned       | 1,116  |
| Missing GPA Values Recovered | 3      |

Example:

**Before**

```text
GPA: None
Comments: M.S. in Computer Science GPA: 3.9/4
```

**After**

```text
GPA: None
gpa_from_comments: 3.9
```

---

# Stage 3 – LLM Standardization

## Goal

Applicants frequently enter program and university names inconsistently.

Examples:

```text
Information, McG
Comp Sci, UIUC
Bio, MIT
```

The goal of the LLM step is to generate standardized program and university names in additional output fields.

The original applicant-provided fields are preserved.

---

## Why Use a Local LLM?

A local model was selected because it:

* Requires no API costs
* Is fully reproducible
* Can operate offline after setup
* Demonstrates deployment of an open-source LLM

This project uses:

```text
TinyLlama 1.1B Chat
GGUF format
llama-cpp-python
```

---

## Engineering Effort Required for the LLM Pipeline

Getting the local LLM environment operational required substantially more effort than expected.

### Challenges Encountered

#### 1. Python Compatibility

The project initially used Python 3.14.

However, `llama-cpp-python` did not provide compatible binaries, requiring creation of a separate Python 3.11 virtual environment.

#### 2. Compiler Installation

The LLM runtime required local compilation support.

To resolve this:

* Visual Studio Build Tools were installed
* MSVC compiler tools were installed
* Windows SDK components were installed

#### 3. Architecture Issues

Initial installations produced:

```text
WinError 193
%1 is not a valid Win32 application
```

This issue was caused by architecture mismatches between Python, compiled DLLs, and the llama-cpp runtime.

The issue was ultimately resolved by rebuilding the environment inside the Visual Studio Developer Command Prompt.

#### 4. Model Download

The TinyLlama model (~669 MB) had to be downloaded and configured locally before inference could begin.

---

## Why Only 1,000 Records Were Processed by the LLM

The complete dataset contains 35,000 records.

However, local LLM inference proved computationally expensive.

Observed performance:

```text
Approximately 30 minutes per 1,000 records
```

Estimated runtime for the full dataset:

```text
17–18 hours
```

Given the educational goals of the assignment, a representative subset of 1,000 records was processed to demonstrate functionality while keeping runtime manageable.

This subset was sufficient to validate the workflow and evaluate LLM behavior.

---

## Observations and Limitations of the LLM Approach

### Strengths

The model successfully standardized many abbreviated or informal entries and generated more consistent naming conventions than simple rule-based approaches.

The LLM was particularly useful for:

* Abbreviation expansion
* Capitalization normalization
* Informal naming conventions
* Program name standardization

### Limitations

#### 1. Computational Cost

Inference was significantly slower than regex-based processing.

Rule-based cleaning completed in minutes, while LLM processing required approximately:

```text
30 minutes per 1,000 records
```

on local CPU hardware.

#### 2. Hallucination Risk

The model occasionally generated plausible but potentially incorrect standardizations.

For example:

```text
Public Policy, University of Massachusetts
```

might be standardized as:

```text
Public Policy
University of Massachusetts Lowell
```

even though the original record did not explicitly specify the campus.

Such outputs may appear reasonable but cannot always be verified automatically.

#### 3. Not All Records Require an LLM

Many entries were already standardized.

Applying an LLM to such records introduces computational cost without meaningful benefit.

A practical production workflow would likely:

1. Apply deterministic cleaning first.
2. Identify ambiguous records.
3. Apply the LLM only when necessary.

---
---



# Reproducing the Pipeline

## Environment Setup

Install the required Python packages:

```bash
pip install -r requirements.txt
```

For the LLM component, a separate Python 3.11 virtual environment was used because `llama-cpp-python` was not compatible with the Python 3.14 environment used during development.

---

## Step 1: Run the Scraper

Generate the raw applicant dataset:

```bash
python scrape.py
```

Output:

```text
applicant_data.json
```

The scraper includes:

- Pagination support
- Retry logic for temporary HTTP failures
- Resume functionality after interruption
- Delays between requests to comply with robots.txt guidance

If an existing `applicant_data.json` file is present, the scraper will automatically resume from the last successfully collected page.

---

## Step 2: Run Data Cleaning

Generate the cleaned dataset:

```bash
python clean.py
```

Outputs:

```text
cleaned_applicant_data.json
cleaning_log.txt
```

This step performs:

- Text normalization
- Missing value handling
- GPA extraction using regular expressions
- Preparation of records for LLM standardization

---

## Step 3: Run Local LLM Standardization

Navigate to the LLM directory:

```bash
cd llm_hosting
```

Run the standardization pipeline:

```bash
python app.py --file ..\cleaned_applicant_data.json --stdout > ..\llm_extend_applicant_data.jsonl
```

Output:

```text
llm_extend_applicant_data.jsonl
```

This project uses:

```text
TinyLlama 1.1B Chat
GGUF format
llama-cpp-python
```

Due to computational cost, only the first 1,000 records were processed through the LLM for demonstration purposes. Processing the full 35,000-record dataset would require approximately 17–18 hours on the development machine.

---

## Files Included in Submission

| File | Purpose |
|--------|--------|
| scrape.py | Web scraping pipeline |
| clean.py | Data cleaning pipeline |
| applicant_data.json | Raw scraped dataset (35,000 records) |
| cleaned_applicant_data.json | Cleaned dataset |
| cleaning_log.txt | Cleaning summary and examples |
| llm_extend_applicant_data.jsonl | LLM standardization output |
| llm_hosting/app.py | TinyLlama standardization script |
| requirements.txt | Python dependencies |
| README.md | Project documentation |
| screenshot.jpg | robots.txt compliance evidence |

---



# Conclusion

This project demonstrates an end-to-end data engineering workflow involving:

* Large-scale web scraping
* Data cleaning and normalization
* Local LLM deployment
* Structured data enrichment

The final pipeline successfully collected and processed **35,000 graduate admissions records**, while illustrating both the strengths and limitations of using a small local language model for data standardization tasks.

In addition to the final dataset, the project highlights important engineering considerations including robustness, fault recovery, reproducibility, computational efficiency, and the tradeoffs between rule-based and LLM-based approaches.
