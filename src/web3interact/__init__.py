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

if config("WEB3_POA", default=False, cast=bool):
    print("Injecting geth_poa_middleware...")
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.eth.default_account = w3.eth.accounts[config("WEB3_KEY_INDEX", cast=int, default=0)]

acct = w3.eth.default_account
eth = w3.eth


def _load_abi(contract_name):
    try:
        with open(f"{contract_dir}/{contract_name}.json") as f:
            compile_metadata = json.load(f)
        for contract_id, metadata in compile_metadata.items():
            section_name = contract_id.split(":")[-1]
            if section_name == contract_name:
                return metadata["abi"]
    except FileNotFoundError:
        pass
    else:
        raise KeyError(
            f"contract name {contract_name} not found in {contract_dir}/{contract_name}.json"
        )
    with open(f"{contract_dir}/{contract_name}.abi") as f:
        contract_abi = json.load(f)
        return contract_abi


def get_contract(contract_name):
    with open(f"{build_dir}/address.json") as f:
        contract_addr = json.load(f)[contract_name]

    contract_abi = _load_abi(contract_name)
    return w3.eth.contract(address=contract_addr, abi=contract_abi)


def main():
    parser = argparse.ArgumentParser(description="deploy solidity contracts through json-rpc")
    parser.add_argument("--names", "-n", nargs="*", help="names of contracts (case-sensitive)")
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
    if args.names:
        names = args.names
    else:
        try:
            with open(f"{build_dir}/address.json") as f:
                address_dct = json.load(f)
                names = list(address_dct)
        except FileNotFoundError:
            print("build/web3deploy/address.json not found, no contracts loaded")
            names = []

    for name in names:
        abbrev = "".join([char for char in name if char.isupper()]).lower()
        exec(f"{abbrev}_c = get_contract('{name}')")
        exec(f"{abbrev} = {abbrev}_c.functions")

    # start interactive shell
    c = get_config()
    c.InteractiveShellEmbed.colors = "Linux"
    embed(config=c)
