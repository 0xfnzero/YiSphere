<div align="center">
    <h1>☯️ YiSphere</h1>
    <h3><em>AI I Ching Divination · BaZi Calculator · Liu Yao · Huangli · Chinese Naming</em></h3>
</div>

<p align="center">
    <strong>YiSphere is an open-source AI-powered Chinese metaphysics chat application. It supports I Ching divination, BaZi / Four Pillars calculation, Liu Yao hexagram casting, Huangli auspicious date selection, Chinese baby naming, company naming, wedding date selection, business opening date selection, and solar-lunar calendar conversion.</strong>
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
    <img src="https://img.shields.io/badge/I_Ching-Divination-c9a227?style=for-the-badge" alt="I Ching">
    <img src="https://img.shields.io/badge/BaZi-Calculator-8f5b2d?style=for-the-badge" alt="BaZi">
</p>

<p align="center">
    <a href="https://github.com/0xfnzero/YiSphere/blob/main/README.md">中文</a> |
    <a href="https://github.com/0xfnzero/YiSphere/blob/main/README_EN.md">English</a> |
    <a href="https://fnzero.dev/">Website</a> |
    <a href="https://t.me/fnzero_group">Telegram</a> |
    <a href="https://discord.gg/vuazbGkqQE">Discord</a>
</p>

---

YiSphere combines traditional Chinese metaphysics with modern LLM chat. Users can ask natural-language questions such as:

- "Cast an I Ching hexagram for my career decision."
- "My lunar birthday is 1988.3.24 at 13:30, male. Read my BaZi."
- "Pick auspicious wedding dates in May 2026."
- "A baby was born on January 1, 2020 at 10 AM. The surname is Li. Suggest Chinese names."

The application first computes structured results locally, including BaZi pillars, lunar calendar data, Huangli day information, and I Ching hexagrams. The LLM then explains those computed results in a conversational Chinese-master persona.

**Search keywords**: AI fortune telling, I Ching AI, I Ching divination, BaZi calculator, Four Pillars, Liu Yao, Huangli, auspicious date picker, Chinese astrology, Chinese metaphysics, Chinese naming, Feng Shui, Zi Wei Dou Shu, Plum Blossom Numerology, lunar calendar converter.

## Why YiSphere

Many AI divination demos ask the model to invent astrology or divination results directly. That often produces incorrect pillars, wrong lunar dates, mismatched hexagrams, or unreliable Huangli recommendations.

YiSphere separates calculation from interpretation:

- Local code calculates BaZi, lunar dates, Huangli, and I Ching hexagrams.
- The LLM receives structured tool results as context.
- The LLM explains, summarizes, and asks follow-up questions, but is instructed not to rewrite calculated data.

This makes the app more suitable for real product prototypes, research demos, and Chinese metaphysics tools where structured results matter.

## Features

- **AI I Ching Divination**: casts six lines using the three-coin method, then returns the primary hexagram, moving lines, and changed hexagram.
- **BaZi / Four Pillars Calculator**: calculates year, month, day, and hour pillars from solar or lunar birth dates.
- **Liu Yao / Hexagram Reading**: provides structured hexagram data for the LLM to interpret.
- **Huangli Auspicious Date Picker**: selects suitable days for weddings, engagements, openings, moving, construction, travel, burial, and more.
- **Solar-Lunar Calendar Conversion**: converts between Gregorian dates and Chinese lunar dates.
- **Chinese Naming**: supports baby naming, company naming, pen names, and name suggestions based on BaZi, meaning, sound, and preferences.
- **Multi-Master Chat UI**: choose from many persona-based masters specializing in BaZi, I Ching, Liu Yao, Qi Men Dun Jia, Feng Shui, Zi Wei Dou Shu, naming, dreams, face reading, palm reading, and date selection.
- **OpenAI-Compatible LLM Settings**: configure Base URL, API key, and model in the UI, or use backend `.env` settings.
- **Streaming Chat**: SSE streaming response with local per-master chat history.

## Supported Use Cases

| Use Case | Description |
|----------|-------------|
| I Ching divination | Cast a hexagram and interpret the primary hexagram, moving lines, and changed hexagram. |
| BaZi reading | Calculate Four Pillars from a solar or lunar birth date and interpret the result. |
| Auspicious date selection | Pick dates for weddings, business openings, moving, travel, burial, and other events. |
| Chinese baby naming | Suggest Chinese names using BaZi, five elements, pronunciation, and meaning. |
| Company naming | Generate Chinese company names with meaning and numerology-aware suggestions. |
| Calendar conversion | Convert Gregorian dates to Chinese lunar dates and vice versa. |
| Chinese metaphysics chat | Ask follow-up questions across I Ching, BaZi, Feng Shui, Zi Wei Dou Shu, Liu Yao, and more. |

## Calculation vs AI

YiSphere does not rely on the LLM to fabricate divination data. The backend computes:

- BaZi / Four Pillars via `sxtwl`
- Solar-lunar calendar conversion via `sxtwl`
- Huangli information and auspicious dates via `cnlunar`
- I Ching hexagrams using a three-coin six-line method

The computed data is injected into the system prompt. The LLM is responsible for explanation, tone, and advice, not for recalculating or changing the tool output.

## Requirements

- Python 3.10+
- An OpenAI-compatible API key, such as DeepSeek, OpenAI, or another compatible provider

## Quick Start

### 1. Install dependencies

```bash
git clone https://github.com/0xfnzero/YiSphere.git
cd YiSphere
pip install -r requirements.txt
```

Optional virtual environment:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 2. Configure an LLM provider

```bash
cp .env.example .env
# Edit .env and set OPENAI_API_KEY
```

DeepSeek is the default compatible provider in `.env.example`. You can also use OpenAI or another OpenAI-compatible API by changing:

```bash
OPENAI_API_BASE=
OPENAI_MODEL=
OPENAI_API_KEY=
```

You can also configure the Base URL, API key, and model directly in the web UI by clicking **Model** in the top-right corner. If you choose to save the settings, the API key is stored in browser `localStorage`, which is only recommended for personal or local development environments.

### 3. Run the app

```bash
./start.sh
# or
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8000
```

Open:

```text
http://localhost:8000
```

## Example Prompts

- "Cast an I Ching hexagram for whether this project can succeed."
- "My lunar birthday is 1988.3.24 at 13:30, male. Read my BaZi."
- "Pick a few auspicious wedding dates in May 2026."
- "Which day next week is good for opening a business?"
- "A baby was born on January 1, 2020 at 10 AM, surname Li. Please suggest Chinese names."
- "Convert my Gregorian birthday 1990-05-01 to the Chinese lunar date."

## API Overview

| Method / Path | Description |
|---------------|-------------|
| `GET /api/masters` | List all chat masters and persona metadata. |
| `GET /api/llm/defaults` | Return backend LLM defaults without exposing the API key. |
| `POST /api/chat` | Non-streaming chat with automatic tool-result injection. |
| `POST /api/chat/stream` | SSE streaming chat with automatic tool-result injection. |
| `POST /api/tools/bazi` | Calculate BaZi / Four Pillars from a solar date. |
| `POST /api/tools/huangli/day` | Get Huangli information for a date. |
| `POST /api/tools/huangli/select` | Select auspicious days for an event type. |
| `POST /api/tools/iching/draw` | Cast an I Ching hexagram using the three-coin method. |
| `POST /api/tools/calendar/solar2lunar` | Convert Gregorian date to Chinese lunar date. |
| `POST /api/tools/calendar/lunar2solar` | Convert Chinese lunar date to Gregorian date. |

Chat request example with per-request LLM settings:

```json
{
  "messages": [{"role": "user", "content": "Cast an I Ching hexagram for my career decision."}],
  "master": "shengsuanzi",
  "llm": {
    "base_url": "https://api.deepseek.com",
    "api_key": "sk-...",
    "model": "deepseek-chat"
  }
}
```

## Tech Stack

| Dependency | Purpose |
|------------|---------|
| FastAPI / Uvicorn | Web server and streaming API |
| OpenAI SDK | OpenAI-compatible LLM calls |
| sxtwl | BaZi and solar-lunar calendar conversion |
| cnlunar | Huangli and auspicious date data |
| Pydantic | Request validation |
| python-dotenv | Environment variable loading |

## Project Structure

```text
YiSphere/
├── main.py
├── start.sh
├── requirements.txt
├── .env.example
├── app/
│   ├── prompts.py
│   └── services/
│       ├── chat.py
│       ├── bazi.py
│       ├── calendar.py
│       ├── huangli.py
│       └── iching.py
├── static/
│   └── index.html
└── tests/
    └── test_core_logic.py
```

## License

MIT, following the repository license.
