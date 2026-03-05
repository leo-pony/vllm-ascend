# Issues data manually extracted from previous analysis (29 bugs)
issues_data = [
    {"number": 6982, "title": "[Usage]:hdk25.5 vllm-ascend0.14.0rc1部署kimi k2.5时aclnnMoeDistributeDispatchV4算子报错", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6982"},
    {"number": 6980, "title": "[Bug]: 在gpustack上使用vllm-ascend:glm5部署GLM-5-w4a8模型，模型输出异常", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6980"},
    {"number": 6978, "title": "[Misc]: 支持Qwen3-omni w8a8的量化后的版本什么时候发布", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6978"},
    {"number": 6974, "title": "Are there any recent update plans related to #6603?", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6974"},
    {"number": 6972, "title": "[Bug]: vllm 启动 qwen3-omni 模型，尝试命令行方式--compilation-config '{\"cudagraph_mode\": \"FULL_DECODE_ONLY\", \"cudagraph_capture_sizes\":[1,2,4,8,16,24,48]}'  或yaml 文件方式，FULL_DECODE_ONLY均未生效", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6972"},
    {"number": 6970, "title": "[Release]: Release checklist for v0.16.0rc1", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6970"},
    {"number": 6969, "title": "[Feedback]: v0.16.0rc1 Release Feedback", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6969"},
    {"number": 6934, "title": "[Bug]: [kimi-k2.5] Attempted to assign 4225 = 4225 multimodal tokens to 1 placeholder", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6934"},
    {"number": 6931, "title": "[Usage]: VLLM-ASCEND v0.11.0 启动deepseek-r1-0528-w8a8服务报错", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6931"},
    {"number": 6929, "title": "[Bug]: Qwen3-VL-235B模型，压测时模型内存占用一直提升，压测完毕后，重新压测依旧会继续上涨", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6929"},
    {"number": 6926, "title": "[Bug]: 开启export VLLM_TORCH_PROFILER_DIR=\"./vllm_profile\"这个变量后，发送多次curl请求会报错", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6926"},
    {"number": 6920, "title": "[Usage]: prefill实例间KV Cache pool 使用", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6920"},
    {"number": 6879, "title": "[Bug]: qwen3.5单机部署，回复很慢，思考很啰嗦", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6879"},
    {"number": 6875, "title": "[Bug]: A2尝试四机部署GLM5-bf16失败，报错：NPU function error: call aclnnSwiGlu failed, error code is 507014", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6875"},
    {"number": 6863, "title": "[Bug]: qwen3-next-80B 运行半个月后服务挂掉报错 Fatal Python error： none_dealloc：deallocating None", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6863"},
    {"number": 6861, "title": "[Usage]: GLM5思考过程如何显示在reasoning中", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6861"},
    {"number": 6853, "title": "[Bug]: Failed to apply Qwen2_5_VLProcessor for qwen2.5-vl-72b", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6853"},
    {"number": 6848, "title": "[Bug]: qwen3.5 A2 双机回答的思考模式为英文", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6848"},
    {"number": 6838, "title": "[v0.15.0rc1] FAQ / Feedback | 问题/反馈", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6838"},
    {"number": 6833, "title": "[Usage]: 为什么Qwen3-Next多并发的时候，请求要排队那么久，而且缓存命中为0", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6833"},
    {"number": 6938, "title": "[Bug]: Anthropic Messages API (/v1/messages) fails to process image inputs — images passed as None to Qwen3VLProcessor", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6938"},
    {"number": 6925, "title": "[Bug]: quay.io/ascend/vllm-ascend:glm5-openeuler 部署GLM-OCR 精度劣化严重", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6925"},
    {"number": 6909, "title": "[Bug]: v0.15.0rc1-openeuler版本镜像部署的Qwen3-vl模型无完整回复", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6909"},
    {"number": 6949, "title": "[Bug]: v0.15.0rc1, server failed to start with mooncake connector", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6949"},
    {"number": 6868, "title": "[Bug]: When Running GLM5 metrics.py make server crush", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6868"},
    {"number": 6950, "title": "[Bug]: v0.15.0rc1, Flash Comm V1 is not supported for VL models.", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6950"},
    {"number": 6942, "title": "[Installation]: NPU卡无法调用，无法加载模型", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6942"},
    {"number": 6935, "title": "[Bug]: [Bug]: v16版本，存在的问题 [ERROR] 2026-03-02-15:44:05 (PID:1, Device:-1, RankID:-1) ERR99999 UNKNOWN applicaiton exception", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6935"},
    {"number": 6908, "title": "[Usage]: Qwen3 dense quant是否支持动态量化", "html_url": "https://github.com/vllm-project/vllm-ascend/issues/6908"}
]

from collections import defaultdict

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
    if any(x in combined_text for x in ["install", "build", "crash", "segmentation fault", "core dump", "exception", "error", "fail", "start", "load", "import", "device", "npu", "found", "die", "kill", "启动", "报错", "挂掉", "失败", "无法", "unknown", "生效"]):
        return "Basic Functionality Anomaly (基本功能异常)"

    # 5. Documentation/Other (文档/其他)
    if any(x in combined_text for x in ["doc", "typo", "example", "guide", "文档", "release", "feedback", "faq", "misc", "plan"]):
        return "Documentation/Other (文档/其他)"
        
    return "Other (其他)"

def main():
    print(f"Analyzing {len(issues_data)} issues from cache...")
    
    categories = defaultdict(list)
    for issue in issues_data:
        cat = categorize_bug_new(issue)
        categories[cat].append(issue)
        
    # Report
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
            print(f"- **#{item['number']}**: {item['title']}")
            print(f"  Link: {item['html_url']}")

if __name__ == "__main__":
    main()
