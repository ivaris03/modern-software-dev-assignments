import os
from unittest.mock import MagicMock, patch

from ..app.services.extract import extract_action_items, extract_action_items_llm


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


class TestExtractActionItemsLLM:
    """Tests for extract_action_items_llm with mocked LLM responses."""

    @patch("week2.app.services.extract.chat")
    def test_bullet_list_input(self, mock_chat):
        """Test LLM extraction with bullet list format."""
        mock_response = MagicMock()
        mock_response.message.content = (
            '["Set up database", "implement API endpoint", "Write tests"]'
        )
        mock_chat.return_value = mock_response

        text = """
        Notes from meeting:
        - Set up database
        * implement API endpoint
        1. Write tests
        """
        items = extract_action_items_llm(text)

        assert items == ["Set up database", "implement API endpoint", "Write tests"]
        mock_chat.assert_called_once()

    @patch("week2.app.services.extract.chat")
    def test_keyword_prefixed_lines(self, mock_chat):
        """Test LLM extraction with keyword-prefixed lines."""
        mock_response = MagicMock()
        mock_response.message.content = (
            '["TODO: Fix login bug", "ACTION: Update docs", "NEXT: Deploy to prod"]'
        )
        mock_chat.return_value = mock_response

        text = """
        TODO: Fix login bug
        ACTION: Update docs
        NEXT: Deploy to prod
        """
        items = extract_action_items_llm(text)

        assert items == ["TODO: Fix login bug", "ACTION: Update docs", "NEXT: Deploy to prod"]

    @patch("week2.app.services.extract.chat")
    def test_empty_input(self, mock_chat):
        """Test LLM extraction with empty input returns empty list."""
        mock_response = MagicMock()
        mock_response.message.content = "[]"
        mock_chat.return_value = mock_response

        items = extract_action_items_llm("")

        assert items == []
        mock_chat.assert_called_once()

    @patch("week2.app.services.extract.chat")
    def test_invalid_json_response(self, mock_chat):
        """Test that invalid JSON from LLM returns empty list."""
        mock_response = MagicMock()
        mock_response.message.content = "Sorry, I couldn't extract any items."
        mock_chat.return_value = mock_response

        items = extract_action_items_llm("Some text without clear action items")

        assert items == []

    @patch("week2.app.services.extract.chat")
    def test_llm_model_config(self, mock_chat):
        """Test that correct model is used when OLLAMA_MODEL is set."""
        mock_response = MagicMock()
        mock_response.message.content = '["Test item"]'
        mock_chat.return_value = mock_response

        with patch.dict(os.environ, {"OLLAMA_MODEL": "mistral-nemo:12b"}):
            extract_action_items_llm("Test input")

        call_kwargs = mock_chat.call_args
        assert call_kwargs.kwargs["model"] == "mistral-nemo:12b"
        assert call_kwargs.kwargs["options"]["temperature"] == 0
