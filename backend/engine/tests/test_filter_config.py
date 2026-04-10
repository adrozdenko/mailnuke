"""Tests for models/filter_config.py."""

from models.filter_config import FilterConfig


# -- from_dict ----------------------------------------------------------------


class TestFilterConfigFromDict:
    def test_overrides_selected_fields(self):
        fc = FilterConfig.from_dict({"older_than_days": 30, "sender_domains": ["spam.com"]})
        assert fc.older_than_days == 30
        assert fc.sender_domains == ["spam.com"]
        # non-overridden fields keep defaults
        assert fc.exclude_attachments is True

    def test_ignores_unknown_keys(self):
        fc = FilterConfig.from_dict({"older_than_days": 30, "bogus_key": "whatever"})
        assert fc.older_than_days == 30
        assert not hasattr(fc, "bogus_key")

    def test_ignores_multiple_unknown_keys_mixed_with_valid(self):
        fc = FilterConfig.from_dict({
            "older_than_days": 7,
            "nope": 1,
            "also_nope": True,
            "sender_emails": ["a@b.com"],
        })
        assert fc.older_than_days == 7
        assert fc.sender_emails == ["a@b.com"]
        assert not hasattr(fc, "nope")
        assert not hasattr(fc, "also_nope")

    def test_empty_dict_gives_defaults(self):
        fc = FilterConfig.from_dict({})
        assert fc == FilterConfig()

    def test_all_fields_roundtrip(self):
        original = FilterConfig(
            older_than_days=14,
            exclude_attachments=False,
            exclude_important=False,
            exclude_starred=False,
            min_size_mb=1,
            max_size_mb=50,
            sender_domains=["x.com"],
            sender_emails=["a@b.com"],
            exclude_senders=["boss@work.com"],
            subject_keywords=["sale", "promo"],
            exclude_labels=["INBOX"],
        )
        rebuilt = FilterConfig.from_dict(original.to_dict())
        assert rebuilt == original


# -- to_dict ------------------------------------------------------------------


class TestFilterConfigToDict:
    def test_returns_plain_dict(self):
        d = FilterConfig(older_than_days=7, sender_emails=["a@b.com"]).to_dict()
        assert isinstance(d, dict)
        assert d["older_than_days"] == 7
        assert d["sender_emails"] == ["a@b.com"]

    def test_none_values_preserved(self):
        d = FilterConfig().to_dict()
        assert d["min_size_mb"] is None
        assert d["max_size_mb"] is None

    def test_list_fields_are_independent_copies(self):
        fc = FilterConfig(sender_domains=["a.com"])
        d = fc.to_dict()
        d["sender_domains"].append("b.com")
        assert fc.sender_domains == ["a.com"]  # original unchanged


# -- roundtrip ----------------------------------------------------------------


class TestFilterConfigRoundtrip:
    def test_default_survives_roundtrip(self):
        fc = FilterConfig()
        assert FilterConfig.from_dict(fc.to_dict()) == fc

    def test_custom_config_survives_roundtrip(self):
        fc = FilterConfig(
            older_than_days=14,
            min_size_mb=5,
            sender_domains=["x.com"],
            subject_keywords=["sale"],
        )
        assert FilterConfig.from_dict(fc.to_dict()) == fc
