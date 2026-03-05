import pandas as pd

data = [
    {"Label": "area/core", "Description": "核心框架与调度", "Scope": "Platform, Worker, Scheduler"},
    {"Label": "area/kernel", "Description": "算子实现与优化", "Scope": "C++ Kernels, Python Ops"},
    {"Label": "area/attention", "Description": "注意力机制", "Scope": "PagedAttention, MLA, SFA"},
    {"Label": "area/quantization", "Description": "量化支持", "Scope": "W8A8, W4A16, ModelSlim"},
    {"Label": "area/distributed", "Description": "分布式与通信", "Scope": "Communication, EPLB"},
    {"Label": "area/graph", "Description": "图模式与编译", "Scope": "ACL Graph, TorchAir"},
    {"Label": "area/spec-decode", "Description": "投机采样", "Scope": "Eagle, Medusa"},
    {"Label": "area/model", "Description": "模型适配与加载", "Scope": "Patches, Model Loader, LoRA"},
    {"Label": "device/310p", "Description": "310P 硬件相关", "Scope": "Ascend 310P"},
    {"Label": "infra/test", "Description": "测试与 CI", "Scope": "Tests, CI/CD, Benchmarks"},
    {"Label": "infra/docs", "Description": "文档", "Scope": "Documentation"}
]

df = pd.DataFrame(data)

# Rename columns to Chinese as requested by user context implies Chinese output
df.columns = ["标签 (Label)", "描述 (Description)", "适用范围 (Scope)"]

output_file = "vllm_ascend_issue_labels.xlsx"
df.to_excel(output_file, index=False)

print(f"Successfully exported labels to {output_file}")
