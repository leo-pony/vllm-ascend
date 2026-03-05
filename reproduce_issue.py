
import os
import sys
from vllm_ascend.quantization.modelslim_config import AscendModelSlimConfig

def test_reproduce():
    model_name = "vllm-ascend/Qwen3-235B-A22B-w8a8"
    os.environ["VLLM_USE_MODELSCOPE"] = "true"
    
    config = AscendModelSlimConfig()
    try:
        print(f"Testing maybe_update_config with model_name='{model_name}'...")
        config.maybe_update_config(model_name)
        print("Success! Config loaded (or at least no error raised).")
        print(f"Quant description keys: {list(config.quant_description.keys())[:5]}")
    except ValueError as e:
        print("Caught expected error (if reproducing) or unexpected error:")
        print(e)
        sys.exit(1)
    except Exception as e:
        print(f"Caught unexpected exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_reproduce()
