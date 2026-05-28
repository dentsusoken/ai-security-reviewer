"""SSE events endpoint for progress streaming."""

import asyncio
import json
from typing import AsyncGenerator

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.data.mock_data import MOCK_AGENT_STATES, MOCK_LOG_MESSAGES
from app.services.review_state import get_review_manager

router = APIRouter()


async def generate_real_progress_events(review_session_id: str) -> AsyncGenerator[dict, None]:
    """Generate real progress events from the review state manager."""
    manager = get_review_manager()
    state = await manager.get_review(review_session_id)

    if not state:
        # Fall back to mock events for unknown reviews
        async for event in generate_mock_progress_events(review_session_id):
            yield event
        return

    # Get the SSE queue for this review
    queue = manager.get_sse_queue(review_session_id)
    if not queue:
        # Review already completed, send final state
        if state.status == "completed" and state.result:
            yield {
                "event": "completed",
                "data": json.dumps({
                    "reviewSessionId": review_session_id,
                    "status": "completed",
                    "overall_score": state.result.overall_score,
                    "findings_count": len(state.result.findings),
                }),
            }
        elif state.status == "error":
            yield {
                "event": "error",
                "data": json.dumps({
                    "message": state.error or "Unknown error",
                }),
            }
        return

    # Stream events from the queue
    try:
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=60.0)
                if event is None:
                    # End of stream signal
                    break

                yield {
                    "event": event["event"],
                    "data": json.dumps(event["data"]),
                }

            except asyncio.TimeoutError:
                # Send keepalive
                yield {
                    "event": "keepalive",
                    "data": json.dumps({"timestamp": "keepalive"}),
                }

    except asyncio.CancelledError:
        # Client disconnected
        pass


async def generate_mock_progress_events(review_session_id: str) -> AsyncGenerator[dict, None]:
    """Generate mock progress events over ~30 seconds."""
    progress_steps = [
        (0, "リポジトリ取得中..."),
        (15, "SpecComplianceAgent 実行中..."),
        (35, "SastAnalysisAgent 実行中..."),
        (55, "SastAnalysisAgent 解析中..."),
        (72, "ReportSynthesizerAgent 準備中..."),
        (85, "レポート生成中..."),
        (95, "最終チェック中..."),
        (100, "完了"),
    ]

    log_index = 0

    for i, (progress, message) in enumerate(progress_steps):
        # Progress event
        yield {
            "event": "progress",
            "data": json.dumps({
                "percent": progress,
                "message": message,
                "elapsedMs": (i + 1) * 4000,
                "estimatedRemainingMs": max(0, (len(progress_steps) - i - 1) * 4000),
            }),
        }

        # Agent state events
        if progress == 15:
            yield {
                "event": "agent_state",
                "data": json.dumps({
                    "agentName": "SpecComplianceAgent",
                    "status": "running",
                    "progressPercent": 50,
                    "currentActivity": "OWASP ASVS カテゴリを評価中...",
                }),
            }
        elif progress == 35:
            yield {
                "event": "agent_state",
                "data": json.dumps({
                    "agentName": "SpecComplianceAgent",
                    "status": "completed",
                    "progressPercent": 100,
                    "currentActivity": "OWASP ASVS 14カテゴリを評価",
                    "details": ["🔴 2", "🟠 4", "🟡 8"],
                }),
            }
            yield {
                "event": "agent_state",
                "data": json.dumps({
                    "agentName": "SastAnalysisAgent",
                    "status": "running",
                    "progressPercent": 20,
                    "currentActivity": "Semgrep 初期化中...",
                }),
            }
        elif progress == 55:
            yield {
                "event": "agent_state",
                "data": json.dumps({
                    "agentName": "SastAnalysisAgent",
                    "status": "running",
                    "progressPercent": 67,
                    "currentActivity": "Semgrep 実行中... (245ルール適用)",
                }),
            }
        elif progress == 72:
            yield {
                "event": "agent_state",
                "data": json.dumps({
                    "agentName": "SastAnalysisAgent",
                    "status": "completed",
                    "progressPercent": 100,
                    "currentActivity": "解析完了",
                }),
            }
            yield {
                "event": "agent_state",
                "data": json.dumps({
                    "agentName": "ReportSynthesizerAgent",
                    "status": "running",
                    "progressPercent": 30,
                    "currentActivity": "結果統合中...",
                }),
            }
        elif progress == 95:
            yield {
                "event": "agent_state",
                "data": json.dumps({
                    "agentName": "ReportSynthesizerAgent",
                    "status": "completed",
                    "progressPercent": 100,
                    "currentActivity": "レポート生成完了",
                }),
            }

        # Log events (send 1-2 logs per step)
        for _ in range(2):
            if log_index < len(MOCK_LOG_MESSAGES):
                yield {
                    "event": "log",
                    "data": json.dumps({
                        "message": MOCK_LOG_MESSAGES[log_index],
                        "timestamp": f"2026-05-27T14:26:{42 + log_index:02d}Z",
                    }),
                }
                log_index += 1

        # Wait between events (simulate real processing time)
        if progress < 100:
            await asyncio.sleep(3)  # 3 seconds between events (~30s total)

    # Final completed event
    yield {
        "event": "completed",
        "data": json.dumps({
            "reviewSessionId": review_session_id,
            "status": "completed",
            "message": "レビューが完了しました",
        }),
    }


@router.get("/reviews/{review_session_id}/events")
async def stream_review_events(review_session_id: str) -> EventSourceResponse:
    """Stream review progress events via SSE.

    Events:
    - progress: Overall progress percentage
    - agent_state: Individual agent status updates
    - log: Real-time log messages
    - completed: Final completion event
    - error: Error event
    """
    return EventSourceResponse(
        generate_real_progress_events(review_session_id),
        media_type="text/event-stream",
    )
