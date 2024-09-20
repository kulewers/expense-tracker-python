import click
import crud

@click.group()
@click.version_option()
def cli():
  pass

cli.add_command(crud.create)
cli.add_command(crud.read)
cli.add_command(crud.update)
cli.add_command(crud.delete)