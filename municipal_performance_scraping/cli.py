import typer

from .loaders import load_governorates, load_municipalities, load_performance_criteria
from .models import reset_db

app = typer.Typer()
app_db = typer.Typer()
app_loader = typer.Typer()

app.add_typer(app_db, name="db")
app.add_typer(app_loader, name="load")


@app_db.command("reset")
def command_reset_db():
    typer.echo(typer.style("Restting database", fg=typer.colors.YELLOW))
    reset_db()


@app_loader.command("municipalities")
def command_load_municipalities():
    typer.echo(typer.style("Loading municipalities", fg=typer.colors.GREEN))
    load_municipalities()


@app_loader.command("governorates")
def command_load_governorates():
    typer.echo(typer.style("Loading governorates", fg=typer.colors.GREEN))
    load_governorates()


@app_loader.command("criteria")
def command_load_performance_criteria():
    typer.echo(typer.style("Loading criteria", fg=typer.colors.GREEN))
    load_performance_criteria()


@app_loader.command("all")
def command_load_all():
    command_reset_db()
    command_load_governorates()
    command_load_municipalities()
    command_load_performance_criteria()


# load_performance_criteria()
# load_evaluations()
