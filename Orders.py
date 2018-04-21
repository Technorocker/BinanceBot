import config
from numpy import *
import math
from decimal import *
from binance.exceptions import BinanceAPIException as e
from Messages import Messages
from Balance import Balance
import time

#Define API keys
client = config.bclient

class Orders:

	#Join assets into pair variable
	@staticmethod
	def pair(asseta, assetb):
		pair = asseta + assetb
		return pair

	@staticmethod
	def exchangeinfo(pair):
		try:
			exchangeinfo = client.get_exchange_info()
			if pair != "":
				for market in exchangeinfo['symbols']:
					if market["symbol"] == pair:
						return market
			return exchangeinfo

		except e:
			print(e.message)
			return

	# Get Market Price for Given Pair
	@staticmethod
	def getpairprice(pair):
		try:
			prices = client.get_ticker()
			for i in prices:
				if i['symbol'] == pair:
					price = float(i['lastPrice'])
					return price

		except e:
			print(e.status_code)
			print(e.message)
			exit()

	@staticmethod
	def maxusquantity(balance, market, pairinfo):
		# Get Max quantity and lot size for  USDT buy order
		quantity = round(float(balance), 2) / float(market)
		#print(type(quantity))
		#print('max buy qty', quantity)
		for filt in pairinfo['filters']:
			if filt['filterType'] == 'LOT_SIZE':
				#print(filt['stepSize'])
				ticks = filt['stepSize'].find('1') - 1
				#print('Ticks', ticks)
				ticks = float(ticks)
				quantity = math.floor(quantity * 10 ** ticks) / float(10 ** ticks)
				#print('Quantity', quantity)
				percent = (quantity * 0.2) / 100
				quantity = Balance.format(quantity - percent)
				#print('New quantity is', quantity)
		# Set precision for BTC Trades
		quantity = Decimal(str(quantity)).quantize(Decimal('.000001'), ROUND_DOWN)
		#print('max buy order',quantity)
		return float(quantity)

	@staticmethod
	def maxcoinquantity(asset):
		balance = client.get_asset_balance(asset)
		balance = float(balance['free'])
		qty = Balance.format(balance)
		qty = float(qty)
		percent = (float(qty) * 0.2) / 100
		#print('percent', type(percent))
		quantity = qty - percent
		#print(type(quantity))
		quantity = Balance.format(quantity)
		return float(quantity)

	# Get minimal Amount to sell order on ETH trade ETHBTC Pair
	@staticmethod
	def minamount1(pair, price, symbolinfo):
		minord = symbolinfo['filters'][2]['minNotional']
		minorder1 = float(minord)
		minorder1 = minorder1/price
		minorder1 = float(("%.8f" % minorder1))
		minorder1 = Orders.lotamount(minorder1, symbolinfo)
		print('Minimum order for ',pair,' is:',minorder1)
		return minorder1

	@staticmethod
	def lotamount(balance, symbolinfo):
		coins_available = balance
		for filt in symbolinfo['filters']:
			if filt['filterType'] == 'LOT_SIZE':
				ticks = filt['stepSize'].find('1') - 1
				#print('Tick size', ticks)
				order_quantity = math.floor(coins_available * 10 ** ticks) / float(10 ** ticks)
				return order_quantity

	# Get minimal Amount to buy order on USDT for ETHUSDT trade
	@staticmethod
	def pricerange(balance, symbolinfo):
		coins_available = float(balance)
		for filt in symbolinfo['filters']:
			if filt['filterType'] == 'PRICE_FILTER':
				ticks = int(filt['minPrice'].find('1') - 1)
				#print('Tick size', ticks)
				#print('%.*f' % (ticks, coins_available))
				minprice = math.floor(coins_available * 10 ** ticks) / float(10 ** ticks)
				return minprice

	@staticmethod
	def buylimitorder(pair, quantity, mrktprc):
		try:
			results = {}
			percentage = (mrktprc * 0.2) / 100
			percentage = float(("%.8f" % percentage))
			orderprice = mrktprc - percentage
			orderprice = ("%.2f" % orderprice)
			#print('Market', mrktprc, 'with order', orderprice)
			#print('Quantity:',quantity)
			orderId = client.order_limit_buy(
				symbol=pair,
				quantity=quantity,
				price=orderprice)

			print('==========Buying=================')
			print('Market price right now is:', mrktprc)
			print('Trying to buy order for:', orderprice)
			results['orderId'] = int(orderId['orderId'])
			results['orderprice'] = orderprice
			if 'msg' in orderId:
				Messages.get(orderId['msg'])
				print(orderId['msg'])

			# Buy order created
			return results
		except e:
			print('buylimitorder error')
			print(e.status_code)
			print(e.message)
			return

	@staticmethod
	def selllimitorder(pair, quantity, mrktprc):
		try:
			results = {}
			percentage = (mrktprc * 0.15) / 100
			percentage = float(("%.8f" % percentage))
			orderprice = mrktprc + percentage
			orderprice = ("%.2f" % orderprice)
			orderId = client.order_limit_sell(
				symbol=pair,
				quantity=quantity,
				price=orderprice)

			print('============Selling==============')
			print('Market price right now is:',mrktprc)
			print('Trying to sell order for:',orderprice)
			#print('OrderId is:', orderId['orderId'])
			results['orderId'] = int(orderId['orderId'])
			results['orderprice'] = orderprice
			print(results['orderId'])
			if 'msg' in orderId:
				Messages.get(orderId['msg'])
				print(orderId['msg'])

			# Buy order created
			return results

		except e:
			print('selllimitorder error')
			print(e.status_code)
			print(e.message)
			return

	@staticmethod
	def buymarketorder(pair, quantity):
		try:
			orderId = client.order_market_buy(
				symbol=pair,
				quantity=quantity)

			#print('Buy orderId is:',orderId['status'])

			if 'msg' in orderId:
				Messages.get(orderId['msg'])

			# Buy order created
			return float(orderId['price'])

		except e:
			print(e.status_code)
			print(e.message)
			return

	@staticmethod
	def sellmarketorder(pair, quantity):
		try:
			orderId = client.order_market_sell(
				symbol=pair,
				quantity=quantity)

			#print ('OrderId is:',orderId['orderId'])
			if 'msg' in orderId:
				Messages.get(orderId['msg'])

			# Buy order created
				return float(orderId['price'])

		except e:
			print(e.status_code)
			print(e.message)
			return

	@staticmethod
	def cancelorder(pair, orderId):
		try:
			order = client.cancel_order(
				symbol=pair,
				orderId=orderId)

			if 'msg' in order:
				Messages.get(order['msg'])
			#print('Order didnt go through so its cancelled')

			return order#['clientOrderId']


		except e:
			print(e.status_code)
			print(e.message)

	@staticmethod
	def checkorderstatus(pair, orderId):
		order = client.get_order(
			symbol=pair,
			orderId=orderId)
		#print(order)
		#print('Order Status',order['status'])
		return order['status']

	@staticmethod
	def allorders():
		try:
			order = client.get_open_orders()
			'''for i in order:
				print(i['symbol'])
				items = int(i[0])
				print(items)'''

			if 'msg' in order:
				Messages.get(order['msg'])
				return False

			return order


		except e:
			print('Status Code',e.status_code)
			print('Message',e.message)

