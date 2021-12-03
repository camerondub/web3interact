import argparse
import json
import sys

from decouple import config
from IPython import embed
from traitlets.config import get_config
from web3 import Web3
from web3.middleware import geth_poa_middleware

build_dir = config("WEB3_BUILD_DIR", default="build/web3deploy")
contract_dir = f"{build_dir}/contract"

w3 = Web3(Web3.HTTPProvider(config("WEB3_HTTP_PROVIDER", default="http://localhost:8545")))

if config("WEB3_POA", default=False):
    print("Injecting geth_poa_middleware...")
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.eth.default_account = w3.eth.accounts[config("WEB3_KEY_INDEX", cast=int, default=0)]

acct = w3.eth.default_account
eth = w3.eth


def _load_abi(contract_name):
    with open(f"{contract_dir}/{contract_name}.json") as f:
        compile_metadata = json.load(f)
    for contract_id, metadata in compile_metadata.items():
        section_name = contract_id.split(":")[-1]
        if section_name == contract_name:
            return metadata
    raise KeyError(
        f"contract name {contract_name} not found in {contract_dir}/{contract_name}.json"
    )


def get_contract(contract_name):
    with open(f"{build_dir}/address.json") as f:
        contract_addr = json.load(f)[contract_name]

    contract_metadata = _load_abi(contract_name)
    return w3.eth.contract(address=contract_addr, abi=contract_metadata["abi"])


def main():
    parser = argparse.ArgumentParser(description="deploy solidity contracts through json-rpc")
    parser.add_argument(
        "--names", "-n", nargs="*", required=True, help="names of contracts (case-sensitive)"
    )
    parser.add_argument("--envdesc", "-d", action="store_true")
    args = parser.parse_args()

    if args.envdesc:
        print(
            "WEB3_BUILD_DIR: where to find contract build artifacts (./build/web3deploy)\n"
            "WEB3_HTTP_PROVIDER: url for eth client json-rpc interface (http://localhost:8545)\n"
            "WEB3_POA: enable proof-of-authority metadata (True)\n"
            "WEB3_KEY_INDEX: account index to use from provider (0)\n"
        )
        sys.exit(0)

    # fetch named contract objects from cmdline
    for name in args.names:
        exec(f"{name}Contract = get_contract('{name}')")
        exec(f"{name} = {name}Contract.caller")

    # start interactive shell
    c = get_config()
    c.InteractiveShellEmbed.colors = "Linux"
    embed(config=c)
