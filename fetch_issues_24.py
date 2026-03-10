import os
import json
import subprocess
import csv
import sys
import time
import requests
import re
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
LOWER, UPPER = 4067, 7051
REPO_URL = "https://github.com/vllm-project/vllm-ascend/issues"
JSON_FILE = "/data/mnj/vllm-ascend/vllm_issues_filtered.json"
CSV_FILE = "/data/mnj/vllm-ascend/vllm_ascend_bugs.csv"
PROXY_URL = "http://127.0.0.1:7890"
PROXIES = {
    "http": PROXY_URL,
    "https": PROXY_URL,
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9"
}

# Keywords and logic
non_bug_keywords = [
    "feature", "rfc", "support", "implement", "add", "new model",
    "release", "checklist", "roadmap", "tracking", "discussion",
    "question", "doc", "documentation", "proposal", "example",
    "test", "ci", "build", "refactor", "clean", "update", "upgrade",
    "chore", "bump", "usage", "how to"
]
non_bug_cn_keywords = [
    "是否支持", "怎么", "如何", "咨询", "求助", "请问", "支持吗",
    "使用问题", "使用疑问", "使用方法", "新模型", "新增模型", "版本发布", "检查清单"
]
perf_keywords = [
    "performance", "latency", "throughput", "tps", "qps", "speed",
    "吞吐", "时延", "延迟", "性能", "速度", "卡顿", "变慢", "慢"
]
perf_regression_markers = [
    "regression", "回归", "退化", "变慢", "更慢", "下降", "降低", "降速",
    "比之前慢", "比以前慢", "升级后变慢", "升级后更慢", "比旧版本慢", "比先前慢"
]
non_bug_labels = {"enhancement", "feature", "documentation", "question", "wontfix", "invalid", "duplicate", "good first issue", "ci", "test", "usage"}
bug_labels = {"bug", "kind/bug", "triage/bug"}

def is_valid_bug(item):
    num = item.get("number")
    title = item.get("title", "")
    url = item.get("html_url", "")
    t = title.lower()
    
    # Range check
    if not (isinstance(num, int) and LOWER <= num <= UPPER):
        return False
        
    # PR check
    if "/pull/" in url:
        return False
        
    # Prefix check
    if t.startswith("[usage]") or t.startswith("[question]") or t.startswith("[misc]"):
        return False
        
    # CN non-bug keywords
    if any(k in title for k in non_bug_cn_keywords):
        return False
        
    # General non-bug keywords
    is_crash_or_fail = any(x in t for x in ["fail", "error", "crash", "panic", "exception", "broken"])
    if any(k in t for k in non_bug_keywords):
        if "regression" not in t and not is_crash_or_fail:
            return False
            
    # Performance strictness
    if any(k in t for k in perf_keywords) and not any(m in t for m in perf_regression_markers):
        return False
        
    # Labels check
    labels = []
    for l in item.get("labels", []) or []:
        if isinstance(l, dict) and "name" in l:
            labels.append(l["name"].lower())
        elif isinstance(l, str):
            labels.append(l.lower())
        else:
            labels.append(str(l).lower())
            
    if labels:
        if any(lb in non_bug_labels for lb in labels) and not any(lb in bug_labels for lb in labels):
            return False
            
    return True

def label_to_str(labels):
    out = []
    for l in labels or []:
        if isinstance(l, dict) and "name" in l:
            out.append(l["name"])
        elif isinstance(l, str):
            out.append(l)
        else:
            out.append(str(l))
    return ";".join(out)

def fetch_page(page):
    url = f"{REPO_URL}?q=is%3Aopen+is%3Aissue&page={page}"
    print(f"Fetching {url}...")
    try:
        res = requests.get(url, headers=HEADERS, proxies=PROXIES, verify=False, timeout=60)
        res.raise_for_status()
        return res.text
    except Exception as e:
        print(f"Error fetching: {e}")
        return None

def parse_issues(html):
    soup = BeautifulSoup(html, 'html.parser')
    issues = []
    
    # Strategy: Find all links that look like issue URLs
    # Pattern: /vllm-project/vllm-ascend/issues/\d+
    pattern = re.compile(r'/vllm-project/vllm-ascend/issues/\d+$')
    links = soup.find_all('a', href=pattern)
    
    seen_nums = set()
    
    for link in links:
        try:
            href = link.get('href')
            if not href:
                continue
                
            # Extract number
            parts = href.split('/')
            if not parts:
                continue
            try:
                num = int(parts[-1])
            except ValueError:
                continue
                
            if num in seen_nums:
                continue
            seen_nums.add(num)
                
            title = link.get_text(strip=True)
            if not title:
                continue
                
            # Try to find labels
            # Usually they are in the same container or row
            # We can look for label links nearby
            labels = []
            
            # Navigate up to find a row container
            # Common GitHub classes: js-issue-row, Box-row, etc.
            # But structure changes. Let's look for siblings or parents.
            
            row = link.find_parent(lambda tag: tag and tag.name in ['div', 'li'] and ('js-issue-row' in tag.get('class', []) or 'Box-row' in tag.get('class', [])))
            
            if row:
                # Find labels in this row
                # Labels usually have href containing "label%3A" or "label:" or class "IssueLabel"
                label_links = row.find_all('a', class_=lambda x: x and 'IssueLabel' in x)
                if not label_links:
                     label_links = row.find_all('a', href=re.compile(r'label%3A|label:'))
                
                for l in label_links:
                    labels.append(l.get_text(strip=True))
            
            issues.append({
                "number": num,
                "title": title,
                "html_url": "https://github.com" + href,
                "labels": labels,
                "created_at": "Unknown" 
            })
            
        except Exception as e:
            print(f"Error parsing link: {e}")
            continue
            
    return issues

def main():
    scraped = []
    # Fetch pages 1 to 24 (inclusive)
    for page in range(1, 25):
        html = fetch_page(page)
        if not html:
            break
            
        page_issues = parse_issues(html)
        if not page_issues:
            print("No issues found on page (end of list or scraping blocked).")
            # Dump a bit of HTML to debug if it's blocked
            if "Rate limit" in html:
                print("Rate limited.")
            elif "Sign in" in html and "to GitHub" in html:
                 # Sometimes GitHub redirects to login if suspicious
                 print("Redirected to login?")
            break
            
        print(f"Found {len(page_issues)} issues on page {page}")
        
        nums = [i['number'] for i in page_issues]
        scraped.extend(page_issues)
        
        # Robust stopping condition:
        # Only stop if ALL issues on the page are below LOWER.
        # This handles pinned issues (which might be old) appearing on the first page.
        if nums:
            if all(n < LOWER for n in nums):
                print(f"All issues on page {page} are below {LOWER}. Stopping.")
                break
            
        time.sleep(1) # Be nice

    print(f"Total scraped: {len(scraped)}")

    # Load Existing
    existing = []
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except:
            existing = []
            
    # Merge
    by_num = {}
    for it in existing:
        if isinstance(it, dict) and "number" in it:
            by_num[it["number"]] = it
            
    for it in scraped:
        n = it["number"]
        if n in by_num:
            base = by_num[n]
            # Update title if changed
            if base.get("title") != it["title"]:
                base["title"] = it["title"]
            # Merge labels if scraped has them
            if it["labels"]:
                # If we have existing labels, maybe we want to keep them or merge?
                # Let's trust scraped labels as "current state"
                # But scraped labels might be missing colors or IDs, just strings.
                # Existing labels might be dicts.
                # Let's update labels to list of strings for simplicity in this CSV export context
                # Or keep dicts if existing has them, but convert scraped to dicts?
                # Let's just store list of strings for scraped.
                base["labels"] = it["labels"]
        else:
            by_num[n] = it
            
    merged = [v for k, v in sorted(by_num.items(), key=lambda kv: kv[0])]
    
    # Filter
    filtered = [it for it in merged if is_valid_bug(it)]
    print(f"Valid bugs after filtering: {len(filtered)}")
    
    # Save JSON
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)
        
    # Export CSV
    rows = []
    for it in filtered:
        rows.append({
            "issue_number": it.get("number"),
            "title": it.get("title"),
            "url": it.get("html_url"),
            "labels": label_to_str(it.get("labels", [])),
            "created_at": it.get("created_at", "Unknown"),
        })

    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["issue_number","title","url","labels","created_at"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Exported to {CSV_FILE}")

if __name__ == "__main__":
    main()
