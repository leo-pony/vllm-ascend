# TRAE Context: Issue Identification for vLLM Ascend

## Overview
This directory contains the results and artifacts from an issue analysis session performed on the vLLM Ascend repository.

The goal was to identify valid open bugs (filtering out features, questions, PRs, and non-regression performance requests).

## Artifacts

### 1. Data Files
- **`vllm_issues_filtered.json`**: The complete JSON database of all identified valid issues (merged from both tasks).
- **`vllm_ascend_bugs.csv`**:
  - **Scope**: Issues with IDs between `4067` and `7051`.
  - **Count**: 148 issues.
  - **Columns**: `issue_number`, `title`, `url`, `labels`, `created_at`.
- **`vllm_ascend_bugs_page25_plus.csv`**:
  - **Scope**: Issues from Page 25 onwards (older issues), without ID range restriction.
  - **Count**: 100 issues.
  - **Columns**: Same as above.

### 2. Logic Script
- **`issue_analyzer_logic.py`**: A Python script containing the core logic used for:
  - Fetching issues from GitHub (handling pagination and HTML parsing).
  - Filtering rules (keywords, labels, regression detection).
  - Exporting to CSV.
  - Note: This script is provided for reference/reproduction. During the session, specialized scripts (`fetch_all_issues.py`, `fetch_page25_plus.py`) were used and then deleted.

## Filtering Rules Applied
1. **Status**: Open issues only.
2. **Exclusions**:
   - Pull Requests.
   - Issues with prefixes like `[usage]`, `[question]`, `[misc]`.
   - Titles containing keywords like "feature", "support", "doc", "test", "question", "how to".
   - Performance issues *unless* they explicitly mention "regression", "degradation", or "slower".
   - Chinese keywords for non-bugs (e.g., "咨询", "求助", "是否支持").

## Execution Environment
- **Date**: 2026-03-10
- **Proxy**: `http://127.0.0.1:7890` (for GitHub access)
