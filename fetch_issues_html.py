import requests
import re
import time
import subprocess
import os

# Configuration
REPO_OWNER = "vllm-project"
REPO_NAME = "vllm-ascend"
BASE_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/issues"
PROXY = "http://127.0.0.1:7890"

def fetch_page(page_num):
    url = f"{BASE_URL}?q=is%3Aopen+is%3Aissue&page={page_num}"
    print(f"Fetching page {page_num}...")
    
    # Use wget via subprocess because it handles proxy and SSL better in this environment
    cmd = [
        "wget", "--no-check-certificate", "-q", "-O", "-",
        "-e", "use_proxy=yes",
        "-e", f"http_proxy={PROXY}",
        "-e", f"https_proxy={PROXY}",
        url
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"Error fetching page {page_num} via wget. Return code: {result.returncode}")
            return None
    except Exception as e:
        print(f"Exception fetching page {page_num}: {e}")
        return None

def parse_issues_robust(html_content):
    issues = []
    
    if "js-issue-row" not in html_content:
        if "<title>GitHub · Where software is built</title>" in html_content:
             print("Warning: Redirected to GitHub homepage. Proxy or rate limit issue.")
             return []
        print("Warning: 'js-issue-row' not found in HTML.")
        # Proceed with regex search anyway
    
    # Improved Regex for title and URL to work on full content
    # Look for: <a id="issue_1234_link" ...>Title</a>
    issue_links = re.findall(r'<a id="issue_(\d+)_link"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html_content, re.DOTALL)
    
    for issue_id, url_suffix, title_html in issue_links:
        url = "https://github.com" + url_suffix
        title = re.sub(r'<.*?>', '', title_html).strip()
        
        # Try to find labels for this issue
        # We search for the issue row block
        row_pattern = f'id="issue_{issue_id}"'
        row_start = html_content.find(row_pattern)
        labels = []
        
        if row_start != -1:
            # Search in the next 3000 chars (heuristic)
            chunk = html_content[row_start:row_start+3000]
            
            # Stop at next issue start
            next_issue_match = re.search(r'id="issue_\d+"', chunk[1:])
            if next_issue_match:
                chunk = chunk[:next_issue_match.start()]
                
            label_matches = re.findall(r'class="[^"]*IssueLabel[^"]*"[^>]*>(.*?)</a>', chunk, re.DOTALL)
            for label_html in label_matches:
                clean_label = re.sub(r'<.*?>', '', label_html).strip()
                if clean_label:
                    labels.append(clean_label)

        issues.append({
            "id": issue_id,
            "url": url,
            "title": title,
            "labels": labels
        })
        
    return issues

def is_bug(issue):
    title = issue["title"].lower()
    labels = [l.lower() for l in issue["labels"]]
    
    # Exclusion criteria
    exclude_keywords = [
        "feature", "enhancement", "rfc", "new model", "documentation", 
        "refactor", "test", "ci", "question", "discussion", "help wanted",
        "support", "task", "bump", "chore"
    ]
    
    # Check labels
    for label in labels:
        if any(keyword in label for keyword in exclude_keywords):
            return False
            
    # Check title for explicit non-bug indicators
    if title.startswith("[feat") or title.startswith("feat:") or "feature request" in title:
        return False
    if title.startswith("[rfc]") or "rfc:" in title:
        return False
    if title.startswith("[doc]") or "doc:" in title:
        return False
        
    return True

def categorize_issue(issue):
    title = issue["title"].lower()
    labels = [l.lower() for l in issue["labels"]]
    combined_text = title + " " + " ".join(labels)
    
    if "install" in combined_text or "build" in combined_text or "setup" in combined_text or "docker" in combined_text or "env" in combined_text:
        return "Installation/Environment"
    if "crash" in combined_text or "segmentation fault" in combined_text or "core dump" in combined_text or "exception" in combined_text or "error" in combined_text or "failed" in combined_text:
        return "Crash/Runtime Error"
    if "accuracy" in combined_text or "precision" in combined_text or "output" in combined_text or "wrong" in combined_text or "nan" in combined_text:
        return "Accuracy/Correctness"
    if "perf" in combined_text or "slow" in combined_text or "latency" in combined_text or "throughput" in combined_text or "speed" in combined_text:
        return "Performance"
    if "quant" in combined_text or "awq" in combined_text or "gptq" in combined_text:
        return "Quantization"
    if "kernel" in combined_text or "op" in combined_text or "operator" in combined_text:
        return "Kernels/Ops"
    if "lora" in combined_text or "adapter" in combined_text:
        return "LoRA/Adapters"
    if "serve" in combined_text or "api" in combined_text or "http" in combined_text:
        return "Serving/API"
    
    return "Other/Uncategorized"

def main():
    all_issues = []
    # Fetch 4 pages (approx 100 issues)
    for page in range(1, 5):
        html = fetch_page(page)
        if html:
            issues = parse_issues_robust(html)
            all_issues.extend(issues)
            time.sleep(1) # Be nice
            
    print(f"Total issues fetched: {len(all_issues)}")
    
    bug_issues = [i for i in all_issues if is_bug(i)]
    print(f"Total bug issues identified: {len(bug_issues)}")
    
    categories = {}
    
    for issue in bug_issues:
        category = categorize_issue(issue)
        if category not in categories:
            categories[category] = []
        categories[category].append(issue)
        
    # Generate Report
    print("\n" + "="*50)
    print("vLLM Ascend Open Bug Issues Analysis (Top 100)")
    print("="*50)
    
    sorted_categories = sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)
    
    for category, items in sorted_categories:
        print(f"\n## {category} ({len(items)})")
        for item in items:
            label_str = f" [{', '.join(item['labels'])}]" if item['labels'] else ""
            print(f"- #{item['id']} {item['title']}{label_str}")
            print(f"  Link: {item['url']}")

if __name__ == "__main__":
    main()
