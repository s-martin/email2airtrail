"""Tests for config.py."""
import os
import pytest
from unittest.mock import patch


class TestConfig:
    def test_default_imap_port(self):
        with patch.dict(os.environ, {}, clear=True):
            import importlib
            import config as cfg_module
            importlib.reload(cfg_module)
            assert cfg_module.Config.IMAP_PORT == 993

    def test_custom_imap_port(self):
        with patch.dict(os.environ, {"IMAP_PORT": "143"}, clear=False):
            import importlib
            import config as cfg_module
            importlib.reload(cfg_module)
            assert cfg_module.Config.IMAP_PORT == 143

    def test_default_check_interval(self):
        with patch.dict(os.environ, {}, clear=True):
            import importlib
            import config as cfg_module
            importlib.reload(cfg_module)
            assert cfg_module.Config.CHECK_INTERVAL_MINUTES == 10

    def test_custom_check_interval(self):
        with patch.dict(os.environ, {"CHECK_INTERVAL_MINUTES": "30"}, clear=False):
            import importlib
            import config as cfg_module
            importlib.reload(cfg_module)
            assert cfg_module.Config.CHECK_INTERVAL_MINUTES == 30

    def test_default_flight_pattern_file(self):
        with patch.dict(os.environ, {}, clear=True):
            import importlib
            import config as cfg_module
            importlib.reload(cfg_module)
            assert cfg_module.Config.FLIGHT_PATTERN_FILE == "bcd_travel"

    def test_email_senders_split_on_comma(self):
        with patch.dict(os.environ, {"EMAIL_SENDERS": "a@a.com,b@b.com"}, clear=False):
            import importlib
            import config as cfg_module
            importlib.reload(cfg_module)
            assert cfg_module.Config.EMAIL_SENDERS == ["a@a.com", "b@b.com"]

    def test_email_senders_default_empty(self):
        with patch.dict(os.environ, {"EMAIL_SENDERS": ""}, clear=False):
            import importlib
            import config as cfg_module
            importlib.reload(cfg_module)
            assert cfg_module.Config.EMAIL_SENDERS == []

    def test_email_senders_whitespace_only(self):
        with patch.dict(os.environ, {"EMAIL_SENDERS": "  , , "}, clear=False):
            import importlib
            import config as cfg_module
            importlib.reload(cfg_module)
            assert cfg_module.Config.EMAIL_SENDERS == []

    def test_reads_imap_server_from_env(self):
        with patch.dict(os.environ, {"IMAP_SERVER": "imap.test.com"}, clear=False):
            import importlib
            import config as cfg_module
            importlib.reload(cfg_module)
            assert cfg_module.Config.IMAP_SERVER == "imap.test.com"

    def test_reads_airtrail_api_url_from_env(self):
        with patch.dict(os.environ, {"AIRTRAIL_API_URL": "http://api.example.com"}, clear=False):
            import importlib
            import config as cfg_module
            importlib.reload(cfg_module)
            assert cfg_module.Config.AIRTRAIL_API_URL == "http://api.example.com"


class TestConfigValidate:
    def _make_config(self, env_overrides):
        with patch.dict(os.environ, env_overrides, clear=False):
            import importlib
            import config as cfg_module
            importlib.reload(cfg_module)
            return cfg_module.Config

    def test_validate_passes_when_all_required_vars_set(self):
        env = {
            "IMAP_SERVER": "imap.example.com",
            "EMAIL_ADDRESS": "user@example.com",
            "AIRTRAIL_API_URL": "http://api.example.com",
            "AIRTRAIL_API_KEY": "key123",
        }
        cfg = self._make_config(env)
        cfg.validate()  # Should not raise

    def test_validate_raises_when_imap_server_missing(self):
        env = {
            "EMAIL_ADDRESS": "user@example.com",
            "AIRTRAIL_API_URL": "http://api.example.com",
            "AIRTRAIL_API_KEY": "key123",
        }
        cfg = self._make_config(env)
        cfg.IMAP_SERVER = None
        with pytest.raises(ValueError, match="IMAP_SERVER"):
            cfg.validate()

    def test_validate_raises_when_email_address_missing(self):
        env = {
            "IMAP_SERVER": "imap.example.com",
            "AIRTRAIL_API_URL": "http://api.example.com",
            "AIRTRAIL_API_KEY": "key123",
        }
        cfg = self._make_config(env)
        cfg.EMAIL_ADDRESS = None
        with pytest.raises(ValueError, match="EMAIL_ADDRESS"):
            cfg.validate()

    def test_validate_raises_when_airtrail_api_url_missing(self):
        env = {
            "IMAP_SERVER": "imap.example.com",
            "EMAIL_ADDRESS": "user@example.com",
            "AIRTRAIL_API_KEY": "key123",
        }
        cfg = self._make_config(env)
        cfg.AIRTRAIL_API_URL = None
        with pytest.raises(ValueError, match="AIRTRAIL_API_URL"):
            cfg.validate()

    def test_validate_raises_when_airtrail_api_key_missing(self):
        env = {
            "IMAP_SERVER": "imap.example.com",
            "EMAIL_ADDRESS": "user@example.com",
            "AIRTRAIL_API_URL": "http://api.example.com",
        }
        cfg = self._make_config(env)
        cfg.AIRTRAIL_API_KEY = None
        with pytest.raises(ValueError, match="AIRTRAIL_API_KEY"):
            cfg.validate()

    def test_validate_error_message_lists_all_missing(self):
        env = {
            "IMAP_SERVER": "imap.example.com",
            "EMAIL_ADDRESS": "user@example.com",
        }
        cfg = self._make_config(env)
        cfg.AIRTRAIL_API_URL = None
        cfg.AIRTRAIL_API_KEY = None
        with pytest.raises(ValueError) as exc_info:
            cfg.validate()
        assert "AIRTRAIL_API_URL" in str(exc_info.value)
        assert "AIRTRAIL_API_KEY" in str(exc_info.value)
