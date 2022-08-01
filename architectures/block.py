from datetime import datetime
import hashlib, time

class Trade:
    def __init__(self, timestamp, _to, _from, fassets, tassets, tradestorage):
        self.id = len(tradestorage.trades) + 1
        self._to = _to
        self._from = _from
        self.fassets = fassets
        self.tassets = tassets
        self.state = 0 # 0 = pending # 1 = accepted # 2 = decline
        self.created_at = timestamp
        tradestorage.trades.append(self)

class TradeHandler():
    def accept_trade(self, id, private_key, address, assets, _ad, tradestorage):
        for trade in tradestorage.trades:
            if trade.id == id:
                if trade.state == 2 or trade.state == 1:
                    return # This trade has already been interacted with
                if trade._to == address.get_public_key(private_key):
                    tassets = 0
                    for asset_id in trade.tassets:
                        for asset in assets.assets:
                            if asset.id == asset_id and asset.owner == trade._to:
                                tassets += 1
                    if tassets == len(trade.tassets):
                        for asset_id in trade.tassets:
                            assets.assets[asset_id-1].owner = address.get_public_key(trade._from)
                            for address in address.addresses:
                                if address["address"]["pve"] == trade._from:
                                    address["info"]["assets"].append(asset_id)
                            for address in _ad.addresses:
                                if address["address"]["pbc"] == trade._to:
                                    address["info"]["assets"].pop(address["info"]["assets"].index(asset_id))

                                    

                        for asset_id in trade.fassets:
                            assets.assets[asset_id-1].owner = trade._to
                            for address in _ad.addresses:
                                if address["address"]["pbc"] == trade._to:
                                    address["info"]["assets"].append(asset_id)
                                
                                

                        trade.state = 1
                else:
                    print("worng address")
        
    def decline_trade(self, id, private_key ,address, assets, _ad, tradestorage):
        for trade in tradestorage.trades:
            if trade.id == id:
                if trade.state == 2 or trade.state == 1:
                    return # This trade has already been interacted with
                if trade._from == private_key or trade._to == address.get_public_key(private_key):
                    for asset in assets.assets:
                        if str(asset.owner).replace("PendingTradeFrom:","") == address.get_public_key(trade._from):
                            asset.owner = address.get_public_key(trade._from)
                            for _address in _ad.addresses:
                                if _address["address"]["pve"] == trade._from:
                                    _address["info"]["assets"].append(asset.id)


                trade.state = 2
class Asset:
    def __init__(self, timestamp, public_key, collection_id, name, description, _ad=None, _as=None):
        self.id = len(_as.assets) + 1
        self.name = name
        self.description = description
        self.collection_id = collection_id
        self.created_at = timestamp
        self.owner = public_key
        self.trading = False
        self.selling = False
        _as.assets.append(self)
        for address in _ad.addresses:
            if address["address"]["pbc"] == public_key:
                address["info"]["assets"].append(self.id)



class Block:
    def __init__(self, timestamp, transactions, previous_hash="",addresses = "", collections="", assets="", trades="", asset=""):
        self.addresses = addresses
        self.asset = asset
        self.collections = collections
        self.assets = assets
        self.trades = trades
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.hash = self.get_hash()
        self.status = 0 # 0 = pending, 1 = completed 
        self.complete()
    
    def complete(self):

        for transaction in self.transactions:
            try:
                pbc = self.addresses.get_public_key(transaction.input["data"]["from"])
                pve = transaction.input["data"]["from"]
            except:
                pass

            if transaction == "genisis block":
                return
            
            if transaction.input["type"] == "token-transfer":
                if float(transaction.input["data"]["amount"]) >= 0:
                    if self.addresses.get_balance(pve, pbc) >= float(transaction.input["data"]["amount"]):
                        self.addresses.credit_address(transaction.input["data"]["to"], float(transaction.input["data"]["amount"]))
                        self.addresses.credit_address(pbc, -float(transaction.input["data"]["amount"]))
            elif transaction.input["type"] == "contract-action":
                # if collection name is valid continue
                # create collection
                if transaction.input["action"] == "collection-creation":
                    is_valid_name = self.collections.validate_collection_name(transaction.input["data"]["name"])
                    if is_valid_name:
                        pbc = self.addresses.get_public_key(transaction.input["data"]["signer"])
                        self.collections.create_collection(datetime.now().timestamp(), pbc, transaction.input["data"]["url"], transaction.input["data"]["icon"], transaction.input["data"]["name"], transaction.input["data"]["description"], transaction.input["data"]["tags"], self.addresses)
                # fix minting
                elif transaction.input["action"] == "asset-creation":
                    pbc = self.addresses.get_public_key(transaction.input["data"]["signer"])
                    is_collection_owner = self.collections.validate_collection_owner(pbc, transaction.input["data"]["collection_id"])
                    if is_collection_owner:
                        Asset(datetime.now().timestamp(), pbc, transaction.input["data"]["collection_id"], transaction.input["data"]["name"], transaction.input["data"]["description"], self.addresses, self.assets)
                elif transaction.input["action"] == "accept-trade":
                    TradeHandler().accept_trade(transaction.input["data"]["id"],transaction.input["data"]["signer"], self.addresses, self.assets, self.addresses, self.trades)
                elif transaction.input["action"] == "decline-trade":
                    TradeHandler().decline_trade(transaction.input["data"]["id"],transaction.input["data"]["signer"], self.addresses, self.assets, self.addresses, self.trades)
            elif transaction.input["type"] == "asset-transfer":
                # check if the user owns the assets
                # check if the other user owns the assets
                fassets = 0
                tassets = 0
                for asset_id in transaction.input["data"]["fassets"]: # this is what they sending
                    for asset in self.assets.assets:
                        if asset.id == asset_id and asset.owner == self.addresses.get_public_key(transaction.input["data"]["_from"]):
                            fassets += 1

                for asset_id in transaction.input["data"]["tassets"]: # this is what they other are sending
                    for asset in self.assets.assets:
                        if asset.id == asset_id and asset.owner == transaction.input["data"]["_to"]:
                            tassets += 1

                if fassets == len(transaction.input["data"]["fassets"]):
                    if tassets == len(transaction.input["data"]["tassets"]):
                        for asset_id in transaction.input["data"]["fassets"]:
                            self.assets.assets[asset_id-1].owner = "PendingTradeFrom:"+self.addresses.get_public_key(transaction.input["data"]["_from"])
                            for address in self.addresses.addresses:
                                if address["address"]["pve"] == transaction.input["data"]["_from"]:
                                    address["info"]["assets"].pop(asset_id-1)
                        
                        Trade(datetime.now().timestamp(), transaction.input["data"]["_to"], transaction.input["data"]["_from"], transaction.input["data"]["fassets"], transaction.input["data"]["tassets"], self.trades)
                
        self.status = 1
    
    def get_hash(self):
        return hashlib.sha256(str(self.timestamp).encode('utf-8')+str(self.transactions).encode('utf-8')+str(self.previous_hash).encode('utf-8')).hexdigest()