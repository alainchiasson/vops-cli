import click
import managedvault as mv


@click.group()
@click.version_option()
def cli():
    "Vault Operations CLI"


@click.command()
def show():
    "Show the configuration"
    click.echo(mv.config.vault_addr)
    click.echo(mv.config.vault_token)
    click.echo(mv.config.dblink)

cli.add_command(show)

@click.command()
def status():
    "Show Application status"
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
        
    click.echo("verifying data structure ... ", nl=False)
    if vault.verify_and_init():
        click.echo("Data correct")
    else:
        click.echo("Error")

cli.add_command(status)
        
@click.command()
def list():
    "List managed vaults"
    vault = mv.ManagedVault()

    vault.list_vaults()
    
cli.add_command(list)

@click.command()
@click.argument("name")
@click.argument("url")
def addvault(name, url):
    "List managed vaults"
    vault = mv.ManagedVault()

    vault.vault_add(name, url)

cli.add_command(addvault)

@click.command()
@click.argument("name")
def vaultstatus(name):
    "Show Status of Vault"
    vault = mv.ManagedVault()

    click.echo(vault.vault_status(name))

cli.add_command(vaultstatus)

@click.command()
@click.argument("name")
def vaultinit(name):
    "Show Status of Vault"
    vault = mv.ManagedVault()

    click.echo(vault.vault_init(name))

cli.add_command(vaultinit)