"""Cleanup endpoints — preview and live deletion."""

import sys
import os
import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "engine"))

from models.filter_config import FilterConfig
from services.query_builder import QueryBuilder
from services.gmail_client import GmailClient
from services.email_deleter import EmailDeleter
from services.performance_tracker import PerformanceTracker
from constants import EMAILS_PER_CHUNK, MAX_CONCURRENT_TASKS, EMAILS_PER_TASK

router = APIRouter()


@router.post("/cleanup/preview")
async def preview_cleanup(filters: dict):
    """Dry run — returns estimated email count for given filters."""
    config = FilterConfig.from_dict(filters)
    query = QueryBuilder(config).build_query()

    # For now, use token.pickle from engine dir
    engine_dir = os.path.join(os.path.dirname(__file__), "..", "..", "engine")
    original_dir = os.getcwd()
    os.chdir(engine_dir)

    try:
        client = GmailClient()
        count = await client.get_initial_email_count(query)
        return {
            "estimated_count": count,
            "query": query,
            "filter_summary": config.to_dict(),
        }
    finally:
        os.chdir(original_dir)


@router.websocket("/cleanup/run")
async def run_cleanup(websocket: WebSocket):
    """Live deletion with WebSocket progress updates."""
    await websocket.accept()

    try:
        data = await websocket.receive_json()
        filters = data.get("filters", {})
        config = FilterConfig.from_dict(filters)
        query = QueryBuilder(config).build_query()

        engine_dir = os.path.join(os.path.dirname(__file__), "..", "..", "engine")
        original_dir = os.getcwd()
        os.chdir(engine_dir)

        try:
            client = GmailClient()
            deleter = EmailDeleter(client)
            tracker = PerformanceTracker()

            service = await client.get_service()
            initial_count = await client.get_initial_email_count(query)

            await websocket.send_json({
                "type": "start",
                "estimated": initial_count,
                "query": query,
            })

            tracker.start_tracking()
            batch_number = 0

            while True:
                ids = await client.get_email_batch(query, EMAILS_PER_CHUNK)
                if not ids:
                    break

                batch_number += 1
                deleted, errors = 0, 0

                batches = [
                    ids[i:i + EMAILS_PER_TASK]
                    for i in range(0, len(ids), EMAILS_PER_TASK)
                ]

                semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

                async def run_batch(batch):
                    async with semaphore:
                        return await deleter.delete_email_batch(batch)

                results = await asyncio.gather(
                    *(run_batch(b) for b in batches),
                    return_exceptions=True,
                )

                for r in results:
                    if isinstance(r, Exception):
                        errors += 1
                    else:
                        d, e = r
                        deleted += d
                        errors += e
                        tracker.update_stats(d, e)

                total = tracker.stats.total_deleted
                rate = tracker.get_current_rate(total)
                pct = min((total / initial_count) * 100, 100) if initial_count > 0 else 0

                await websocket.send_json({
                    "type": "progress",
                    "batch": batch_number,
                    "batch_deleted": deleted,
                    "batch_errors": errors,
                    "total_deleted": total,
                    "total_errors": tracker.stats.total_errors,
                    "rate": round(rate, 1),
                    "progress_pct": round(pct, 1),
                })

                await asyncio.sleep(0.05)

            final = tracker.get_final_results()
            await websocket.send_json({
                "type": "complete",
                **final,
            })

        finally:
            os.chdir(original_dir)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
