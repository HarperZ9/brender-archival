from engine_revival.cli import main


def test_main_help_exits_zero(capsys):
    assert main(["--help"]) == 0
    assert "validate" in capsys.readouterr().out


def test_unknown_command_exits_nonzero(capsys):
    assert main(["not-a-command"]) == 2
    assert "invalid choice" in capsys.readouterr().err
