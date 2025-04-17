import click
from services.account_service import AccountService
from services.transaction_service import TransactionService
from services.currency_exchange_service import CurrencyExchangeService
from database.connection import DatabaseConnection
from database.connection_parameters import get_database_parameters
from collections import defaultdict
from decimal import Decimal

VALID_CURRENCIES = {"USD", "EUR", "GBP"}

cfg = get_database_parameters("database/database.ini")
db_conn = DatabaseConnection(cfg['postgresql']).get_connection()
account_service = AccountService(db_conn)
transaction_service = TransactionService(db_conn)
currency_service = CurrencyExchangeService(db_conn)

def parse_currency_list(ctx, param, value):
    """Parses comma-separated CUR=AMT entries into a dict with currency validation."""
    if not value:
        return defaultdict(Decimal)
    currencies = defaultdict(Decimal)
    for pair in value.split(","):
        if "=" not in pair:
            raise click.BadParameter(f"Invalid format: '{pair}', expected CUR=AMT")
        cur, amt = pair.strip().split("=")
        cur = cur.upper()
        if cur not in VALID_CURRENCIES:
            raise click.BadParameter(f"Invalid currency '{cur}'. Must be one of {', '.join(VALID_CURRENCIES)}")
        try:
            currencies[cur] = Decimal(amt)
        except ValueError:
            raise click.BadParameter(f"Invalid amount for {cur}: {amt}")
    return currencies

def validate_currency(ctx, param, value):
    if value and value.upper() not in VALID_CURRENCIES:
        raise click.BadParameter(f"Currency must be one of: {', '.join(VALID_CURRENCIES)}")
    return value.upper() if value else None

@click.group(help="""
Multi-Currency Financial Ledger CLI Tool

Examples:
  cli.py create_account --initial-balance "USD=100,EUR=50"
  cli.py deposit --account-id acc123 --currencies "GBP=200"
  cli.py withdraw --account-id acc123 --currencies "EUR=25"
  cli.py transfer --from-account acc1 --to-account acc2 --from-currency USD --amount 100
  cli.py convert_currency --account-id acc1 --from-currency EUR --amount 10 --to-currency GBP
  cli.py update_rate --from-currency USD --to-currency EUR --rate 1.10
""")
def cli():
    pass

@cli.command(help="Create a new account with optional ID and initial balances.")
@click.option("--initial-balance", callback=parse_currency_list,
              help="Comma-separated list of CUR=AMT (e.g. USD=100,EUR=50).")
def create_account(initial_balance):
    click.echo(f"[CREATE ACCOUNT], Balances: {initial_balance}")
    # print(**initial_balance)
    account_id = account_service.create_account(initial_balance)
    click.echo(f"Created account with ID: {account_id}.")


@cli.command(help="Deposit currencies into an account.")
@click.option("--account-id", required=True, help="Account ID to deposit into.")
@click.option("--currency", required=True, help="Currency", callback=validate_currency)
@click.option("--amount", required=True, help="Amount to be deposited")
def deposit(account_id, currency, amount):
    click.echo(f"[DEPOSIT] Account: {account_id}, Currency: {currency}, Amount: {amount}")
    transaction_id = transaction_service.deposit(account_id, currency, Decimal(amount))
    if transaction_id < 0:
        click.echo("Invalid Account ID.")
    else:
        click.echo(f"Deposited money into Account: {account_id}, Currency: {currency}, Amount: {amount}")

@cli.command(help="Withdraw currencies from an account.")
@click.option("--account-id", required=True, help="Account ID to withdraw from.")
@click.option("--currency", required=True, help="Currency", callback=validate_currency)
@click.option("--amount", required=True, help="Amount to be withdrawn.")
def withdraw(account_id, currency, amount):
    click.echo(f"[WITHDRAW] Account: {account_id}, Currency: {currency}")
    transaction_id = transaction_service.withdraw(account_id, currency, Decimal(amount))
    message = f"Withdrawn money from Account: {account_id}, Currency: {currency}, Amount: {amount}"
  
    if transaction_id == -1:
        message = "Withdraw amount can only hold a positive value."
    elif transaction_id == -2:
        message = "Invalid account ID"
    elif transaction_id == -3:
        message = f"Insufficient balance in {currency}"

    click.echo(message)

@cli.command(help="Transfer money between accounts (same or different currencies).")
@click.option("--from-account", required=True, help="Sender's account ID.")
@click.option("--to-account", required=True, help="Receiver's account ID.")
@click.option("--from-currency", required=True, callback=validate_currency, help="Currency to transfer from.")
@click.option("--amount", required=True, type=float, help="Amount to transfer.")
@click.option("--to-currency", required=False, callback=validate_currency,
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
    elif transaction_id == -4:
        message = f"Transfer amount can only hold a positive value."
    
    click.echo(message)

    if transaction_id >= 0:
        if to_currency != from_currency and to_currency is not None:
            click.echo(f"Converted Amount: {amount} in {from_currency} To {to_currency}")
        else:
            click.echo(f"Currency: {from_currency}, Amount: {amount}")
    

@cli.command(help="Convert currency within a single account.")
@click.option("--account-id", required=True, help="Account ID.")
@click.option("--from-currency", required=True, callback=validate_currency, help="Currency to convert from.")
@click.option("--amount", required=True, type=float, help="Amount to convert.")
@click.option("--to-currency", required=True, callback=validate_currency,
              help="Currency to convert to (optional).")
def convert_currency(account_id, from_currency, amount, to_currency):
    click.echo(f"[CONVERT CURRENCY] Account: {account_id}, {amount:.2f} {from_currency} to {to_currency or '[DEFAULT]'}")
    transaction_id = transaction_service.convert_currency(account_id, from_currency, to_currency, Decimal(amount))
    click.echo(f"Converted {amount} in {from_currency} to {to_currency}")


@cli.command(help="Update currency conversion rate.")
@click.option("--from-currency", required=True, callback=validate_currency, help="Source currency.")
@click.option("--to-currency", required=True, callback=validate_currency, help="Target currency.")
@click.option("--rate", required=True, type=float, help="Exchange rate (e.g. 1.23).")
def update_rate(from_currency, to_currency, rate):
    click.echo(f"[UPDATE RATE] {from_currency} → {to_currency} = {rate:.2f}")
    currency_service.update_exchange_rate(from_currency, to_currency, Decimal(rate))
    click.echo(f"Exchange rate updated between {from_currency} and {to_currency}")

if __name__ == "__main__":
    cli()
