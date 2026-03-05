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
            
            # Use wget via subprocess because it handles proxy and SSL better in this environment
            import subprocess
            cmd = [
                "curl", "-s", "-k", "-L",
                "-x", PROXY_URL,
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                print(f"curl failed for page {page} with code {result.returncode}")
                break
                
            page_issues = parse_html_issues(result.stdout)
            if not page_issues:
                # If we got HTML but no issues, maybe structure changed or rate limited
                if "Rate limit" in result.stdout:
                    print("Hit GitHub rate limit in HTML scraping.")
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
    
    # Improved Regex to extract issue links
    # Matches <a id="issue_1234_link" ... href="/vllm-project/vllm-ascend/issues/1234" ... >Title</a>
    # Note: PRs usually have href="/.../pull/..."
    
    issue_links = re.findall(r'<a id="issue_(\d+)_link"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
    
    for issue_id, url_suffix, title_html in issue_links:
        # Strict check: If URL contains '/pull/', it is a PR, skip it.
        if "/pull/" in url_suffix:
            continue
            
        title = re.sub(r'<.*?>', '', title_html).strip()
        url = "https://github.com" + url_suffix
        
        issues.append({
            "number": int(issue_id),
            "title": title,
            "html_url": url,
            "labels": [], # HTML parsing labels is complex, skipping for now
            "body": ""
        })
    return issues

def is_target_bug(issue):
    """
    Filter logic:
    - Exclude PRs (API check)
    - Keep: Bugs, Regressions
    - Filter: Features, RFC, NewModel, Performance (Optimization)
    """
    # 0. Exclude PRs (API specific check)
    if "pull_request" in issue:
        return False
        
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
    return True

def categorize_bug_new(issue):
    title = issue["title"].lower()
    labels = []
    if issue.get("labels"):
        for l in issue["labels"]:
            if isinstance(l, dict):
                labels.append(l["name"].lower())
            else:
                labels.append(str(l).lower())
    combined_text = title + " " + " ".join(labels)
    
    # 1. Performance Regression (性能 Regression)
    # Keywords: slow, latency, throughput, memory leak, oom, hang, stuck, timeout, regression (perf context)
    if any(x in combined_text for x in ["slow", "latency", "throughput", "memory leak", "oom", "hang", "stuck", "timeout", "performance", "speed", "占用", "上涨", "排队"]):
        return "Performance Regression (性能 Regression)"

    # 2. Accuracy Regression (精度 Regression)
    # Keywords: accuracy, precision, wrong, incorrect, nan, inf, garbled, degradation, 精度, 乱码, 异常
    if any(x in combined_text for x in ["accuracy", "precision", "wrong", "incorrect", "nan", "inf", "garbled", "degradation", "output", "reply", "response", "精度", "乱码", "输出异常", "回复", "劣化", "完整回复"]):
        return "Accuracy Regression (精度 Regression)"

    # 3. Specific Feature Anomaly (某一个特性异常)
    features = {
        "Quantization": ["quant", "awq", "gptq", "w8a8", "w4a8", "fp8", "int8", "量化"],
        "Multi-modal/VL": ["vision", "image", "vl", "multimodal", "processor", "clip", "vit", "多模态", "图片"],
        "LoRA/Adapter": ["lora", "adapter", "peft"],
        "Speculative/MTP": ["speculative", "eagle", "mtp", "draft", "verifier", "投机"],
        "Context Parallel": ["context parallel", "cp", "ring attention", "sequence parallel"],
        "MoE": ["moe", "expert", "router", "gating"],
        "KV Cache/Prefix": ["kv cache", "prefix cache", "paged attention", "block manager", "缓存", "pool"],
        "Tool/Function Call": ["tool", "function call", "fc"],
        "Profiler": ["profiler", "profile"],
        "Op/Kernel": ["op", "kernel", "算子", "operator"]
    }
    
    for feat_name, keywords in features.items():
        if any(kw in combined_text for kw in keywords):
            return f"Specific Feature Anomaly (特性异常: {feat_name})"

    # 4. Basic Functionality Anomaly (基本功能异常)
    if any(x in combined_text for x in ["install", "build", "crash", "segmentation fault", "core dump", "exception", "error", "fail", "start", "load", "import", "device", "npu", "found", "die", "kill", "启动", "报错", "挂掉", "失败", "无法", "unknown"]):
        return "Basic Functionality Anomaly (基本功能异常)"

    # 5. Documentation/Other (文档/其他)
    if any(x in combined_text for x in ["doc", "typo", "example", "guide", "文档", "release", "feedback", "faq"]):
        return "Documentation/Other (文档/其他)"
        
    return "Other (其他)"

def main():
    # 1. Fetch
    # Directly fetch HTML since API is rate limited
    print("API rate limited, switching to HTML scraping...")
    issues = fetch_issues_html()
        
    if not issues:
        print("Failed to fetch issues.")
        return

    print(f"Total items fetched: {len(issues)}")
    
    # 2. Filter
    bug_issues = [i for i in issues if is_target_bug(i)]
    print(f"Total bugs identified (after filtering PRs and Features): {len(bug_issues)}")
    
    # 3. Categorize
    categories = defaultdict(list)
    for issue in bug_issues:
        cat = categorize_bug_new(issue)
        categories[cat].append(issue)
        
    # 4. Report
    print("\n" + "="*60)
    print("vLLM Ascend Open Bug Analysis Report (New Classification)")
    print("="*60)
    
    # Custom sort order
    sort_order = [
        "Basic Functionality Anomaly (基本功能异常)",
        "Performance Regression (性能 Regression)",
        "Accuracy Regression (精度 Regression)"
    ]
    
    # Helper to get sort index
    def get_sort_key(item):
        cat_name = item[0]
        if cat_name in sort_order:
            return sort_order.index(cat_name)
        if "Specific Feature Anomaly" in cat_name:
            return 3
        if "Documentation" in cat_name:
            return 10
        return 20

    sorted_categories = sorted(categories.items(), key=get_sort_key)
    
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
