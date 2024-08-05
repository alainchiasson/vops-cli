import click
import managedvault

vaults = managedvault.ManagedVault()

@click.group()
@click.version_option()
def cli():
    "Vault Operations CLI"


@click.command()
def show():
    "Show the configuration"
    conf = vaults.show()
    
    click.echo(conf.vault_addr)
    click.echo(conf.vault_token)
    click.echo(conf.dblink)

cli.add_command(show)

@click.command()
def appstatus():
    "Show Application status"
    click.echo(vaults.status())

cli.add_command(appstatus)


@click.command()
def test():
    "Show Application status"
    click.echo("Verifying Vault connection  ...  ", nl=False)
    if vaults.secret_store_connected():
        click.echo("Authenticated")
    else:
        click.echo("Error!")
        
    click.echo("Verifying SQLite connection  ...  ", nl=False)
    if vaults.data_store_connected():
        click.echo("Connected")
    else:
        click.echo("Error!")
        
    click.echo("verifying data structure ... ", nl=False)
    if vaults.verify_and_init():
        click.echo("Data correct")
    else:
        click.echo("Error")

cli.add_command(test)
        
@click.command()
def list():
    "List managed vaults"
    click.echo(f"{'Name':20} URL")
    for vault in vaults.list():
        ( name, url ) = vault
        click.echo(f"{name:20} {url}")
    
cli.add_command(list)

@click.command()
@click.argument("name")
@click.argument("url")
def add(name, url):
    "List managed vaults"
    vaults.vault_add(name, url)

cli.add_command(add)

@click.command()
@click.argument("name")
def status(name):
    "Show Status of Vault"
    click.echo(vaults.vault_status(name))

cli.add_command(status)

@click.command()
@click.argument("name")
def init(name):
    "Init named Vault"
    click.echo(vaults.vault_init(name))

cli.add_command(init)

@click.command()
@click.argument("name")
def unseal(name):
    "Unseal Named Vault"
    click.echo(vaults.vault_unseal(name))

cli.add_command(unseal)

@click.command()
def prune():
    "Prune credentials in DB and Vault"
    click.echo(vaults.prune())

cli.add_command(prune)

@click.command()
@click.argument("name")
def remove(name):
    "Remove a managed vault"
    click.echo(vaults.vault_remove(name))

cli.add_command(remove)

@click.command()
@click.argument("name")
def genroot(name):
    "Remove a managed vault"
    click.echo(vaults.genroot(name))

cli.add_command(genroot)