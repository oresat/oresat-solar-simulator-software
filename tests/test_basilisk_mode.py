from unittest.mock import MagicMock

from lib.modes.basilisk_mode import BasiliskMode


def test_handle_line_skips_blank_line_without_stopping_loop() -> None:
    # Arrange
    mode = BasiliskMode(MagicMock())

    # Act
    result = mode.handle_line("")

    # Assert
    assert result is True


def test_handle_line_skips_whitespace_only_line_without_stopping_loop() -> None:
    # Arrange
    mode = BasiliskMode(MagicMock())

    # Act
    result = mode.handle_line("   \n")

    # Assert
    assert result is True
