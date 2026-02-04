#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VENV_DIR = PROJECT_ROOT / ".venv"


def _venv_python() -> Path:
    if sys.platform.startswith("win"):
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def _run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.check_call(cmd, cwd=str(PROJECT_ROOT))

def _try_run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    result = subprocess.call(cmd, cwd=str(PROJECT_ROOT))
    if result != 0:
        print(f"提示：命令执行失败（已忽略）：{' '.join(cmd)}")


def _ensure_venv() -> Path:
    python_exe = _venv_python()
    if python_exe.exists():
        return python_exe
    _run([sys.executable, "-m", "venv", str(VENV_DIR)])
    return python_exe


def _ensure_env_file() -> None:
    env_file = PROJECT_ROOT / ".env"
    example = PROJECT_ROOT / ".env.example"
    if env_file.exists() or not example.exists():
        return
    shutil.copyfile(example, env_file)
    print("已生成 .env：请编辑并填写 DEEPSEEK_API_KEY（不使用 AI 可留空）。")

def _warn_if_api_key_missing() -> None:
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        return
    try:
        content = env_file.read_text(encoding="utf-8")
    except Exception:
        return
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() != "DEEPSEEK_API_KEY":
            continue
        value = value.strip().strip("'\"")
        if not value or value == "replace-me":
            print("提示：你还未配置 DEEPSEEK_API_KEY，AI 对话功能将不可用。")
        return


def main() -> int:
    args = set(sys.argv[1:])
    seed = "--seed" in args

    python_exe = _ensure_venv()
    _try_run([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"])
    _run([str(python_exe), "-m", "pip", "install", "-r", "requirements.txt"])
    _ensure_env_file()
    _warn_if_api_key_missing()

    _run([str(python_exe), "manage.py", "migrate"])
    if seed:
        _run([str(python_exe), "manage.py", "seed_data"])

    print("启动开发服务器：http://127.0.0.1:8000/ （Ctrl+C 停止）")
    _run([str(python_exe), "manage.py", "runserver", "127.0.0.1:8000"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
