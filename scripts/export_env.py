"""
Export environment snapshot:
  - python version
  - platform
  - torch/transformers versions
  - GPU name(s) if available
  - pip freeze

Outputs:
  - reports/env_snapshot.json
  - reports/env_freeze.txt

Notes:
- Best effort: each section is wrapped with try/except to avoid failing the run.
"""
import json, subprocess, sys, platform
from pathlib import Path

def get_gpu():
    """Return a list of detected GPU names if torch.cuda is available, else []."""
    try:
        import torch
        if torch.cuda.is_available():
            return [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]
    except Exception:
        return []
    return []

def main():
    """Collect and write environment snapshot + freeze into reports/."""
    out_dir = Path("reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    snap = {
        "python": sys.version,
        "platform": platform.platform(),
        "torch": None,
        "transformers": None,
        "gpus": get_gpu()
    }
    try:
        import torch, transformers
        snap["torch"] = torch.__version__
        snap["transformers"] = transformers.__version__
    except Exception:
        pass
    (out_dir/"env_snapshot.json").write_text(json.dumps(snap, ensure_ascii=False, indent=2), encoding="utf-8")

    try:
        freeze = subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True)
        (out_dir/"env_freeze.txt").write_text(freeze, encoding="utf-8")
    except Exception as e:
        (out_dir/"env_freeze.txt").write_text(f"# pip freeze failed: {e}\n", encoding="utf-8")
    print("[env] snapshot written.")

if __name__ == "__main__":
    main()