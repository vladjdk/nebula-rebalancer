class Asset:
    def __init__(self, contract_addr=None, denom=None, amount=0):
        if contract_addr is None and denom is None:
            raise Exception("Contract address or denom must contain value")
        if contract_addr is not None and denom is not None:
            raise Exception("Asset must either be native or a token")

        self.contract_addr = contract_addr
        self.denom = denom
        self.amount = amount

    def get_dict(self):
        if self.contract_addr is not None:
            return {
                "info": {
                    "token": {
                        "contract_addr": self.contract_addr
                    },
                },
                "amount": str(self.amount)
            }
        else:
            return {
                "info": {
                    "native_token": {
                        "denom": self.denom
                    },
                },
                "amount": str(self.amount)
            }

    def __str__(self):
        return "Asset: {}, Amount: {}".format(self.contract_addr,
                                              self.amount) if self.contract_addr else "Asset: {}, Amount: {}".format(
            self.denom, self.amount)

    def __repr__(self):
        return "Asset: {}, Amount: {}".format(self.contract_addr,
                                              self.amount) if self.contract_addr else "Asset: {}, Amount: {}".format(
            self.denom, self.amount)
