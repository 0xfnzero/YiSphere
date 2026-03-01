# YiSphere 易道 · 易经·八字·六爻·黄道吉日 + AI

结合传统术数（易经、八字、六爻、黄历）与 AI 的对话式预测与择日应用。用户用自然语言提问，AI 结合自动计算的八字/黄历/卦象进行解读，并可像聊天一样追问或补充信息。

## 支持的场景

- **取名**：宝宝取名、公司取名（可结合八字、五行）
- **八字 / 四柱**：排盘与简单解读（需生辰）
- **六爻 / 易经**：起卦与解卦
- **黄道吉日 / 择日**：
  - 婚嫁 / 嫁娶、订婚 / 纳采
  - 开业 / 开市、入宅 / 搬家 / 移徙
  - 动土 / 修造 / 装修、安葬、出行、祭祀、求嗣、安床 等

## 环境要求

- **Python 3.10 或更高**（推荐 3.12）

安装最新 Python（任选其一）：

- **macOS (Homebrew)**：`brew install python@3.12`
- **pyenv**：`pyenv install 3.12`，在项目目录执行 `pyenv local 3.12`
- **官网**：<https://www.python.org/downloads/>

## 快速开始

### 1. 安装依赖

```bash
cd YiSphere
pip install -r requirements.txt
# 或: pip install -e .   # 按 pyproject.toml 安装
```

### 2. 配置 API Key（默认 DeepSeek）

```bash
cp .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY；默认已配 DeepSeek 的 base 和 model
```

- **DeepSeek**：`.env.example` 里已写好 `OPENAI_API_BASE=https://api.deepseek.com`、`OPENAI_MODEL=deepseek-chat`，只需填你的 DeepSeek API Key。
- **OpenAI 或其他**：改 `OPENAI_API_BASE` 和 `OPENAI_MODEL` 即可（接口需兼容 OpenAI 格式）。

### 3. 启动服务

```bash
python main.py
# 或: uvicorn main:app --host 0.0.0.0 --port 8000
```

浏览器访问：<http://localhost:8000>

## 使用方式

- 在页面输入框用自然语言描述需求，例如：
  - “想给娃取名字，2020年1月1日上午10点生，姓李”
  - “今年5月想结婚，选几个吉日”
  - “帮我占一卦，问事业”
  - “下周开业，哪天比较好”
- AI 会视情况自动调用八字、黄历、起卦等工具，并在回复中结合结果解读；若信息不足会主动询问。

## 接口说明

- `POST /api/chat`：多轮对话，自动根据最后一条用户消息注入八字/黄历/卦象/公历农历转换结果。
- `POST /api/tools/bazi`：按公历年月日时计算八字。
- `POST /api/tools/huangli/day`：查某日黄历宜忌。
- `POST /api/tools/huangli/select`：在日期范围内按事宜类型筛选黄道吉日。
- `POST /api/tools/iching/draw`：随机起一卦。
- `POST /api/tools/calendar/solar2lunar`：公历转农历（如身份证生日对应农历哪天）。
- `POST /api/tools/calendar/lunar2solar`：农历转公历。

## 依赖说明

- **sxtwl**：八字四柱（年月日时干支）计算
- **cnlunar**：黄历宜忌、吉神凶神、按事宜选吉日
- **openai**：对话模型调用（兼容 DeepSeek / OpenAI 等，通过 `.env` 配置 base_url 与 model）
