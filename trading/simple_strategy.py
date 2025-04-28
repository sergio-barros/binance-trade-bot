def simple_moving_average_strategy(data):
    closes = [float(x[4]) for x in data]
    short_ma = sum(closes[-20:]) / 20
    long_ma = sum(closes[-80:]) / 80

    if short_ma > long_ma:
        return "buy"
    elif short_ma < long_ma:
        return "sell"
    return "hold"