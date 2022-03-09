from collections import defaultdict
f = open('coinbase_txns.csv', 'r')

class CoinbaseCalc:
    def __init__(self, curr = 'BTC'):
        self.curr = curr
        lines = f.read().split('\n')
        lines = [line.split(' ') for line in lines]
        lines = lines[1:]

        txns = defaultdict(dict)
        for line in lines:
            ttype, amount, currency, txn_id = line[1], float(line[5]), line[6], line[9]
            if ttype != 'Match' and ttype != 'Fee':
                continue
            if ttype == 'Match':
                if currency == 'USD':
                    if amount <= 0:
                        txns[txn_id]['type'] = 'buy'
                    else:
                        txns[txn_id]['type'] = 'sell'

                    txns[txn_id]['dollar_amount'] = amount if amount > 0 else -amount
                    txns[txn_id]['txn_id'] = txn_id
                else:
                    txns[txn_id]['currency_amount'] = amount if amount > 0 else -amount
                    txns[txn_id]['txn_id'] = txn_id
                    txns[txn_id]['currency'] = currency
            if ttype == 'Fee':
                txns[txn_id]['fee'] = amount
        txns = zip(txns.keys(), txns.values())
        self.txns = [x[1] for x in sorted(txns, key=lambda x: x[0]) if x[1]['currency'] == self.curr] 
        for txn in self.txns:
            txn['usd_per_unit'] = txn['dollar_amount'] / txn['currency_amount']
        self.losses = 0.0
        self.gains = 0.0
        self.fees = 0.0
        self.purchases = []

    def calc(self):
        for txn in self.txns:
            self.fees += -txn['fee']
            if txn['type'] == 'buy':
                self.purchases.append(txn)
            else:
                purchase = self.purchases[-1]
                if not purchase:
                    raise ValueError('purchase should never be zero')
                sell_currency_amount = txn['currency_amount']
                buy_currency_amount = purchase['currency_amount']

                wipe_out_purchase = buy_currency_amount <= sell_currency_amount
                while wipe_out_purchase:
                    original_purchase_total = buy_currency_amount * purchase['usd_per_unit']
                    current_sell_total = buy_currency_amount * txn['usd_per_unit']
                    diff = current_sell_total - original_purchase_total
                    if diff > 0:
                        self.gains += diff
                        txn_id = txn['txn_id']
                        b_txn_id = purchase['txn_id']
                        print(f'{txn_id} sold for {diff} against {b_txn_id}')
                    else:
                        self.losses -= diff

                    sell_currency_amount = sell_currency_amount - buy_currency_amount
                    if sell_currency_amount <= 0:
                        break
                    self.purchases.pop(-1)
                    purchase = self.purchases[-1]
                    
                    buy_currency_amount = purchase['currency_amount']
                    wipe_out_purchase = buy_currency_amount <= sell_currency_amount

                if sell_currency_amount <= 0:
                    continue
                original_purchase_total = sell_currency_amount * purchase['usd_per_unit']
                current_sell_total = sell_currency_amount * txn['usd_per_unit']

                diff = current_sell_total - original_purchase_total
                if diff > 0:
                    self.gains += diff
                    txn_id = txn['txn_id']
                    b_txn_id = purchase['txn_id']
                    print(f'{txn_id} sold for {diff} against {b_txn_id}')
                else:
                    self.losses += -diff

cbc = CoinbaseCalc(curr='NMR')
cbc.calc()
print(cbc.gains, cbc.losses, cbc.fees)
