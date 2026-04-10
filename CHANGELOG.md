# Changelog

## [2.0.0] - 2026-04-10

Major refactoring. Single entry point, typed config, full test suite.

### Breaking Changes
- Removed `gmail_bulk_delete.py` (monolithic entry point)
- Removed `gmail_bulk_delete_config.py` (JSON config entry point)
- Removed `gmail_bulk_delete_refactored.py` (renamed to `main.py`)
- Removed JSON rule-based config format (`config.json`, `smart_filters.json`)
- Removed `services/config_loader.py` (`ConfigLoader`, `RuleProcessor`, `ConfigBasedFilter`)
- Removed `utils/display_helpers.py` and `utils/config_menu.py`

### Added
- `main.py` as the single entry point
- `FilterConfig` dataclass (`models/filter_config.py`) replacing raw `Dict` everywhere
- `utils/ui.py` merging all display and menu logic into plain functions
- Dry-run mode (`--dry-run` prompt before deletion)
- Credential validation with clear error messages when `token.pickle` is missing
- 119 unit tests across 8 test files (pytest + pytest-asyncio)
- 96% code coverage, 0.80s runtime, zero real API calls
- `pyproject.toml` with pytest config and project metadata
- `requirements-dev.txt` for test dependencies
- Test plan document (`docs/plans/2026-04-10-test-suite.md`)

### Changed
- `QueryBuilder` now accepts `FilterConfig` or `dict` (auto-converts)
- `DeletionOrchestrator` now accepts `FilterConfig` or `dict`
- `GmailClient` validates credential file existence before loading
- Collapsed 3 query builder implementations into 1
- Collapsed 3 menu implementations into 1
- Collapsed 3 filter display implementations into 1
- Removed `aiohttp` from dependencies (was imported but never used)
- Relaxed version pins in `requirements.txt`

### Removed
- 1,400 lines of duplicated production code
- Dead threading code (unused `concurrent.futures` path)
- Unreachable final results printing block
- Bare `except:` handlers (replaced with `except Exception:`)

## [1.0.0] - 2025-06-04

Initial release.

- Async Gmail bulk delete with 83.7 emails/second throughput
- Smart filtering presets (newsletters, GitHub, social, promotional, large emails)
- Batch API with individual fallback
- Connection pooling and rate limit handling
- Interactive preset selection menu
- JSON rule-based configuration system
- Memory monitoring with psutil
