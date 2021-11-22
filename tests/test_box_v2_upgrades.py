from scripts.helpful_scripts import get_account, upgrade, encode_function_data
from brownie import (
    Box,
    ProxyAdmin, 
    TransparentUpgradeableProxy,
    BoxV2, 
    Contract,
    network,
    exceptions
)
import pytest

def test_proxy_upgrades():
    # 1. Deploy V1 contract
    account = get_account()
    box = Box.deploy({"from": account})

    # 2. Deploy Proxy Admin
    proxy_admin = ProxyAdmin.deploy({"from": account})

    # 3a. Encode initializer function (optional)
    # initializer = box.store, 1
    box_encoded_initializer_function = encode_function_data() 
    
    # 3b. Deploy Proxy Contract
    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000}
    )
    
    # assert proxy is not yet upgraded to V2
    box_v2 = BoxV2.deploy({"from": account})
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    with pytest.raises(exceptions.VirtualMachineError):
        proxy_box.increment({"from": account})

    # upgrade to V2
    upgrade_transaction = upgrade(
        account, proxy, box_v2, proxy_admin_contract=proxy_admin
    )
    upgrade_transaction.wait(1)
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    
    # assert proxy is incremented to V2
    proxy_box.increment({"from": account})
    assert proxy_box.retrieve() == 1


