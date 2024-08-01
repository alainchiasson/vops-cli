import click
import managedvault as mv


@click.group()
@click.version_option()
def cli():
    "Vault Operations CLI"


@cli.command()
def show():
    "Show the configuration"
    click.echo(mv.config.vault_addr)
    click.echo(mv.config.vault_token)
    click.echo(mv.config.dblink)


@cli.command()
def status():
    "List managed vaults"
    vault = mv.ManagedVault()
    click.echo("Verifying Vault connection  ...  ", nl=False)
    if vault.secret_store_connected():
        click.echo("Authenticated")
    else:
        click.echo("Error!")
        
    click.echo("Verifying SQLite connection  ...  ", nl=False)
    if vault.data_store_connected():
        click.echo("Connected")
    else:
        click.echo("Error!")
        
    
