class Formatter:
    @staticmethod
    def signal(stock, strategy, buy, target):
        return (
            f"📈 BUY SIGNAL\n"
            f"Stock: {stock}\n"
            f"Strategy: {strategy}\n"
            f"Buy Range: {buy}\n"
            f"Stoploss: None\n"
            f"Target: {target}\n"
        )