import argparse
import asyncio
import os

from oracle_voter.oracle.machine2 import Oracle
from oracle_voter.chain.core import LCDNode
from oracle_voter.wallet.cli import CLIWallet
from oracle_voter._version import __version__


async def start_coro(args):
    n = LCDNode(addr=args["node"])
    home_dir = args.get(
        "wallet_dir",
        None,
    ) or os.path.expanduser("~/.terracli")

    account_addr = CLIWallet.get_addr(args["wallet_name"], home_dir)

    w = CLIWallet(
        args["wallet_name"],
        args["wallet_password"],
        account_addr,
        lcd_node=n,
        home_dir=home_dir,
    )
    # Sync Wallet
    await w.sync_state()

    # Init the Start Machine
    oracle = Oracle(
        vote_period=args["vote_period"],
        lcd_node=n,
        validator_addr=args["validator"],
        wallet=w,
        chain_id=args["chain_id"],
        gas_fee=args["gas_fee"],
        gas_denom=args["gas_denom"],
    )
    while True:
        await oracle.retrieve_height()
        await asyncio.sleep(0.50)


def main():
    parser = argparse.ArgumentParser(description="Run Terra Oracle Voter")
    parser.add_argument(
        "validator",
        metavar="validator",
        help="validator operator address (valoper)",
    )
    parser.add_argument(
        "--wallet",
        metavar="wallet_name",
        help="Terra Feeder Wallet in terracli",
        default="feeder",
    )
    parser.add_argument(
        "--node",
        metavar="node",
        help="Terra LCD Node",
        default="http://127.0.0.1:1317",
    )
    parser.add_argument(
        "--chain-id",
        metavar="chain_id",
        help="Tendermint Chain ID",
    )
    parser.add_argument(
        "--vote-period",
        metavar="vote_period",
        help="Terra Chain vote period length",
        default=5,
    )
    parser.add_argument(
        "--password",
        metavar="password",
        help="Password to unlock feeder account",
        default=None,
    )
    parser.add_argument(
        "--home",
        metavar="home_dir",
        help="Home Directory to pass to terracli",
        default=None,
    )
    parser.add_argument(
        "--gas-fee",
        metavar="gas_fee",
        help="Transaction fee amount to pay in gas denoms",
        default="1000"
    )
    parser.add_argument(
        "--gas-denom",
        metavar="gas_denom",
        help="Base denomination for gas transaction fee amount",
        default="uluna"
    )
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=f"{__version__}",
    )
    args = parser.parse_args()
    # Check that password is given
    wallet_pass = os.environ.get("password", None) or args.password
    if wallet_pass is None:
        raise ValueError(f"Password not provided for feeder account")

    pargs = {
        "node": args.node,
        "validator": args.validator,
        "wallet_name": args.wallet,
        "wallet_password": args.password,
        "chain_id": args.chain_id,
        "wallet_dir": args.home,
        "vote_period": args.vote_period,
        "gas_denom": args.gas_denom,
        "gas_fee": args.gas_fee,
    }

    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_coro(pargs))


if __name__ == '__main__':
    main()
