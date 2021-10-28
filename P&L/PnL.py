#!/tool/pandora64/bin/python3

import sys
import os
import pandas as pd

if len(sys.argv) <= 2:
	print("Instructions: PnL.py <trades csv> <price_marks csv>")
	print("In that input order")
	exit()

if os.path.isfile(sys.argv[1]) == True:
	trades = pd.read_csv(sys.argv[1])
else:
	print(sys.argv[1], "does not exist")
	exit()
if os.path.isfile(sys.argv[2]) == True:
	priceMarks = pd.read_csv(sys.argv[2])
else:
	print(sys.argv[2], "does not exist")
	exit()

# checking for non numeric and null values

check = pd.to_numeric(trades["Quantity"], errors="coerce").notnull().all()
if check != True:
	print(sys.argv[1], "Non numeric value found in Quantity column")
	exit()
check = pd.to_numeric(trades["Price"], errors="coerce").notnull().all()
if check != True:
	print(sys.argv[1], "Non numeric value found in Price column")
	exit()
check = pd.to_numeric(priceMarks["Marking_Price"], errors="coerce").notnull().all()
if check != True:
	print(sys.argv[2], "Non numeric value found in Marking_Price column")
	exit()
check = pd.isnull(trades["Symbol"]).all()
if check == True:
	print(sys.argv[1], "NULL value found in Symbol column")
	exit()
check = pd.isnull(trades["Symbol"]).all()
if check == True:
	print(sys.argv[1], "NULL value found in Buy/Sell column")
	exit()
check = pd.isnull(priceMarks["Symbol"]).all()
if check == True:
	print(sys.argv[2], "NULL value found in Symbol column")
	exit()

# get total amount per trade

totalPrice = trades["Quantity"] * trades["Price"]
trades["Total_Price"] = totalPrice

# Separate Buy and Sell

tradesBuys = trades[trades["Buy/Sell"] == "Buy"][["Symbol", "Quantity", "Total_Price"]].groupby("Symbol").sum().sort_values("Symbol").reset_index()
tradesSells = trades[trades["Buy/Sell"] == "Sell"][["Symbol", "Quantity", "Total_Price"]].groupby("Symbol").sum().sort_values("Symbol").reset_index()

#print(tradesBuys)
#print(tradesSells)

# Calculate remaining position and net money

priceDiff = tradesSells["Total_Price"] - tradesBuys["Total_Price"]
quantityDiff = tradesBuys["Quantity"] - tradesSells["Quantity"]

finalTrades = tradesBuys

finalTrades["Cash_Profit"] = priceDiff
finalTrades["Remaining_Position"] = quantityDiff


# Join Price marks table, replace NaN with 0

finalTrades = finalTrades.merge(priceMarks, how="outer", on="Symbol")[["Symbol", "Remaining_Position", "Cash_Profit", "Marking_Price"]]
finalTrades["Remaining_Position"] = finalTrades["Remaining_Position"].fillna(0)
finalTrades["Cash_Profit"] = finalTrades["Cash_Profit"].fillna(0)
finalTrades["Marking_Price"] = finalTrades["Marking_Price"].fillna(0)

#print(finalTrades)

nanValues = finalTrades[finalTrades["Marking_Price"] == 0]["Symbol"].tolist()
if len(nanValues) > 0:
	print("WARNING ...", ",".join(nanValues), "have no marking price. Marking price of 0 used instead.")
	print("")

#print(finalTrades)

# Calculate final P&L

profitLoss = finalTrades["Cash_Profit"] + (finalTrades["Remaining_Position"] * finalTrades["Marking_Price"])
finalTrades["P&L"] = profitLoss
finalTrades = finalTrades.drop(["Cash_Profit", "Marking_Price"], axis=1)

print(finalTrades)