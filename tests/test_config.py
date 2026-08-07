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
            assert cfg_module.Config.EMAIL_SENDERS == [""]

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
