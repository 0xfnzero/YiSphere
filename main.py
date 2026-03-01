# -*- coding: utf-8 -*-
"""YiSphere 易道预测 - FastAPI 入口。"""

import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

import json

import urllib.request

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.prompts import MASTERS
from app.services.chat import chat_service
from app.services.bazi import bazi_service
from app.services.huangli import huangli_service
from app.services.iching import iching_service
from app.services.calendar import calendar_service

app = FastAPI(title="YiSphere 易道预测", description="易经·八字·六爻·黄道吉日 + AI 对话")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- 请求/响应模型 ----------
class ChatMessage(BaseModel):
    role: str  # user | assistant
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    master: str | None = None  # 角色 id：shengsuanzi / naming / bazi / liuyao / qimen / fengshui


class ChatResponse(BaseModel):
    message: ChatMessage


class BaziRequest(BaseModel):
    year: int
    month: int
    day: int
    hour: int | None = None


class HuangliDayRequest(BaseModel):
    year: int
    month: int
    day: int
    hour: int = 12


class HuangliSelectRequest(BaseModel):
    start_date: str  # YYYY-MM-DD
    end_date: str
    event_type: str  # 婚嫁/开业/入宅/动土/安葬/订婚/出行 等
    max_days: int = 30


class Solar2LunarRequest(BaseModel):
    year: int
    month: int
    day: int


class Lunar2SolarRequest(BaseModel):
    lunar_year: int
    lunar_month: int
    lunar_day: int
    is_leap_month: bool = False


# ---------- 角色与对话 ----------
@app.get("/api/masters")
def api_masters():
    """可选大师角色列表，用于前端下拉。"""
    return list(MASTERS.values())


@app.get("/api/avatar/{master_id}", response_class=Response)
def api_avatar(master_id: str):
    """头像代理：避免外链图片被拦截或跨域不显示。"""
    master = MASTERS.get(master_id)
    if not master:
        raise HTTPException(status_code=404, detail="角色不存在")
    url = master.get("avatar_url")
    if not url:
        raise HTTPException(status_code=404, detail="该角色无头像")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "YiSphere/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            content_type = resp.headers.get("Content-Type", "image/jpeg")
            return Response(content=data, media_type=content_type)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"头像加载失败: {e!s}")


@app.post("/api/chat", response_model=ChatResponse)
async def api_chat(req: ChatRequest):
    """多轮对话（非流式）。"""
    messages = [{"role": m.role, "content": m.content} for m in req.messages]
    reply = await chat_service.reply(messages, inject_tools=True, master_id=req.master)
    return ChatResponse(message=ChatMessage(role=reply["role"], content=reply["content"]))


@app.post("/api/chat/stream")
async def api_chat_stream(req: ChatRequest):
    """流式对话：返回 SSE，前端可逐字显示。"""
    messages = [{"role": m.role, "content": m.content} for m in req.messages]

    async def event_stream():
        async for chunk in chat_service.reply_stream(
            messages, inject_tools=True, master_id=req.master
        ):
            yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------- 工具接口（可选，供前端或其它服务直接调用）----------
@app.post("/api/tools/bazi")
def api_bazi(req: BaziRequest):
    """根据公历年月日时计算八字四柱。"""
    return bazi_service.get_si_zhu(req.year, req.month, req.day, req.hour)


@app.post("/api/tools/huangli/day")
def api_huangli_day(req: HuangliDayRequest):
    """查询某日黄历（宜忌、吉神凶神等）。"""
    return huangli_service.get_day_info(req.year, req.month, req.day, req.hour)


@app.post("/api/tools/huangli/select")
def api_huangli_select(req: HuangliSelectRequest):
    """在日期范围内筛选黄道吉日。event_type: 婚嫁/开业/入宅/动土/安葬/订婚/出行 等。"""
    import datetime
    start = datetime.datetime.strptime(req.start_date, "%Y-%m-%d").date()
    end = datetime.datetime.strptime(req.end_date, "%Y-%m-%d").date()
    return huangli_service.select_auspicious_days(start, end, req.event_type, req.max_days)


@app.post("/api/tools/iching/draw")
def api_iching_draw():
    """随机起一卦。"""
    return iching_service.draw_random()


@app.post("/api/tools/calendar/solar2lunar")
def api_calendar_solar2lunar(req: Solar2LunarRequest):
    """公历日期转农历（如身份证上的生日对应农历哪天）。"""
    return calendar_service.solar2lunar(req.year, req.month, req.day)


@app.post("/api/tools/calendar/lunar2solar")
def api_calendar_lunar2solar(req: Lunar2SolarRequest):
    """农历日期转公历。"""
    return calendar_service.lunar2solar(
        req.lunar_year, req.lunar_month, req.lunar_day, req.is_leap_month
    )


# ---------- 静态前端 ----------
frontend_dir = Path(__file__).parent / "static"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
