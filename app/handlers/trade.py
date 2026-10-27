class TradeInfo:
    def __init__(self, trades):
        self.total = 0
        self.trades = []
        self._parse(trades)

    def _parse(self, trades):
        self.total = len(trades)
        self.trades = [self._map_to_trade(gift) for gift in trades]

    @staticmethod
    def _map_to_trade(single):
        return dict(
            user_name=single.user.nickname,
            time=single.created_at.strftime("%Y-%m-%d"),
            id=single.id,
        )
