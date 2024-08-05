import click
import managedvault

vault = managedvault.ManagedVault()

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
    click.echo(vault.status())

cli.add_command(status)


@click.command()
def test():
    "Show Application status"
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

cli.add_command(test)
        
@click.command()
def list():
    "List managed vaults"
    vault.list_vaults()
    
cli.add_command(list)

@click.command()
@click.argument("name")
@click.argument("url")
def addvault(name, url):
    "List managed vaults"
    vault.vault_add(name, url)

cli.add_command(addvault)

@click.command()
@click.argument("name")
def vaultstatus(name):
    "Show Status of Vault"
    click.echo(vault.vault_status(name))

cli.add_command(vaultstatus)

@click.command()
@click.argument("name")
def vaultinit(name):
    "Init named Vault"
    click.echo(vault.vault_init(name))

cli.add_command(vaultinit)

@click.command()
@click.argument("name")
def vaultunseal(name):
    "Unseal Named Vault"
    click.echo(vault.vault_unseal(name))

cli.add_command(vaultunseal)

@click.command()
def prune():
    "Prune credentials in DB and Vault"
    click.echo(vault.prune())

cli.add_command(prune)

@click.command()
@click.argument("name")
def removevault(name):
    "Remove a managed vault"
    vault.vault_remove(name)

cli.add_command(removevault)