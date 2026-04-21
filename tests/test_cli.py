from click.testing import CliRunner

from kalmancve.cli import main


class TestCli:
    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "version" in result.output.lower()

    def test_missing_data_file(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--data-file", "/nonexistent/nvd.jsonl"])
        assert result.exit_code != 0

    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Forecast CVE counts" in result.output
