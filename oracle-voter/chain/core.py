from decimal import Decimal
from common import client

EIGHTEEN_PLACES = Decimal(10) ** -18


class Transaction:

    def __init__(
        self,
        chain_id,
        account_number,
        sequence,
        memo="",
    ):
        self.chain_id = chain_id
        self.account_number = account_number
        self.sequence = sequence
        self.memo = memo
        self.fee = {
            "amount": list(),
            "gas": "200000",
        }
        self.msgs = list()
        self.signatures = None

    def append_prevotemsg(
        self,
        hashed="",
        denom="",
        feeder="",
        validator="",
    ):
        # Currency Rate is 18 Decimals
        msg = {
            "type": "oracle/MsgExchangeRatePrevote",
            "value": {
                "hash": hashed,
                "denom": denom,
                "feeder": feeder,
                "validator": validator,
            },
        }
        self.msgs.append(msg)

    def append_votemsg(
        self,
        exchange_rate="",
        denom="",
        feeder="",
        validator="",
        salt=None,
    ):
        # Currency Rate is 18 Decimals
        rate = "-1.000000000000000000"
        if isinstance(exchange_rate, Decimal):
            rate = str(exchange_rate.quantize(EIGHTEEN_PLACES))

        msg_salt = None

        if salt is not None:
            msg_salt = salt

        msg = {
            "type": "oracle/MsgExchangeRateVote",
            "value": {
                "exchange_rate": rate,
                "salt": msg_salt,
                "denom": denom,
                "feeder": feeder,
                "validator": validator,
            },
        }
        self.msgs.append(msg)

    def build_incomplete(self):
        incomplete_tx = {
            "chain_id": self.chain_id,
            "account_number": str(self.account_number),
            "sequence": str(self.sequence),
            "fee": self.fee,
            "msgs": self.msgs,
            "memo": self.memo,
        }
        if self.signatures is not None:
            incomplete_tx["signatures"] = self.signatures
        return incomplete_tx

    def build(self):
        tx = {
            "type": "core/StdTx",
            "value": {
                "msg": self.msgs,
                "fee": self.fee,
                "memo": self.memo,
                "signatures": list(),
            }
        }
        return tx

    def sign(
        self,
        wallet,  # Wallet Name in the cli
    ):
        payload = self.build()
        result = wallet.offline_sign(
            payload,
            self.chain_id,
            self.account_number,
            self.sequence,
        )
        return result


class FullNode:

    def __init__(
        self,
        addr="http://127.0.0.1:26657",
    ):
        self.addr = addr

    async def broadcast_tx_async(self, tx):
        target_url = f"{self.addr}/txs"
        params = {}
        post_data = tx
        http_res = await client.http_post(
            target_url,
            params=params,
            post_data=post_data,
        )
        return http_res


class LCDNode:

    def __init__(
        self,
        addr="http://127.0.0.1:1317",
    ):
        self.addr = addr

    async def get_latest_block(self):
        target_url = f"{self.addr}/blocks/latest"
        params = dict()
        http_res = await client.http_get(target_url, params=params)
        return http_res

    async def get_account(self, account):
        target_url = f"{self.addr}/auth/accounts/{account}"
        params = dict()
        http_res = await client.http_get(target_url, params=params)
        return http_res

    async def get_oracle_rates(self):
        target_url = f"{self.addr}/oracle/denoms/exchange_rates"
        params = dict()
        http_res = await client.http_get(target_url, params=params)
        return http_res

    async def get_oracle_prevotes_validator(
        self,
        denom="",
        validator_addr="",
    ):
        target_url = f"{self.addr}/oracle/denoms/{denom}/prevotes/{validator_addr}"
        params = dict()
        http_res = await client.http_get(target_url, params=params)
        return http_res

    async def get_oracle_votes_validator(
        self,
        denom="",
        validator_addr="",
    ):
        target_url = f"{self.addr}/oracle/denoms/{denom}/votes/{validator_addr}"
        params = dict()
        http_res = await client.http_get(target_url, params=params)
        return http_res