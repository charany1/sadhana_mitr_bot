"""Tests for Sadhana Mitra bot logic."""

import pytest
from unittest.mock import patch, MagicMock

from app.bot import is_greeting, detect_language, MENU_TEXT_EN, MENU_TEXT_HI, MENU_MAP
from app.escalation import (
    detect_escalation_category,
    get_escalation_email,
    build_escalation_message,
)


class TestGreetingDetection:
    def test_english_greetings(self):
        assert is_greeting("Hi") is True
        assert is_greeting("Hello") is True
        assert is_greeting("Hey") is True
        assert is_greeting("Good morning") is True

    def test_hindi_greetings(self):
        assert is_greeting("Namaste") is True
        assert is_greeting("Namaskar") is True
        assert is_greeting("Pranam") is True

    def test_non_greetings(self):
        assert is_greeting("What are the yoga classes?") is False
        assert is_greeting("Tell me about retreats") is False

    def test_long_messages_not_greeting(self):
        assert is_greeting("Hi I want to know about yoga classes") is False


class TestEscalation:
    def test_detect_seva(self):
        assert detect_escalation_category("I want to volunteer") == "seva"

    def test_detect_programmes(self):
        assert detect_escalation_category("What is the registration fee?") == "programmes"

    def test_detect_sensitive(self):
        assert detect_escalation_category("I need spiritual guidance") == "sensitive"

    def test_no_escalation(self):
        assert detect_escalation_category("Tell me about Saadho") is None

    def test_email_routing(self):
        assert get_escalation_email("programmes") == "programs@saadho.org"
        assert get_escalation_email("seva") == "seva@saadho.org"
        assert get_escalation_email("sensitive") == "connect@saadho.org"

    def test_escalation_message_english(self):
        msg = build_escalation_message("seva", "en")
        assert "seva@saadho.org" in msg

    def test_escalation_message_hindi(self):
        msg = build_escalation_message("seva", "hi")
        assert "seva@saadho.org" in msg


class TestMenuMap:
    def test_all_menu_numbers_exist(self):
        for i in range(1, 8):
            assert str(i) in MENU_MAP

    def test_menu_text_has_all_options(self):
        for i in range(1, 8):
            assert f"{i}️⃣" in MENU_TEXT_EN
            assert f"{i}️⃣" in MENU_TEXT_HI
