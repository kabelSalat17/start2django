from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://ropsten.infura.io/v3/27eb2bd2c6e944dd935ec09c400be912'))
account = w3.eth.account.create()
privateKey = account.privateKey.hex()
address = account.address

print(f"Your Address: {address}\nYour key: {privateKey}")
