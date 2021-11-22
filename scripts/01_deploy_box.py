from brownie import (
    Box,
    TransparentUpgradeableProxy,
    ProxyAdmin,
    config,
    network,
    Contract
)
from scripts.helpful_scripts import get_account, encode_function_data

def main():
    account = get_account()
    print(f"Deploying to {network.show_active()}")
    box = Box.deploy({"from": account})
    print(box.retrieve())

    # proxy admin
    proxy_admin = ProxyAdmin.deploy({"from": account})

    # initializer = box.store, 1
    box_encoded_initializer_function = encode_function_data() 
    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000}
    )
    print(f"Proxy deployed to: {proxy}. You can now upgrade to V2.")
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    proxy_box.store(1, {"from": account})
    print(proxy_box.retrieve())

    

