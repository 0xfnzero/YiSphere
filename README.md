<div align="center">
    <h1>☯️ YiSphere 易道</h1>
    <h3><em>传统术数 + AI 对话</em></h3>
</div>

<p align="center">
    <strong>结合易经、八字、六爻、黄道吉日、奇门遁甲、风水、紫微斗数、梅花易数、大六壬、太乙、测字、面相、手相、解梦、择日等传统术数与 AI 的对话式应用。用自然语言与多位「大师」角色对话，自动排八字、起卦、查黄历，占卜、取名、择日一气呵成。</strong>
</p>

<p align="center">
    <a href="https://github.com/0xfnzero/YiSphere">
        <img src="https://img.shields.io/github/stars/0xfnzero/YiSphere?style=social" alt="GitHub stars">
    </a>
    <a href="https://github.com/0xfnzero/YiSphere/network">
        <img src="https://img.shields.io/github/forks/0xfnzero/YiSphere?style=social" alt="GitHub forks">
    </a>
    <a href="https://github.com/0xfnzero/YiSphere/blob/main/LICENSE">
        <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
    </a>
</p>

<p align="center">
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
    <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI API">
</p>

<p align="center">
    <a href="https://github.com/0xfnzero/YiSphere/blob/main/README.md">中文</a> |
    <a href="https://fnzero.dev/">Website</a> |
    <a href="https://t.me/fnzero_group">Telegram</a> |
    <a href="https://discord.gg/vuazbGkqQE">Discord</a>
</p>

---

结合传统术数与 AI 的对话式预测与择日应用。涵盖**易经、八字、六爻、黄道吉日、奇门遁甲、风水、紫微斗数、梅花易数、大六壬、太乙神数、测字、面相、手相、解梦、择日**等门类。用户用自然语言提问，选择不同「大师」角色对话，AI 结合程序自动计算的八字/黄历/卦象进行解读，支持多轮追问与按角色保存聊天记录。

## 功能概览

- **多角色对话**：左侧可选多位「大师」（神算子、文渊先生、子平先生、易翁老人、遁甲道人、青乌先生、星隐道人、梅翁老人、周文王、诸葛亮、李淳风、袁天罡等），涵盖八字、六爻、奇门遁甲、风水、紫微斗数、梅花易数、大六壬、太乙、测字、面相、手相、解梦、择日等，每位有古人语气，右侧为与当前角色的聊天窗口。
- **自然语言输入**：支持「农历生日 1989.5.18 13:30 男，占卜一卦 运势」等说法；日期支持公历/农历、点号或横线分隔；时辰支持「13:30」「13点」等。
- **八字**：用户给农历生日则按农历直接排四柱，给公历则按公历排盘并附带农历对照；四柱与「今年流年」均由程序计算并注入，避免 AI 自算出错。
- **六爻/易经**：自动起卦并注入卦象，由当前角色解卦。
- **黄道吉日**：婚嫁、订婚、开业、入宅、动土、安葬、出行、祭祀、求嗣等，按事宜类型与日期范围推荐吉日。
- **公历↔农历**：身份证公历生日转农历、农历某日对应公历等。
- **流式回复**：思考中提示 + 逐字输出，聊天记录按角色保存在浏览器本地。

## 涵盖的传统术数

除易经、八字、六爻、黄道吉日外，还包含：

- **三式**：奇门遁甲、大六壬、太乙神数  
- **命理/占卜**：紫微斗数、梅花易数、京氏易、卦象  
- **堪舆/风水**：风水、玄空风水  
- **其他**：取名、测字、面相、手相、解梦、择日、星象占候等  

每位「大师」角色对应一到多项擅长，由对应角色做解读或简要解答。

## 支持的场景

| 类型     | 说明 |
|----------|------|
| 取名     | 宝宝取名、公司取名，可结合八字、五行、字义 |
| 八字/四柱 | 排盘与解读（需生辰；支持农历或公历），流年运势 |
| 六爻/易经 | 起卦与解卦，问事断吉凶 |
| 黄道吉日 | 婚嫁、订婚、开业、入宅、动土、安葬、出行、祭祀、求嗣、安床等 |
| 公历农历 | 公历某日对应农历、农历某日对应公历 |
| 奇门遁甲 | 择时择方、奇门八阵，由遁甲道人等角色解答 |
| 风水     | 阳宅阴宅、布局化煞，由青乌先生等角色解答 |
| 紫微斗数 | 命盘、十二宫、主星、流年，由星隐道人等角色解答 |
| 梅花易数 / 大六壬 / 太乙 | 起卦、课传、象数体用，由对应角色简要解答 |
| 测字 / 面相 / 手相 / 解梦 | 由字灵先生、观相先生、掌翁老人、梦觉先生等角色解答 |

## 环境要求

- **Python 3.10+**（推荐 3.12）

安装方式示例：

- **macOS (Homebrew)**：`brew install python@3.12`
- **pyenv**：`pyenv install 3.12`，在项目目录执行 `pyenv local 3.12`
- **官网**：<https://www.python.org/downloads/>

## 快速开始

### 1. 克隆与依赖

```bash
git clone https://github.com/0xfnzero/YiSphere.git
cd YiSphere
pip install -r requirements.txt
# 或使用虚拟环境：python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

### 2. 配置 API（默认 DeepSeek）

```bash
cp .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY
```

- **DeepSeek**：`.env.example` 已写好 `OPENAI_API_BASE`、`OPENAI_MODEL`，只需填 DeepSeek API Key。
- **OpenAI 或其他**：修改 `OPENAI_API_BASE` 和 `OPENAI_MODEL`（需兼容 OpenAI 接口格式）。

### 3. 启动

```bash
./start.sh
# 或：python main.py
# 或：uvicorn main:app --host 0.0.0.0 --port 8000
```

`start.sh` 会检测 Python 3.10+、若无 `.env` 则从 `.env.example` 复制并提示配置 Key；若存在 `.venv` 则优先使用。

浏览器访问：<http://localhost:8000>

## 使用方式

- 左侧点击一位大师（如「周文王」「神算子」），右侧输入自然语言，例如：
  - 「农历生日 1988.3.24 13:30 男 帮我占卜一卦 运势」
  - 「想给娃取名字，2020 年 1 月 1 日上午 10 点生，姓李」
  - 「今年 5 月想结婚，选几个吉日」
  - 「下周开业，哪天比较好」
- AI 会按当前角色身份回复，并视情况自动调用八字、黄历、起卦等；若信息不足会主动追问。聊天记录按角色保存在本地，刷新不丢失。

## 接口说明

| 方法/路径 | 说明 |
|-----------|------|
| `GET /api/masters` | 大师角色列表（id、name、skill、intro、gender、age 等） |
| `POST /api/chat` | 多轮对话（非流式），自动注入八字/黄历/卦象/当前流年 |
| `POST /api/chat/stream` | 流式对话，返回 SSE，前端可逐字显示 |
| `POST /api/tools/bazi` | 按公历年月日时计算八字四柱 |
| `POST /api/tools/huangli/day` | 查某日黄历宜忌 |
| `POST /api/tools/huangli/select` | 日期范围内按事宜类型筛选黄道吉日 |
| `POST /api/tools/iching/draw` | 随机起一卦 |
| `POST /api/tools/calendar/solar2lunar` | 公历 → 农历 |
| `POST /api/tools/calendar/lunar2solar` | 农历 → 公历 |
| `GET /api/avatar/{master_id}` | 可选：大师头像代理（当前前端使用首字展示，不依赖此接口） |

请求体格式示例：`/api/chat`、`/api/chat/stream` 为 `{ "messages": [{"role":"user","content":"..."}], "master": "shengsuanzi" }`，`master` 为角色 id，不传则默认神算子。

## 依赖说明

| 依赖 | 用途 |
|------|------|
| fastapi / uvicorn | Web 服务与流式响应 |
| openai | 对话模型调用（兼容 DeepSeek / OpenAI，通过 `.env` 配置） |
| sxtwl | 八字四柱（年月日时干支）、公历农历转换 |
| cnlunar | 黄历宜忌、吉神凶神、按事宜选吉日 |
| pydantic | 请求/响应校验 |
| python-dotenv | 环境变量加载 |

## 项目结构（简要）

```
YiSphere/
├── main.py              # FastAPI 入口、路由、静态文件
├── start.sh             # 启动脚本（Python 3.10+ / .venv / .env 检查）
├── requirements.txt
├── .env.example
├── app/
│   ├── prompts.py        # 大师角色与系统提示词
│   └── services/
│       ├── chat.py       # 对话与工具注入（八字/黄历/卦/当前流年）
│       ├── bazi.py       # 八字（公历/农历入口）
│       ├── calendar.py   # 公历↔农历
│       ├── huangli.py    # 黄历与择日
│       └── iching.py     # 易经起卦
└── static/
    └── index.html       # 前端（角色列表 + 聊天 + 流式 + 本地持久化）
```

## License

按项目仓库约定使用。
