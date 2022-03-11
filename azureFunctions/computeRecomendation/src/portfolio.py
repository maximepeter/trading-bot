from ast import List


class Portfolio:
    def __init__(self, usdAmount: float):
        self.usdBalance: float = usdAmount
        self.nbStocks: float = 0.0
        self.binanceFees: float = 0.001

    def updateWallet(self, update: float, nbStocks: float, operationType: str) -> None:
        if operationType == "buy" and self.usdBalance < update * nbStocks * (1 + self.binanceFees):
            print("Operation not possible : balance too low")
        elif operationType == "sell" and self.nbStocks < nbStocks:
            self.usdBalance += update * self.nbStocks * (1 - self.binanceFees)
            self.nbStocks -= self.nbStocks
        elif operationType == "buy" and self.usdBalance >= update * nbStocks * (1 + self.binanceFees):
            self.usdBalance -= update * nbStocks * (1 + self.binanceFees)
            self.nbStocks += nbStocks
        else:
            self.usdBalance += update * nbStocks * (1 - self.binanceFees)
            self.nbStocks -= nbStocks

    def getWallet(self) -> List:
        return [self.usdBalance, self.nbStocks]
