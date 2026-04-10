"""User interface — display helpers, menus, progress."""

from typing import Union
from constants import FILTER_PRESETS, DEFAULT_FILTERS, PROGRESS_BAR_WIDTH
from models.filter_config import FilterConfig


# ---------------------------------------------------------------------------
# Filter display
# ---------------------------------------------------------------------------

def print_filter_summary(filters: Union[FilterConfig, dict]):
    if isinstance(filters, dict):
        filters = FilterConfig.from_dict(filters)

    print("SMART FILTERING ACTIVE:")
    f = filters

    if f.older_than_days:
        print(f"   Age: Older than {f.older_than_days} days")
    if f.min_size_mb or f.max_size_mb:
        lo = f"Larger than {f.min_size_mb}MB" if f.min_size_mb else ""
        hi = f"Smaller than {f.max_size_mb}MB" if f.max_size_mb else ""
        print(f"   Size: {', '.join(p for p in [lo, hi] if p)}")
    if f.sender_domains:
        print(f"   Sender domains: {', '.join(f.sender_domains)}")
    if f.sender_emails:
        print(f"   Sender emails: {', '.join(f.sender_emails)}")
    if f.subject_keywords:
        print(f"   Subject contains: {', '.join(f.subject_keywords)}")

    exclusions = []
    if f.exclude_attachments:
        exclusions.append("attachments")
    if f.exclude_important:
        exclusions.append("important")
    if f.exclude_starred:
        exclusions.append("starred")
    if exclusions:
        print(f"   Excluding: {', '.join(exclusions)}")
    if f.exclude_senders:
        print(f"   Never delete from: {', '.join(f.exclude_senders)}")
    print()


# ---------------------------------------------------------------------------
# Progress display
# ---------------------------------------------------------------------------

def print_progress_bar(current: int, total: int):
    if total <= 0:
        print(f"   Processed: {current} emails")
        return
    progress = min((current / total) * 100, 100)
    filled = int(PROGRESS_BAR_WIDTH * progress / 100)
    bar = "=" * filled + "-" * (PROGRESS_BAR_WIDTH - filled)
    remaining = max(0, total - current)
    print(f"   [{bar}] {progress:.1f}% (~{remaining} remaining)")


def print_batch_stats(batch_num: int, email_count: int,
                      duration: float, rate: float,
                      total_deleted: int, memory_mb: float):
    print(f"   Batch complete: {email_count} emails in {duration:.1f}s")
    print(f"   Batch rate: {rate:.1f} emails/second")
    print(f"   Total deleted: {total_deleted}")
    print(f"   Memory: {memory_mb:.1f} MB")


# ---------------------------------------------------------------------------
# Preset menu
# ---------------------------------------------------------------------------

def show_preset_menu() -> FilterConfig:
    print("FILTER PRESETS:")
    print("=" * 50)

    presets = {
        "1": ("default", "Default - 6 months old, preserve attachments"),
        "2": ("newsletters", "Newsletter cleanup - 30 days, newsletter keywords"),
        "3": ("github_notifications", "GitHub notifications - 7 days old"),
        "4": ("large_emails", "Large emails - 90 days, 10MB+ size"),
        "5": ("social_media", "Social media - 14 days, FB/Twitter/LinkedIn"),
        "6": ("promotional", "Promotional emails - 60 days, sale keywords"),
    }

    for key, (_, desc) in presets.items():
        print(f"   {key}. {desc}")
    print("   7. Custom filters (advanced)")
    print()

    choice = input("Choose preset (1-7) [1]: ").strip()

    if choice in ("1", ""):
        return FilterConfig.from_dict(DEFAULT_FILTERS)
    elif choice in presets:
        return FilterConfig.from_dict(FILTER_PRESETS[presets[choice][0]])
    elif choice == "7":
        return _get_custom_filters()
    else:
        print("Invalid choice, using default.")
        return FilterConfig.from_dict(DEFAULT_FILTERS)


def _get_custom_filters() -> FilterConfig:
    print("\nCUSTOM FILTER CONFIGURATION:")
    print("=" * 40)

    cfg = FilterConfig()

    age = input(f"Older than N days [{cfg.older_than_days}]: ").strip()
    if age:
        try:
            cfg.older_than_days = int(age)
        except ValueError:
            print("Invalid number, keeping default.")

    for label, attr in [("Min size MB", "min_size_mb"), ("Max size MB", "max_size_mb")]:
        val = input(f"{label} (empty = no limit): ").strip()
        if val:
            try:
                setattr(cfg, attr, int(val))
            except ValueError:
                print("Invalid number, skipping.")

    domains = input("Sender domains (comma-separated): ").strip()
    if domains:
        cfg.sender_domains = [d.strip() for d in domains.split(",") if d.strip()]

    emails = input("Sender emails (comma-separated): ").strip()
    if emails:
        cfg.sender_emails = [e.strip() for e in emails.split(",") if e.strip()]

    keywords = input("Subject keywords (comma-separated): ").strip()
    if keywords:
        cfg.subject_keywords = [k.strip() for k in keywords.split(",") if k.strip()]

    print("\nCustom filters configured.")
    return cfg
