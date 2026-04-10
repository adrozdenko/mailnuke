# Test Suite Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Plan ID:** `plan-1775773555508-gakbo5`
**Goal:** 90%+ line coverage across services/ and models/, 40+ test cases, CI-ready without credentials.
**Tech Stack:** pytest >= 8.0, pytest-asyncio >= 0.23, unittest.mock

**Alternatives rejected:**
- (A) unittest — no pytest-asyncio, worse fixture model
- (B) Real Gmail sandbox — requires credentials, flaky, slow, not CI-friendly

## Tasks

### 1. Test infrastructure setup
- Create `tests/__init__.py`, `tests/conftest.py`
- Fixtures: `mock_gmail_service`, `sample_filters`, `sample_message_ids`
- `pyproject.toml` pytest config (asyncio_mode = auto)
- `requirements-dev.txt` with pytest>=8.0, pytest-asyncio>=0.23

### 2. Test models (~8 tests)
`tests/test_models.py`
- DeletionResult: total_processed, success_rate, deletion_rate
- BatchResult: batch_rate normal + zero duration
- PerformanceStats: batch_api_efficiency normal + zero total

### 3. Test QueryBuilder (~12 tests)
`tests/test_query_builder.py`
- Date-only, size-only, sender domains (single + multiple OR)
- Sender emails, subject keywords, all exclusions
- Combined filters, empty filters
- Verify exact Gmail query string output

### 4. Test PerformanceTracker (~8 tests)
`tests/test_performance_tracker.py`
- start_tracking, record_batch_performance
- Rolling window >10 samples drops oldest
- get_current_rate, get_recent_average_rate
- should_print_periodic_status timing
- update_stats accumulation, get_final_results shape
- success_rate with 0 total
- Mock psutil for memory

### 5. Test EmailDeleter (~6 tests)
`tests/test_email_deleter.py`
- Batch delete succeeds (batchModify called)
- Batch fails, individual fallback succeeds
- HttpError 429 triggers rate limit + backoff
- HttpError 400 returns False immediately
- All retries exhausted returns (0, N)

### 6. Test GmailClient (~6 tests)
`tests/test_gmail_client.py`
- Missing token.pickle raises FileNotFoundError
- get_service() creates on first, reuses on second
- connection_reuse_count increments
- get_initial_email_count returns estimate
- get_email_batch returns IDs / empty on no results

### 7. Test ConfigLoader (~6 tests)
`tests/test_config_loader.py`
- ConfigLoader loads config.json presets
- get_preset_names, get_preset
- RuleProcessor.build_gmail_query for each rule type
- ConfigBasedFilter create_filter_from_preset / from_rules

### 8. Test DeletionOrchestrator (~5 tests)
`tests/test_orchestrator.py`
- dry_run=True returns without calling delete
- _create_task_batches splits correctly
- _process_task_results handles Exception in results
- execute_deletion loops until get_email_batch returns empty

### 9. Integration test (1 test)
`tests/test_integration.py`
- Mock Gmail service: list() returns 5 IDs first, empty second
- batchModify() succeeds
- Assert total_deleted=5, total_errors=0
- Assert results dict has correct keys

## Execution order
1 (infra) -> 2,3 (pure logic, parallel) -> 4 (tracker) -> 5,6 (mocked API, parallel) -> 7 (config) -> 8 (orchestrator) -> 9 (integration)
