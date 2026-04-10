"""Tests for services/query_builder.py — pure logic, zero mocks."""

import re
from datetime import datetime, timedelta

import pytest

from models.filter_config import FilterConfig
from services.query_builder import QueryBuilder


# ---------------------------------------------------------------------------
# Date filters
# ---------------------------------------------------------------------------


def test_build_query_older_than_days_produces_before_date():
    query = QueryBuilder({"older_than_days": 30}).build_query()

    expected_date = (datetime.now() - timedelta(days=30)).strftime("%Y/%m/%d")
    assert f"before:{expected_date}" in query


def test_build_query_older_than_days_none_omits_before():
    query = QueryBuilder({"older_than_days": None}).build_query()

    assert "before:" not in query


def test_build_query_older_than_days_zero_omits_before():
    query = QueryBuilder({"older_than_days": 0}).build_query()

    assert "before:" not in query


# ---------------------------------------------------------------------------
# Size filters
# ---------------------------------------------------------------------------


def test_build_query_min_size_produces_larger():
    query = QueryBuilder({"min_size_mb": 10}).build_query()

    assert "larger:10M" in query


def test_build_query_max_size_produces_smaller():
    query = QueryBuilder({"max_size_mb": 5}).build_query()

    assert "smaller:5M" in query


def test_build_query_both_sizes_produces_larger_and_smaller():
    query = QueryBuilder({"min_size_mb": 5, "max_size_mb": 20}).build_query()

    assert "larger:5M" in query
    assert "smaller:20M" in query


def test_build_query_no_sizes_omits_larger_and_smaller():
    query = QueryBuilder({"min_size_mb": None, "max_size_mb": None}).build_query()

    assert "larger:" not in query
    assert "smaller:" not in query


# ---------------------------------------------------------------------------
# Sender domain filters
# ---------------------------------------------------------------------------


def test_build_query_single_sender_domain_no_or_group():
    query = QueryBuilder({"sender_domains": ["spam.com"]}).build_query()

    assert "from:@spam.com" in query
    assert "OR" not in query


def test_build_query_multiple_sender_domains_or_group():
    query = QueryBuilder({"sender_domains": ["a.com", "b.com"]}).build_query()

    assert "(from:@a.com OR from:@b.com)" in query


def test_build_query_three_sender_domains_or_group():
    query = QueryBuilder(
        {"sender_domains": ["a.com", "b.com", "c.com"]}
    ).build_query()

    assert "(from:@a.com OR from:@b.com OR from:@c.com)" in query


# ---------------------------------------------------------------------------
# Sender email filters
# ---------------------------------------------------------------------------


def test_build_query_single_sender_email_no_or_group():
    query = QueryBuilder({"sender_emails": ["bot@gh.com"]}).build_query()

    assert "from:bot@gh.com" in query
    assert "OR" not in query


def test_build_query_multiple_sender_emails_or_group():
    query = QueryBuilder(
        {"sender_emails": ["a@x.com", "b@y.com"]}
    ).build_query()

    assert "(from:a@x.com OR from:b@y.com)" in query


# ---------------------------------------------------------------------------
# Subject keyword filters
# ---------------------------------------------------------------------------


def test_build_query_single_subject_keyword_no_or_group():
    query = QueryBuilder({"subject_keywords": ["sale"]}).build_query()

    assert 'subject:"sale"' in query
    assert "OR" not in query


def test_build_query_multiple_subject_keywords_or_group():
    query = QueryBuilder(
        {"subject_keywords": ["sale", "promo"]}
    ).build_query()

    assert '(subject:"sale" OR subject:"promo")' in query


# ---------------------------------------------------------------------------
# Exclusion flags
# ---------------------------------------------------------------------------


def test_build_query_exclude_attachments_true_adds_flag():
    query = QueryBuilder({"exclude_attachments": True}).build_query()

    assert "-has:attachment" in query


def test_build_query_exclude_attachments_false_omits_flag():
    query = QueryBuilder({"exclude_attachments": False}).build_query()

    assert "-has:attachment" not in query


def test_build_query_exclude_important_true_adds_flag():
    query = QueryBuilder({"exclude_important": True}).build_query()

    assert "-is:important" in query


def test_build_query_exclude_important_false_omits_flag():
    query = QueryBuilder({"exclude_important": False}).build_query()

    assert "-is:important" not in query


def test_build_query_exclude_starred_true_adds_flag():
    query = QueryBuilder({"exclude_starred": True}).build_query()

    assert "-is:starred" in query


def test_build_query_exclude_starred_false_omits_flag():
    query = QueryBuilder({"exclude_starred": False}).build_query()

    assert "-is:starred" not in query


def test_build_query_exclude_senders_adds_negative_from():
    query = QueryBuilder({"exclude_senders": ["boss@co.com"]}).build_query()

    assert "-from:boss@co.com" in query


def test_build_query_multiple_exclude_senders_adds_each():
    query = QueryBuilder(
        {"exclude_senders": ["boss@co.com", "ceo@co.com"]}
    ).build_query()

    assert "-from:boss@co.com" in query
    assert "-from:ceo@co.com" in query


def test_build_query_exclude_labels_lowercased():
    query = QueryBuilder({"exclude_labels": ["TRASH", "SPAM"]}).build_query()

    assert "-in:trash" in query
    assert "-in:spam" in query


def test_build_query_exclude_labels_empty_omits_in():
    query = QueryBuilder({"exclude_labels": []}).build_query()

    assert "-in:" not in query


# ---------------------------------------------------------------------------
# Combined / integration
# ---------------------------------------------------------------------------


def test_build_query_full_filter_set_contains_all_parts():
    filters = {
        "older_than_days": 60,
        "min_size_mb": 5,
        "max_size_mb": 50,
        "sender_domains": ["news.com"],
        "sender_emails": ["alerts@shop.com"],
        "subject_keywords": ["digest"],
        "exclude_attachments": True,
        "exclude_important": True,
        "exclude_starred": True,
        "exclude_senders": ["vip@co.com"],
        "exclude_labels": ["TRASH"],
    }
    query = QueryBuilder(filters).build_query()

    assert "before:" in query
    assert "larger:5M" in query
    assert "smaller:50M" in query
    assert "from:@news.com" in query
    assert "from:alerts@shop.com" in query
    assert 'subject:"digest"' in query
    assert "-has:attachment" in query
    assert "-is:important" in query
    assert "-is:starred" in query
    assert "-from:vip@co.com" in query
    assert "-in:trash" in query


def test_build_query_default_filters_include_exclusion_flags():
    query = QueryBuilder({}).build_query()

    # Default FilterConfig has these True
    assert "-has:attachment" in query
    assert "-is:important" in query
    assert "-is:starred" in query
    # Default exclude_labels
    assert "-in:trash" in query
    assert "-in:spam" in query


def test_build_query_default_filters_include_before_date():
    query = QueryBuilder({}).build_query()

    # Default older_than_days is 180
    expected_date = (datetime.now() - timedelta(days=180)).strftime("%Y/%m/%d")
    assert f"before:{expected_date}" in query


def test_build_query_empty_lists_produce_no_sender_or_subject():
    query = QueryBuilder(
        {
            "sender_domains": [],
            "sender_emails": [],
            "subject_keywords": [],
            "exclude_senders": [],
        }
    ).build_query()

    assert "from:" not in query
    assert "subject:" not in query


# ---------------------------------------------------------------------------
# Dict input auto-converts to FilterConfig
# ---------------------------------------------------------------------------


def test_build_query_dict_input_auto_converts_to_filter_config():
    dict_query = QueryBuilder({"older_than_days": 90, "min_size_mb": 2}).build_query()
    fc_query = QueryBuilder(
        FilterConfig(older_than_days=90, min_size_mb=2)
    ).build_query()

    assert dict_query == fc_query


def test_build_query_dict_ignores_unknown_keys():
    # from_dict filters unknown keys; just make sure it doesn't blow up
    query = QueryBuilder(
        {"older_than_days": 30, "bogus_key": "whatever"}
    ).build_query()

    expected_date = (datetime.now() - timedelta(days=30)).strftime("%Y/%m/%d")
    assert f"before:{expected_date}" in query


# ---------------------------------------------------------------------------
# Query ordering — date, size, senders, subjects, exclusions
# ---------------------------------------------------------------------------


def test_build_query_parts_appear_in_expected_order():
    filters = {
        "older_than_days": 10,
        "min_size_mb": 1,
        "sender_domains": ["x.com"],
        "subject_keywords": ["promo"],
        "exclude_attachments": True,
    }
    query = QueryBuilder(filters).build_query()

    before_pos = query.index("before:")
    larger_pos = query.index("larger:")
    from_pos = query.index("from:")
    subject_pos = query.index("subject:")
    exclude_pos = query.index("-has:attachment")

    assert before_pos < larger_pos < from_pos < subject_pos < exclude_pos
