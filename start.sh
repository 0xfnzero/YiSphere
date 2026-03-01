#!/usr/bin/env bash
# YiSphere 启动脚本（需 Python 3.10+）

cd "$(dirname "$0")"

# 优先使用项目内虚拟环境（依赖已装在 .venv 里）
if [[ -d .venv ]] && [[ -x .venv/bin/python ]]; then
  PYTHON=".venv/bin/python"
  echo "使用虚拟环境: .venv"
else
  for py in python3.13 python3.12 python3.11 python3.10 python3; do
    if MAJOR=$("$py" -c "import sys; print(sys.version_info.major)" 2>/dev/null); MINOR=$("$py" -c "import sys; print(sys.version_info.minor)" 2>/dev/null); then
      if [[ "$MAJOR" -ge 3 && "$MINOR" -ge 10 ]]; then
        PYTHON="$py"
        break
      fi
    fi
  done
  if [[ -z "$PYTHON" ]]; then
    echo "未找到 Python 3.10+，且无 .venv。请先: python3.13 -m venv .venv && .venv/bin/pip install -r requirements.txt"
    exit 1
  fi
  if ! "$PYTHON" -c "import fastapi" 2>/dev/null; then
    echo "当前 Python 未安装依赖。请先: python3.13 -m venv .venv && .venv/bin/pip install -r requirements.txt"
    exit 1
  fi
  echo "使用: $PYTHON"
fi

if [[ ! -f .env ]]; then
  echo "未找到 .env，从 .env.example 复制…"
  cp .env.example .env
  echo "请编辑 .env 填入 OPENAI_API_KEY 后重新运行 ./start.sh"
  exit 1
fi

echo "启动易道服务：http://localhost:8000"
exec "$PYTHON" main.py
