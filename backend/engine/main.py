#!/usr/bin/env python3
"""Gmail Bulk Delete — clean architecture version."""

import asyncio
from services.deletion_orchestrator import DeletionOrchestrator
from utils.ui import show_preset_menu


async def main_async():
    print("Gmail Bulk Delete — Smart Filtering + Async Performance\n")

    filters = show_preset_menu()
    dry_run = input("\nDry run? (y/N): ").strip().lower() == "y"

    try:
        orchestrator = DeletionOrchestrator(filters)
        return await orchestrator.execute_deletion(dry_run=dry_run)
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        return None
    except Exception as e:
        print(f"\nError: {e}")
        return None


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
