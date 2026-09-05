from unittest.mock import MagicMock, patch

import pytest

from solar_simulator.lib.cli import Cli


@patch("solar_simulator.lib.cli.AutoMode")
def test_run_reprompts_on_invalid_input(
    mock_auto_mode_class: MagicMock, capsys: pytest.CaptureFixture[str]
) -> None:
    # Arrange
    cli = Cli(MagicMock())

    # Act
    with patch("builtins.input", side_effect=["5", "1"]):
        cli.run()

    # Assert
    assert "Invalid input. Please enter 1, 2, 3, or 4." in capsys.readouterr().out
    mock_auto_mode_class.return_value.run.assert_called_once()


def test__input_with_default_returns_default_on_empty_input() -> None:
    # Act
    with patch("builtins.input", return_value=""):
        result = Cli._input_with_default("Prompt: ", default_value="no")

    # Assert
    assert result == "no"


def test__input_with_default_validates_choices() -> None:
    # Act
    with patch("builtins.input", side_effect=["maybe", "yes"]):
        result = Cli._input_with_default("Prompt: ", default_value="no", valid_values=("yes", "no"))

    # Assert
    assert result == "yes"


def test__input_with_default_reprompts_until_the_type_converts() -> None:
    # Act
    with patch("builtins.input", side_effect=["hot", "75"]):
        result = Cli._input_with_default("Prompt: ", default_value=100, value_type=int)

    # Assert
    assert result == 75
