import config
import math
import time
from decimal import Decimal
client = config.bclient

class Balance:

	@staticmethod
	def floatPrecision(f, n):
		n = int(math.log10(1 / float(n)))
		f = math.floor(float(f) * 10 ** n) / 10 ** n
		f = "{:0.0{}f}".format(float(f), n)
		return str(int(f)) if int(n) == 0 else f


	@staticmethod
	def bothbalances(asset1, asset2):
		asset1bal = 0
		asset2bal = 0
		# Get Account balances for pair
		info = client.get_account()
		# print(info)
		for i in info['balances']:
			if i['asset'] == asset1:
				asset1bal = float(i['free'])
			if i['asset'] == asset2:
				asset2bal = float(i['free'])
		return {'1': float(asset1bal), '2': float(asset2bal)}

	@staticmethod
	# Get asset balance
	def assetbalance(asset):
		balance = client.get_asset_balance(asset)
		balance = float(balance['free'])
		return balance

	@staticmethod
	def format(price):
		if float(price) < float(1):
			return "{:.8f}".format(price)  # using 8 digits
		else:
			return "{:.2f}".format(price)  # or 2 digits

	@staticmethod
	def minNotional(pairinfo):
		for filt in pairinfo['filters']:
			if filt['filterType'] == 'MIN_NOTIONAL':
				# print(filt['stepSize'])
				notional = filt['minNotional']
				return float(notional)

	@staticmethod
	def stepsize(pairinfo):
		for filt in pairinfo['filters']:
			if filt['filterType'] == 'LOT_SIZE':
				# print(filt['stepSize'])
				step = filt['stepSize']
				step = Decimal(step).normalize()
				#print(type(step))
				return float(step)

	@staticmethod
	def ticksize(pairinfo):
		for filt in pairinfo['filters']:
			if filt['filterType'] == 'PRICE_FILTER':
				# print(filt['tickSize'])
				ticks = filt['tickSize']
				return float(ticks)

	@staticmethod
	def profit_calculator(lastprice, newprice):
		profit1 = float(newprice) - float(lastprice)
		return float(Balance.format(profit1))

	@staticmethod
	def pricerange(firstprice, highprice, currentMA):
		#pcnt = 80
		if abs(highprice - firstprice) <= 50:
			pcnt = 60
		# print ('Percent is:',pcnt)
		elif 50 < abs(highprice - firstprice) <= 100:
			pcnt = 65
		# print ('Percent is:',pcnt)
		elif 100 < abs(highprice - firstprice) <= 150:
			pcnt = 70
		elif abs(highprice - firstprice) > 150:
			pcnt = 75
		if currentMA == 'uptrend':
			# print('-=-=-=-=-=-=-Price range  uptrend method-=-=-=-=-=-=-=')
			total = float(highprice) - float(firstprice)
			# print('Total difference between peak:',peakprice,' and start',startprice,' is:', total)
			shifttime = (total * pcnt) / 100
			# print('75 Percent is', shifttime)
			final = float(firstprice) + float(shifttime)
			# print('Price to make order with is:', final)
			return final
		elif currentMA == 'downtrend':
			# print('-=-=-=-=-=-=-Price range downtrend method-=-=-=-=-=-=-=')
			total = float(firstprice) - float(highprice)
			# print('Total difference between start',startprice,'and peak:',peakprice,' is:', total)
			shifttime = (total * pcnt) / 100
			# print('75 Percent is', shifttime)
			final = float(firstprice) - float(shifttime)
			# print('Price to make order with is:', final)
			return final

	@staticmethod
	def us_value_in_btc(balance, pairprice):
		btc = balance / pairprice
		#print('Balance is btc is', Balance.format(btc))
		maxbtc = btc - ((btc * 0.2) / 100)
		finalbtc = maxbtc - ((maxbtc * 0.1) / 100)

		#print('Total after fees is', Balance.format(finalbtc))
		return float(Balance.format(finalbtc))

	@staticmethod
	def btc_value_after_fees(balance):
		btc = balance
		#print('Balance is btc is', Balance.format(btc))
		maxbtc = btc - ((btc * 0.2) / 100)
		finalbtc = maxbtc - ((maxbtc * 0.1) / 100)
		#print('Total after fees is', Balance.format(finalbtc))
		return float(Balance.format(finalbtc))