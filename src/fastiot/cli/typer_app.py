import typer

DEFAULT_CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

app = typer.Typer(
    context_settings=DEFAULT_CONTEXT_SETTINGS
)

create = typer.Typer(context_settings=DEFAULT_CONTEXT_SETTINGS)
# Use this command to create any subcommand of create, like `fastiot.cli create my-special-file`
