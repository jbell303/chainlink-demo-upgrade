from brownie import (
    Box,
    BoxV2,
    TransparentUpgradeableProxy,
    ProxyAdmin,
    config,
    network,
    Contract
)
from scripts.helpful_scripts import get_account, encode_function_data, upgrade

def main():
    # 1. Deploy V1 contract
    account = get_account()
    print(f"Deploying to {network.show_active()}")
    box = Box.deploy(
        {"from": account}, 
        publish_source=config["networks"][network.show_active()]["verify"]
    )
    print(box.retrieve())

    # 2. Deploy Proxy Admin
    proxy_admin = ProxyAdmin.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"]
    )

    # 3a. Encode initializer function (optional)
    # initializer = box.store, 1
    box_encoded_initializer_function = encode_function_data() 
    
    # 3b. Deploy Proxy Contract
    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000},
        publish_source=config["networks"][network.show_active()]["verify"]
    )
    print(f"Proxy deployed to: {proxy}. You can now upgrade to V2.")
    
    # 3c. Call functions from V1 contract (optional)
    # Proxy -> BoxV1
    proxy_box = Contract.from_abi("Box", proxy, Box.abi)
    proxy_box.store(1, {"from": account})
    print(proxy_box.retrieve())

    # 4a. upgrade to V2
    box_v2 = BoxV2.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"]
    )
    upgrade_transaction = upgrade(
        account, proxy, box_v2, proxy_admin_contract=proxy_admin
    )
    upgrade_transaction.wait(1)
    print("Proxy has been upgraded!")
    
    # 4b. Call functions on V2 contract via proxy
    # Proxy -> BoxV2
    proxy_box = Contract.from_abi("BoxV2", proxy, BoxV2.abi)
    proxy_box.increment({"from": account})
    print(proxy_box.retrieve())


    

