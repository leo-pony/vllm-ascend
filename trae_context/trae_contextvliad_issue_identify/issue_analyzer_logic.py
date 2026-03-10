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
import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==============================================================================
# CONFIGURATION
# ==============================================================================
REPO_URL = "https://github.com/vllm-project/vllm-ascend/issues"
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

# ==============================================================================
# KEYWORDS & FILTERING LOGIC
# ==============================================================================
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

def is_valid_bug(item, lower_bound=None, upper_bound=None):
    """
    Determines if an issue is a valid bug based on keywords, labels, and ID range.
    """
    num = item.get("number")
    title = item.get("title", "")
    url = item.get("html_url", "")
    t = title.lower()
    
    # Range check (optional)
    if lower_bound is not None and upper_bound is not None:
        if not (isinstance(num, int) and lower_bound <= num <= upper_bound):
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

# ==============================================================================
# SCRAPING HELPERS
# ==============================================================================
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
    
    # Robust scraping strategy: find links matching /issues/\d+
    issue_href_pat = re.compile(r'/%s/%s/issues/\d+$' % ("vllm-project", "vllm-ascend"))
    
    links = soup.find_all('a', href=issue_href_pat)
    seen_nums = set()
    
    for link in links:
        # Skip image/icon links
        if link.find('img') or link.find('svg'):
            continue
            
        href = link.get('href')
        if not href: 
            continue
            
        try:
            num = int(href.split('/')[-1])
        except:
            continue
            
        if num in seen_nums:
            continue
            
        title = link.get_text(strip=True)
        if not title:
            continue
        if title.isdigit():
            continue
            
        seen_nums.add(num)
        
        # Find container row to extract labels/time
        row = link.find_parent(lambda tag: tag.name in ['div', 'li'] and ('js-issue-row' in tag.get('class', []) or 'Box-row' in tag.get('class', [])))
        
        labels = []
        created_at = "Unknown"
        
        if row:
            label_links = row.find_all('a', class_=lambda x: x and 'IssueLabel' in x)
            if not label_links:
                 label_links = row.find_all('a', href=re.compile(r'label%3A|label:'))
                 
            for l in label_links:
                labels.append(l.get_text(strip=True))
                
            time_tag = row.find('relative-time')
            if time_tag and time_tag.get('datetime'):
                created_at = time_tag.get('datetime')
        
        issues.append({
            "number": num,
            "title": title,
            "html_url": "https://github.com" + href,
            "labels": labels,
            "created_at": created_at
        })
            
    return issues

# ==============================================================================
# MAIN EXPORT FUNCTION
# ==============================================================================
def export_to_csv(issues, filename):
    rows = []
    for it in issues:
        rows.append({
            "issue_number": it.get("number"),
            "title": it.get("title"),
            "url": it.get("html_url"),
            "labels": label_to_str(it.get("labels", [])),
            "created_at": it.get("created_at", "Unknown"),
        })

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["issue_number","title","url","labels","created_at"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Exported {len(rows)} issues to {filename}")

if __name__ == "__main__":
    print("This script contains the logic used to fetch and analyze issues.")
    print("It can be imported or adapted to re-run the analysis.")
