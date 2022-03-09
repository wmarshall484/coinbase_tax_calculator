# coinbase_tax_calculator

If you go to coinbase and download your account statement for a particular period of time, you'll see a list of transactions in a pdf. If you ctrl-c ctrl-v that into a document called "coinbase_txns.csv", you can use this program to calculate your capital gains, capital losses, and fees for that time period using LIFO accounting.

This only works for one currency at a time right now, so you need to specificy the currency when initializing the calculator, but it shouldn't be too hard to modify it to handle everything at once.

Usage:
```
cbc = CoinbaseCalc(curr='NMR')
cbc.calc()
print(cbc.gains, cbc.losses, cbc.fees)
```
