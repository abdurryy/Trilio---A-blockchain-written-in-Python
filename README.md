<h3>Trilio - A blockchain written in Python</h3>
<h1><img src="https://img.shields.io/badge/license-MIT-green"> <img src="https://img.shields.io/badge/python-v3.9-green"> <img src="https://img.shields.io/badge/category-blockchain-green">
</h1>

<h3>Point of development</h3>
<p>Even though I don't know much about blockchain technology or how it works at all, I've decided to create my own blockchain with consensus algorithm Proof-of-Stake (PoS). I've lately been working with Solidity and been learning about smart-contract development, and during I found it quite fun and interesting. That is why this has and is a very fun project to work on, and even though it might not be classed as a blockchain I've learned a lot during research and improved my Python skills a lot!</p>
<h3>How does Trilio work</h3>
<p>Trilio is a fast single-threaded PoS aimed blockchain that is built upon using classes to store memory variables and detailed architectures/models.
It has plenty of features but I'd rather call them integrated smart-contracts/smart-contract actions, which include:</p>

`Token transfers`
`Asset trading`
`Asset minting`
`Collection creation`

<h3>Install Trilio with 3 steps</h3>

```
$ pip install trilio==0.1.2
$ pip install datetime
$ pip install hashlib
```

<h3>Create your first wallet</h3>

```python
from trilio import Trilio

# make your own blockchain
myBlockchain = Trilio()

# create your own wallet
myWallet = myBlockchain.Address.create_address()

# wallet
myWalletAddress = myWallet["address"]

# wallet keys
myPrivateKey = myWalletAddress["pve"] # pve = private
myPublicKey = myWalletAddress["pbc"] # pbc = public

print(myPublicKey, myPrivateKey)
```

<h3>Contact me</h3>
Discord: LocalMOD#3782
