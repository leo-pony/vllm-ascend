import requests
import json
import re
import os
import sys
from collections import defaultdict

# Configuration
REPO_OWNER = "vllm-project"
REPO_NAME = "vllm-ascend"
API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"
HTML_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/issues"

# Proxy Configuration
PROXY_URL = "http://127.0.0.1:7890"
proxies = {
    "http": PROXY_URL,
    "https": PROXY_URL,
}

# Headers for API
api_headers = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "Trae-Agent-Analysis"
}

# Headers for HTML Scraping (Browser-like)
html_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

def fetch_issues_api():
    """Fetch issues using GitHub API"""
    params = {
        "state": "open",
        "per_page": 100,
        "page": 1,
        "sort": "created",
        "direction": "desc"
    }
    
    print(f"Fetching issues from API: {API_URL}...")
    try:
        response = requests.get(API_URL, headers=api_headers, params=params, proxies=proxies, timeout=30, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API fetch failed: {e}")
        return None

def fetch_issues_html():
    """Fetch issues by scraping GitHub HTML page (Fallback)"""
    print(f"Fetching issues from HTML: {HTML_URL}...")
    try:
        # Fetching up to 4 pages to get ~100 issues (25 per page usually)
        all_issues = []
        for page in range(1, 5):
            url = f"{HTML_URL}?q=is%3Aopen+is%3Aissue&page={page}"
            response = requests.get(url, headers=html_headers, proxies=proxies, timeout=30, verify=False)
            response.raise_for_status()
            
            page_issues = parse_html_issues(response.text)
            if not page_issues:
                break
            all_issues.extend(page_issues)
            if len(all_issues) >= 100:
                break
                
        return all_issues[:100]
    except Exception as e:
        print(f"HTML fetch failed: {e}")
        return None

def parse_html_issues(html):
    """Parse issues from HTML content using regex"""
    issues = []
    # Regex to find issue rows
    # Look for: <a id="issue_1234_link" ...>Title</a>
    # And labels
    
    # We'll do a simple split by "js-issue-row" if possible, or just find all links
    # Finding links: id="issue_(\d+)_link" href="([^"]+)" ... >(.*?)</a>
    
    issue_links = re.findall(r'<a id="issue_(\d+)_link"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
    
    for issue_id, url_suffix, title_html in issue_links:
        title = re.sub(r'<.*?>', '', title_html).strip()
        url = "https://github.com" + url_suffix
        
        # Labels are hard to associate with regex on full HTML. 
        # For now, we might miss labels in HTML mode, so filtering will rely heavily on Title.
        # But we can try to find labels if we split by row.
        labels = [] 
        
        issues.append({
            "number": int(issue_id),
            "title": title,
            "html_url": url,
            "labels": labels, # List of dicts or strings
            "body": "" # Body not available in list view
        })
    return issues

def is_target_bug(issue):
    """
    Filter logic:
    - Keep: Bugs, Regressions
    - Filter: Features, RFC, NewModel, Performance (Optimization)
    """
    title = issue["title"].lower()
    
    # Extract labels (handle API dicts or HTML strings)
    labels = []
    if issue.get("labels"):
        for l in issue["labels"]:
            if isinstance(l, dict):
                labels.append(l["name"].lower())
            else:
                labels.append(str(l).lower())
    
    combined_text = title + " " + " ".join(labels)
    
    # 1. Explicit Exclusions (Features, RFCs, New Models)
    exclude_keywords = [
        "feature", "feat:", "[feat]", "enhancement", 
        "rfc", "[rfc]", "proposal",
        "new model", "support model", "add model", "model support",
        "documentation", "doc:", "[doc]",
        "refactor", "chore", "ci:", "test:",
        "question", "help wanted", "discussion"
    ]
    
    for kw in exclude_keywords:
        if kw in combined_text:
            # Exception: If it's a "feature regression" (rare) or "model support bug"
            if "regression" in combined_text:
                return True
            return False

    # 2. Performance Optimization vs Regression
    if "perf" in combined_text or "optimize" in combined_text or "speed up" in combined_text:
        # Only keep if it's explicitly a regression or a bug
        if "regression" in combined_text or "drop" in combined_text or "degradation" in combined_text or "slow" in combined_text:
            return True
        # If it's just "Optimize X", it's a feature/enhancement
        return False

    # 3. Explicit Inclusions (Bugs)
    bug_keywords = [
        "bug", "error", "fail", "crash", "exception", "panic", 
        "broken", "incorrect", "wrong", "nan", "inf", "stuck", "hang",
        "leak", "segmentation fault", "core dump", "timeout"
    ]
    
    # Check labels for 'bug'
    if any("bug" in l for l in labels):
        return True
        
    # Check title for bug keywords
    if any(kw in title for kw in bug_keywords):
        return True
        
    # 4. Default Assumption
    # If it has no labels and title is ambiguous, we might want to be conservative.
    # But usually, if it's not a feature, it's likely a bug or question.
    # We already filtered questions.
    return True

def categorize_bug(issue):
    title = issue["title"].lower()
    labels = []
    if issue.get("labels"):
        for l in issue["labels"]:
            if isinstance(l, dict):
                labels.append(l["name"].lower())
            else:
                labels.append(str(l).lower())
    combined_text = title + " " + " ".join(labels)
    
    if "install" in combined_text or "build" in combined_text or "setup" in combined_text or "docker" in combined_text or "env" in combined_text or "wheel" in combined_text:
        return "Installation/Environment"
    if "crash" in combined_text or "segmentation fault" in combined_text or "core dump" in combined_text or "exception" in combined_text or "runtime error" in combined_text or "assert" in combined_text:
        return "Crash/Runtime Error"
    if "accuracy" in combined_text or "precision" in combined_text or "output" in combined_text or "wrong" in combined_text or "nan" in combined_text or "incorrect" in combined_text:
        return "Accuracy/Correctness"
    if "perf" in combined_text or "slow" in combined_text or "latency" in combined_text or "throughput" in combined_text or "speed" in combined_text or "regression" in combined_text:
        return "Performance Regression"
    if "quant" in combined_text or "awq" in combined_text or "gptq" in combined_text or "fp8" in combined_text:
        return "Quantization"
    if "kernel" in combined_text or "op" in combined_text or "operator" in combined_text or "custom op" in combined_text:
        return "Kernels/Ops"
    if "lora" in combined_text or "adapter" in combined_text:
        return "LoRA/Adapters"
    if "serve" in combined_text or "api" in combined_text or "http" in combined_text or "server" in combined_text:
        return "Serving/API"
    if "model" in combined_text or "loading" in combined_text or "weight" in combined_text:
        return "Model Loading/Weights"
    
    return "Other/Uncategorized"

def main():
    # 1. Fetch
    issues = fetch_issues_api()
    if not issues:
        print("API failed, switching to HTML scraping...")
        issues = fetch_issues_html()
        
    if not issues:
        print("Failed to fetch issues.")
        return

    print(f"Total issues fetched: {len(issues)}")
    
    # 2. Filter
    bug_issues = [i for i in issues if is_target_bug(i)]
    print(f"Total bugs identified (after filtering): {len(bug_issues)}")
    
    # 3. Categorize
    categories = defaultdict(list)
    for issue in bug_issues:
        cat = categorize_bug(issue)
        categories[cat].append(issue)
        
    # 4. Report
    print("\n" + "="*60)
    print("vLLM Ascend Open Bug Analysis Report (Top 100 Recent)")
    print("="*60)
    
    sorted_categories = sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)
    
    for category, items in sorted_categories:
        print(f"\n### {category} ({len(items)})")
        for item in items:
            # Format labels
            label_str = ""
            if item.get("labels"):
                l_names = []
                for l in item["labels"]:
                    if isinstance(l, dict):
                        l_names.append(l["name"])
                    else:
                        l_names.append(str(l))
                if l_names:
                    label_str = f" [{', '.join(l_names)}]"
            
            print(f"- **#{item['number']}**: {item['title']}{label_str}")
            print(f"  Link: {item['html_url']}")

if __name__ == "__main__":
    # Disable warnings for unverified HTTPS
    requests.packages.urllib3.disable_warnings()
    main()
