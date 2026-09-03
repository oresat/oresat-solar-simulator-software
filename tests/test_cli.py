from unittest.mock import MagicMock, patch

import pytest
from lib.cli import Cli


@patch("lib.cli.AutoMode")
def test_run_reprompts_with_updated_message_on_invalid_input(
    mock_auto_mode_class: MagicMock, capsys: pytest.CaptureFixture[str]
) -> None:
    # Arrange
    cli = Cli(MagicMock())

    # Act
    with patch("builtins.input", side_effect=["5", "1"]):
        cli.run()

    # Assert
    captured = capsys.readouterr()
    assert "Invalid input. Please enter 1, 2, 3, or 4." in captured.out
    mock_auto_mode_class.return_value.run.assert_called_once()


def test__input_with_default_returns_default_on_empty_input() -> None:
    # Arrange
    cli = Cli(MagicMock())

    # Act
    with patch("builtins.input", return_value=""):
        result = cli._input_with_default("Prompt: ", default_value="no")

    # Assert
    assert result == "no"


def test__input_with_default_validates_choices_without_value_type() -> None:
    # Arrange
    cli = Cli(MagicMock())

    # Act
    with patch("builtins.input", return_value="yes"):
        result = cli._input_with_default("Prompt: ", default_value="no", valid_values=["yes", "no"])

    # Assert
    assert result == "yes"


def test__input_with_default_converts_type_without_valid_values() -> None:
    # Arrange
    cli = Cli(MagicMock())

    # Act
    with patch("builtins.input", return_value="75"):
        result = cli._input_with_default("Prompt: ", default_value=100, value_type=int)

    # Assert
    assert result == 75
