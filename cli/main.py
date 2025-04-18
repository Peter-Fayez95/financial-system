import click
from services.account_service import AccountService
from services.transaction_service import TransactionService
from services.currency_exchange_service import CurrencyExchangeService
from services.reconstruction_service import ReconstructionService
from database.connection import DatabaseConnection
from database.connection_parameters import *
from decimal import Decimal
from .validation import *


cfg = get_database_parameters("database/database.ini")
db_conn = DatabaseConnection(cfg['postgresql']).get_connection()
account_service = AccountService(db_conn)
transaction_service = TransactionService(db_conn)
currency_service = CurrencyExchangeService(db_conn)
reconstruction_service = ReconstructionService(db_conn)


@click.group(help="""
Multi-Currency Financial Ledger CLI Tool

Examples:
  cli.py create-account --initial-balance "USD=100,EUR=50"
  cli.py deposit --account-id acc123 --currency GBP --amount 200
  cli.py withdraw --account-id acc123 --currency EUR --amount 25
  cli.py transfer --from-account acc1 --to-account acc2 --from-currency USD --amount 100
  cli.py convert-currency --account-id acc1 --from-currency EUR --amount 10 --to-currency GBP
  cli.py update_rate --from-currency USD --to-currency EUR --rate 1.10
  cli.py get-balance --account-id acc123
  cli.py get-balance --account-id acc123 --timestamp "2023-10-27 10:00:00"
""")
def cli():
    pass

@cli.command(help="Create a new account with optional ID and initial balances.")
@click.option("--initial-balance", callback=parse_currency_list,
              help="Comma-separated list of CUR=AMT (e.g. USD=100,EUR=50).")
def create_account(initial_balance):
    click.echo(f"[CREATE ACCOUNT], Balances: {initial_balance}")
    account_id = account_service.create_account(initial_balance)
    click.echo(f"Created account with ID: {account_id}.")


@cli.command(help="Deposit currencies into an account.")
@click.option("--account-id", required=True, type=click.INT, help="Account ID to deposit into.")
@click.option("--currency", required=True, type=click.Choice(['USD', 'EUR', 'GBP'], case_sensitive=False), help="Currency")
@click.option("--amount", required=True, type=click.FLOAT, help="Amount to be deposited")
def deposit(account_id, currency, amount):
    click.echo(f"[DEPOSIT] Account: {account_id}, Currency: {currency}, Amount: {amount}")
    transaction_id = transaction_service.deposit(account_id, currency, Decimal(amount))
    if transaction_id < 0:
        click.echo("Invalid Account ID.")
    else:
        click.echo(f"Deposited money into Account: {account_id}, Currency: {currency}, Amount: {amount}")

@cli.command(help="Withdraw currencies from an account.")
@click.option("--account-id", required=True, type=click.INT, help="Account ID to withdraw from.")
@click.option("--currency", required=True, type=click.Choice(['USD', 'EUR', 'GBP'], case_sensitive=False), help="Currency")
@click.option("--amount", required=True, type=click.FLOAT, help="Amount to be withdrawn.", callback=validate_amount)
def withdraw(account_id, currency, amount):
    click.echo(f"[WITHDRAW] Account: {account_id}, Currency: {currency}")
    transaction_id = transaction_service.withdraw(account_id, currency, Decimal(amount))
    message = f"Withdrawn money from Account: {account_id}, Currency: {currency}, Amount: {amount}"
  
    if transaction_id == -1:
        message = "Invalid account ID"
    elif transaction_id == -2:
        message = f"Insufficient balance in {currency}"

    click.echo(message)

@cli.command(help="Transfer money between accounts (same or different currencies).")
@click.option("--from-account", required=True, type=click.INT, help="Sender's account ID.")
@click.option("--to-account", required=True, type=click.INT, help="Receiver's account ID.")
@click.option("--from-currency", required=True, type=click.Choice(['USD', 'EUR', 'GBP'], case_sensitive=False), help="Currency to transfer from.")
@click.option("--amount", required=True, type=click.FLOAT, help="Amount to transfer.")
@click.option("--to-currency", required=False, type=click.Choice(['USD', 'EUR', 'GBP'], case_sensitive=False),
              help="Target currency (for conversion). Omit for same-currency transfer.")
def transfer(from_account, to_account, from_currency, amount, to_currency):
    click.echo(f"[TRANSFER] {amount:.2f} {from_currency} from {from_account} to {to_account}" +
               (f" as {to_currency}" if to_currency else ""))
    transaction_id = transaction_service.transfer(from_account, to_account, from_currency, to_currency, Decimal(amount))
    
    message = f"Transferred money from Account: {from_account}, To Account: {to_account}"
    if transaction_id == -1:
        message = "Invalid Sender Account ID."
    elif transaction_id == -2:
        message = "Invalid Reciever Account ID."
    elif transaction_id == -3:
        message = f"Insufficient balance in {from_currency}"
    
    click.echo(message)

    if transaction_id >= 0:
        if to_currency != from_currency and to_currency is not None:
            click.echo(f"Converted Amount: {amount} in {from_currency} To {to_currency}")
        else:
            click.echo(f"Currency: {from_currency}, Amount: {amount}")
    

@cli.command(help="Convert currency within a single account.")
@click.option("--account-id", required=True, type=click.INT, help="Account ID.")
@click.option("--from-currency", required=True, type=click.Choice(['USD', 'EUR', 'GBP'], case_sensitive=False), help="Currency to convert from.")
@click.option("--amount", required=True, type=click.FLOAT, help="Amount to convert.", callback=validate_amount)
@click.option("--to-currency", required=True, type=click.Choice(['USD', 'EUR', 'GBP'], case_sensitive=False),
              help="Currency to convert to.")
def convert_currency(account_id, from_currency, amount, to_currency):
    click.echo(f"[CONVERT CURRENCY] Account: {account_id}, {amount:.2f} {from_currency} to {to_currency or '[DEFAULT]'}")
    transaction_id = transaction_service.convert_currency(account_id, from_currency, to_currency, Decimal(amount))

    message = f"Converted {amount} in {from_currency} to {to_currency}"

    if transaction_id == -1:
        message = "Invalid account ID"
    elif transaction_id == -2:
        message = f"Insufficient balance in {from_currency}"

    click.echo(message)


@cli.command(help="Update currency conversion rate.")
@click.option("--from-currency", required=True, type=click.Choice(['USD', 'EUR', 'GBP'], case_sensitive=False), help="Source currency.")
@click.option("--to-currency", required=True, type=click.Choice(['USD', 'EUR', 'GBP'], case_sensitive=False), help="Target currency.")
@click.option("--rate", required=True, type=click.FLOAT, help="Exchange rate (e.g. 1.23).", callback=validate_rate)
def update_rate(from_currency, to_currency, rate):
    click.echo(f"[UPDATE RATE] {from_currency} → {to_currency} = {rate:.2f}")
    currency_service.update_exchange_rate(from_currency, to_currency, rate)
    click.echo(f"Exchange rate updated between {from_currency} and {to_currency}")


@cli.command(help="Get Account balance, optionally at a specific timestamp.")
@click.option("--account-id", required=True, type=click.INT, help="Account ID")
@click.option("--timestamp", type=click.DateTime(), required=False,
              help="Get balance at a specific point in time (e.g., 'YYYY-MM-DD HH:MM:SS').")
def get_balance(account_id, timestamp):
    if timestamp:
        click.echo(f"[ACCOUNT BALANCE @ {timestamp}] ID: {account_id}")
        # Use reconstruction service
        snapshot = reconstruction_service.reconstruct_state(account_id, timestamp)
        if snapshot:
            usd_balance = snapshot.usd_balance
            eur_balance = snapshot.eur_balance
            gbp_balance = snapshot.gbp_balance
            # Check if the account existed at that time (balances might be 0)
            # Assuming reconstruction returns None or raises error for non-existent accounts at that time
            # or returns a snapshot with potentially zero balances if created later.
            # We'll rely on the snapshot object being valid if returned.
            message = f"ID: {account_id} @ {timestamp} | Balance: {usd_balance} USD, {eur_balance} EUR, {gbp_balance} GBP"
        else:
            # Handle cases where reconstruction failed (e.g., account didn't exist yet, no snapshots found)
            message = f"Could not reconstruct balance for Account ID: {account_id} at {timestamp}. Account might not have existed or no history available."
            # Set a sentinel value to indicate failure like the original logic, if needed downstream
            usd_balance = -1 
    else:
        click.echo(f"[CURRENT ACCOUNT BALANCE] ID: {account_id}")
        # Use account service for current balance (existing logic)
        usd_balance, eur_balance, gbp_balance = account_service.get_balance(account_id)
        if usd_balance < 0: # Existing check for invalid account ID
             message = "Invalid account ID"
        else:
             message = f"ID: {account_id} | Balance: {usd_balance} USD, {eur_balance} EUR, {gbp_balance} GBP"

    click.echo(message)

if __name__ == "__main__":
    cli()
