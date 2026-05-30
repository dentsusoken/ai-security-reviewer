"""Review session endpoints."""

import uuid
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks

from app.agents.spec_compliance_agent import get_spec_compliance_agent
from app.api.schemas.common import Perspective, ReviewDepth, ReviewStatus
from app.api.schemas.finding import FindingsResponse, FindingSummary
from app.api.schemas.review import (
    PerspectiveScore,
    ReviewCreateRequest,
    ReviewCreateResponse,
    ReviewDetail,
    ScoreSummary,
)
from app.data.mock_data import (
    DEMO_REVIEW_ID,
    MOCK_FINDINGS_LIST,
    MOCK_REVIEWS,
)
from app.services.github_service import CodeFile, GitHubService, RepoInfo
from app.services.review_state import get_review_manager

router = APIRouter()


async def run_review_task(  # noqa: C901
    review_id: str,
    repo_url: str,
    branch: str = None,
):
    """Background task to run the actual review."""
    manager = get_review_manager()
    github_service = GitHubService()
    agent = get_spec_compliance_agent()

    # Get depth from state
    state = await manager.get_review(review_id)
    depth = state.depth if state else "standard"

    # Update state to running
    await manager.update_review(
        review_id,
        status="running",
        started_at=datetime.now(),
        progress_percent=5,
        progress_message=f"レビュー開始 (深度: {depth})...",
    )

    async def progress_callback(event_type: str, data: dict):
        """Send progress updates via SSE."""
        if "progress_percent" in data:
            await manager.update_review(
                review_id,
                progress_percent=data["progress_percent"],
            )
        if "message" in data:
            await manager.update_review(
                review_id,
                progress_message=data["message"],
            )
        await manager.send_sse_event(review_id, event_type, data)

    try:
        # Step 1: Fetch repository files
        await progress_callback(
            "progress",
            {
                "percent": 10,
                "message": "リポジトリを取得中...",
            },
        )

        repo_info, code_files = await github_service.fetch_repository_files(
            repo_url,
            progress_callback=progress_callback,
        )

        if not code_files:
            raise ValueError("解析可能なコードファイルが見つかりませんでした")

        # Step 2: Run AI analysis with depth
        await progress_callback(
            "progress",
            {
                "percent": 40,
                "message": (
                    f"GPT-4o でセキュリティ解析中 [{depth}]... "
                    f"({len(code_files)} ファイル)"
                ),
            },
        )

        result = await agent.review(
            repo_info,
            code_files,
            depth=depth,
            progress_callback=progress_callback,
        )

        # Step 3: Store results
        await progress_callback(
            "progress",
            {
                "percent": 95,
                "message": "結果を保存中...",
            },
        )

        await manager.set_result(review_id, result)

        # Send completion event
        await progress_callback(
            "completed",
            {
                "review_id": review_id,
                "overall_score": result.overall_score,
                "findings_count": len(result.findings),
            },
        )

    except Exception as e:
        await manager.set_error(review_id, str(e))
        await manager.send_sse_event(
            review_id,
            "error",
            {
                "message": str(e),
            },
        )

    finally:
        # Close SSE queue
        await manager.close_sse_queue(review_id)


async def run_code_review_task(
    review_id: str,
    code: str,
    filename: str | None = None,
    language: str | None = None,
):
    """Background task to run review on pasted code."""
    manager = get_review_manager()
    agent = get_spec_compliance_agent()

    # Get depth from state
    state = await manager.get_review(review_id)
    depth = state.depth if state else "standard"

    await manager.update_review(
        review_id,
        status="running",
        started_at=datetime.now(),
        progress_percent=5,
        progress_message=f"コードレビュー開始 (深度: {depth})...",
    )

    async def progress_callback(event_type: str, data: dict):
        if "progress_percent" in data:
            await manager.update_review(
                review_id, progress_percent=data["progress_percent"]
            )
        if "message" in data:
            await manager.update_review(
                review_id, progress_message=data["message"]
            )
        await manager.send_sse_event(review_id, event_type, data)

    try:
        # Build a virtual file list from the pasted code
        file_path = filename or "code_input.txt"
        code_files = [
            CodeFile(
                path=file_path,
                content=code,
                language=language or "unknown",
            )
        ]
        repo_info = RepoInfo(
            owner="local",
            repo="code-paste",
            branch="main",
            url="",
            default_branch="main",
        )

        await progress_callback(
            "progress",
            {
                "percent": 30,
                "message": f"GPT-4o でセキュリティ解析中 [{depth}]...",
            },
        )

        result = await agent.review(
            repo_info,
            code_files,
            depth=depth,
            progress_callback=progress_callback,
        )

        await progress_callback(
            "progress",
            {"percent": 95, "message": "結果を保存中..."},
        )
        await manager.set_result(review_id, result)

        await progress_callback(
            "completed",
            {
                "review_id": review_id,
                "overall_score": result.overall_score,
                "findings_count": len(result.findings),
            },
        )

    except Exception as e:
        await manager.set_error(review_id, str(e))
        await manager.send_sse_event(review_id, "error", {"message": str(e)})
    finally:
        await manager.close_sse_queue(review_id)


@router.post("/reviews", response_model=ReviewCreateResponse)
async def create_review(
    request: ReviewCreateRequest,
    background_tasks: BackgroundTasks,
) -> ReviewCreateResponse:
    """Create a new review session.

    Starts a background task to fetch repository and run AI analysis.
    """
    manager = get_review_manager()

    # Generate review ID
    review_id = str(uuid.uuid4())

    # Build perspectives list
    perspectives = [p.value for p in request.perspectives]

    if request.input_type == "code" and request.code:
        # Code-paste flow
        await manager.create_review(
            review_id=review_id,
            repo_url="",
            input_type="code",
            perspectives=perspectives,
            depth=request.depth.value,
        )
        background_tasks.add_task(
            run_code_review_task,
            review_id,
            request.code,
            request.filename,
            request.language,
        )
    elif request.repo_url:
        # GitHub flow
        await manager.create_review(
            review_id=review_id,
            repo_url=request.repo_url,
            branch=request.branch,
            input_type="github",
            perspectives=perspectives,
            depth=request.depth.value,
        )
        background_tasks.add_task(
            run_review_task,
            review_id,
            request.repo_url,
            request.branch,
        )
    else:
        # Fall back to demo mode
        return ReviewCreateResponse(
            reviewSessionId=DEMO_REVIEW_ID,
            status=ReviewStatus.QUEUED,
        )

    return ReviewCreateResponse(
        reviewSessionId=review_id,
        status=ReviewStatus.QUEUED,
    )


@router.post("/reviews/{review_session_id}/rerun", response_model=ReviewCreateResponse)
async def rerun_review(
    review_session_id: str,
    background_tasks: BackgroundTasks,
) -> ReviewCreateResponse:
    """Re-run an existing review with the same parameters.

    Creates a new review session based on the original's settings.
    """
    manager = get_review_manager()
    original = await manager.get_review(review_session_id)
    if not original:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Original review not found")

    new_id = str(uuid.uuid4())

    if original.input_type == "code":
        # For code reviews we can't re-run without the original code
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400,
            detail="Re-run of code-paste reviews is not supported. Create a new review.",
        )

    await manager.create_review(
        review_id=new_id,
        repo_url=original.repo_url,
        branch=original.branch,
        input_type=original.input_type,
        perspectives=original.perspectives,
        depth=original.depth,
    )

    background_tasks.add_task(
        run_review_task,
        new_id,
        original.repo_url,
        original.branch,
    )

    return ReviewCreateResponse(
        reviewSessionId=new_id,
        status=ReviewStatus.QUEUED,
    )


@router.get("/reviews/{review_session_id}", response_model=ReviewDetail)
async def get_review(review_session_id: str) -> ReviewDetail:
    """Get review session details."""
    manager = get_review_manager()
    state = await manager.get_review(review_session_id)

    if state and state.result:
        # Return real review result
        result = state.result
        return ReviewDetail(
            id=review_session_id,
            status=ReviewStatus(state.status),
            inputType="github",
            repoUrl=state.repo_url,
            branch=state.branch or result.repo_info.branch,
            perspectives=[Perspective.ASVS],
            depth=ReviewDepth(state.depth) if state.depth else ReviewDepth.STANDARD,
            startedAt=state.started_at,
            completedAt=state.completed_at,
            durationMs=state.duration_ms,
            scoreSummary=ScoreSummary(
                overall=result.overall_score,
                critical=result.critical_count,
                high=result.high_count,
                medium=result.medium_count,
                low=result.low_count,
            ),
            perspectiveScores=[
                PerspectiveScore(
                    category=ps.get("category", ""),
                    percentage=ps.get("percentage", 0),
                )
                for ps in result.perspective_scores
            ],
        )

    if state:
        # Review in progress or error
        status_map = {
            "queued": ReviewStatus.QUEUED,
            "running": ReviewStatus.RUNNING,
            "completed": ReviewStatus.COMPLETED,
            "error": ReviewStatus.FAILED,
        }
        mapped_status = status_map.get(state.status, ReviewStatus.RUNNING)

        return ReviewDetail(
            id=review_session_id,
            status=mapped_status,
            inputType="github",
            repoUrl=state.repo_url,
            branch=state.branch,
            perspectives=[Perspective.ASVS],
            depth=ReviewDepth(state.depth) if state.depth else ReviewDepth.STANDARD,
            startedAt=state.started_at,
            completedAt=state.completed_at,
            durationMs=state.duration_ms,
            scoreSummary=None,
            perspectiveScores=None,
        )

    # Fall back to mock data for demo ID
    review_data = MOCK_REVIEWS.get(review_session_id)
    if review_data is None:
        review_data = MOCK_REVIEWS[DEMO_REVIEW_ID]

    return ReviewDetail(**review_data)


@router.get("/reviews/{review_session_id}/findings", response_model=FindingsResponse)
async def get_review_findings(review_session_id: str) -> FindingsResponse:
    """Get findings for a review session."""
    manager = get_review_manager()
    state = await manager.get_review(review_session_id)

    if state and state.result and state.result.findings:
        # Return real findings
        findings = []
        for f in state.result.findings:
            findings.append(
                FindingSummary(
                    id=f.get("id", "unknown"),
                    severity=f.get("severity", "medium"),
                    title=f.get("title", "セキュリティの問題"),
                    filePath=f.get("file_path", "unknown"),
                    lineStart=f.get("line_start"),
                    asvsRequirementIds=f.get("asvs_requirements", []),
                    cweIds=f.get("cwe_ids", []),
                )
            )
        return FindingsResponse(findings=findings)

    # Fall back to mock data
    findings = [FindingSummary(**f) for f in MOCK_FINDINGS_LIST]
    return FindingsResponse(findings=findings)


@router.get("/reviews/{review_session_id}/debug")
async def get_review_debug(review_session_id: str) -> dict:
    """Debug endpoint to get review state including error."""
    manager = get_review_manager()
    state = await manager.get_review(review_session_id)

    if not state:
        return {"error": "Review not found", "id": review_session_id}

    return {
        "id": state.id,
        "status": state.status,
        "repo_url": state.repo_url,
        "depth": state.depth,
        "error": state.error,
        "progress_percent": state.progress_percent,
        "progress_message": state.progress_message,
        "started_at": str(state.started_at) if state.started_at else None,
        "completed_at": str(state.completed_at) if state.completed_at else None,
    }
