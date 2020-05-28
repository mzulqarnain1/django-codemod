import pytest
from click.testing import CliRunner

from django_codemod import cli


@pytest.fixture()
def cli_runner():
    return CliRunner()


def test_missing_argument(cli_runner):
    """Should explain missing arguments."""
    result = cli_runner.invoke(cli.djcodemod)

    assert result.exit_code == 2
    assert "Error: Missing argument 'PATH'" in result.output


@pytest.mark.parametrize(
    "command_line",
    [
        # Missing options
        ["."],
        # Too many options
        ["--removed-in", "3.0", "--deprecated-in", "2.0", "."],
    ],
)
def test_invalid_options(cli_runner, command_line):
    """Should explain missing option."""
    result = cli_runner.invoke(cli.djcodemod, command_line)

    assert result.exit_code == 2
    assert (
        "Error: You must specify either '--removed-in' or "
        "'--deprecated-in' but not both." in result.output
    )


def test_help(cli_runner):
    """The --help option should be available."""
    help_result = cli_runner.invoke(cli.djcodemod, ["--help"])

    assert help_result.exit_code == 0
    assert "--help" in help_result.output
    assert "Show this message and exit." in help_result.output


def test_missing_version_parts(cli_runner):
    result = cli_runner.invoke(cli.djcodemod, ["--removed-in", "3", "."])

    assert result.exit_code == 2
    assert "missing version parts." in result.output


@pytest.mark.parametrize(
    ("option", "version"),
    [
        # Removed in option
        ("--removed-in", "1.0"),
        ("--removed-in", "11.0"),
        # Deprecated in option
        ("--deprecated-in", "1.0"),
        ("--deprecated-in", "3.4"),
    ],
)
def test_non_supported_version(cli_runner, option, version):
    result = cli_runner.invoke(cli.djcodemod, [option, version, "."])

    assert result.exit_code == 2
    assert f"'{version}' is not supported. Versions supported:" in result.output


def test_invalid_version(cli_runner):
    result = cli_runner.invoke(cli.djcodemod, ["--removed-in", "not.a.version", "."])

    assert result.exit_code == 2
    assert "'not.a.version' is not a valid version" in result.output


@pytest.mark.parametrize(
    ("option", "version"),
    [
        # Removed in option
        ("--removed-in", "3.0"),
        ("--deprecated-in", "2.0"),
    ],
)
def test_basic_arguments(mocker, cli_runner, option, version):
    call_command = mocker.patch("django_codemod.cli.call_command")

    result = cli_runner.invoke(cli.djcodemod, [option, version, "."])

    assert result.exit_code == 0
    call_command.assert_called_once()
