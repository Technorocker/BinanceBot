import config
import time
from binance.exceptions import BinanceAPIException
from Orders import Orders
from Balance import Balance
import Binancewebsocket
from playsound import playsound
from colorama import init, Fore
init(autoreset=True)


def pricerange(firstprice, highprice, currentMA):
	pcnt = 75
	'''if abs(highprice - firstprice) <= 30:
		pcnt = 75
	# print ('Percent is:',pcnt)
	elif 30 < abs(highprice - firstprice) <= 50:
		pcnt = 80
	# print ('Percent is:',pcnt)
	elif 50 < abs(highprice - firstprice) <= 100:
		pcnt = 85
	else:
		pcnt = 90'''
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

Binancewebsocket.initiate()
client = config.bclient
'''mode = input('Enter mode, Press (t) for testing or (l) for live:')
if mode == 't':
	mode = 'testing'
elif mode == 'l':
	mode = 'live'
asset1 = input('Enter asset1:')
asset2 = input('Enter asset2:')
klinetime = input('Enter timeframe of "1m" "5m" "15m" or "1h":')'''

asset1 = 'btc'
asset2 = 'usdt'
mode = 'live'
asset1 = asset1.upper()
asset2 = asset2.upper()
pair = Orders.pair(asset1, asset2)
print('Pair is', pair)
pairinfo = client.get_symbol_info(pair)

# Current Time
attime = time.strftime('%X %x %Z')
print(attime)

#Timer Variables
cycletime = 180
waittime = 1
peaklimit = 40
orderwait = 30

# Setup price List array
pricearray = Binancewebsocket.btcres_array
fulllist = 0
while fulllist < 5:
	fulllist = len(pricearray)
	# print('Fulllist size is:',fulllist)
	time.sleep(2)
print('Price Array is Full, Starting cycle')
print('Starting ', asset2, ' Balance is', Balance.assetbalance(asset2))
print('Starting ', asset1, ' Balance is', Balance.assetbalance(asset1))
print('Startprice is', pricearray[0]['p'],'\n')
# Set While Loop Vars
if mode == 'testing':
	cash = float(Balance.assetbalance(asset2))
else:
	cash = 0
startprice = float(pricearray[0]['p'])

selltime = False
buytime = False
peakprice = None
startorder = True
lasttrend = None
trend = None
firstbuyskip = True
firstsellskip = True
lastbuyprice = None
lastsellprice = None
profitfault = 0
rebalancing = 0
while True:
	pairprice = float(pricearray[0]['p'])
	#print('Pair price is:',pairprice)

	if profitfault == 2 or rebalancing == 3:
		startprice = float(pricearray[0]['p'])
		print('-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
		print('-=-=-=-    Too many out of range attempts, resetting all   =-=-=-=-=')
		print('-=-=-=-    Cash is:',Balance.format(cash),'                 -=-=-=-=')
		print('-=-=-=-   New startprice is',startprice,'                   -=-=-=-=')
		print('-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-==-=-=-=-=-=-=-=-=-=-==')
		#startorder = True
		selltime = False
		buytime = False
		peakprice = None
		#lasttrend = None
		trend = None
		firstbuyskip = True
		firstsellskip = True
		lastbuyprice = None
		lastsellprice = None
		profitfault = 0

	if pairprice < startprice - peaklimit:
		trend = 'downtrend'
	elif pairprice > startprice + peaklimit:
		trend = 'uptrend'

	# updating Peak Price
	if peakprice is None:
		peakprice = pairprice
		#print('Setting new peak price at:', peakprice)
	elif trend == 'downtrend':
		if pairprice < peakprice:
			peakprice = pairprice
			# print('Trend', priceavg)
			#print('\nDownward Peak price is now:', peakprice)
			#print('Current Pair price is:',pairprice)
	elif trend == 'uptrend':
		if pairprice > peakprice:
			peakprice = pairprice
			# print('Trend', priceavg)
			#print('\nUpward Peak price is now:', peakprice)
			#print('Current Pair price is:',pairprice)

	ordertime = pricerange(startprice, peakprice, trend)
	if trend is None:
		pass
	elif trend == 'uptrend':
		if ordertime > pairprice > startprice + peaklimit:
			print('Testing Sell')
			attime = time.strftime('%X %x %Z')
			print(attime)
			print('Order Limit is:', ordertime)
			print('Startprice was', startprice)
			print('Pairprice is:', pairprice, '\n\n')
			time.sleep(orderwait)
			if ordertime > pairprice > startprice + peaklimit:
				if lastbuyprice is None:
					pass
				elif pairprice < lastbuyprice:
					print('Price is below start price selling\n')
					selltime = False
					profitfault = profitfault + 1
					time.sleep(cycletime)
					continue
				if firstsellskip is True:
					print('Bypassing first sell order')
					attime = time.strftime('%X %x %Z')
					print(attime)
					print('Order Limit is:', ordertime,'\n\n')
					time.sleep(cycletime)
					firstsellskip = False
					continue
				#else:
				selltime = True
				buytime = False
	elif trend == 'downtrend':
		if ordertime < pairprice < startprice - peaklimit:
			print('Testing buy')
			attime = time.strftime('%X %x %Z')
			print(attime)
			print('Pairprice is:', pairprice)
			print('Startprice was', startprice)
			print('Orderprice is:', ordertime, '\n\n')
			time.sleep(orderwait)
			if ordertime < pairprice < startprice - peaklimit:
				if lastsellprice is None:
					pass
				elif pairprice > lastsellprice:
					print('Price is above startprice buying\n')
					profitfault = profitfault + 1
					time.sleep(cycletime)
					buytime = False
					continue
				if firstbuyskip is True:
					print('Bypassing first buy order')
					attime = time.strftime('%X %x %Z')
					print(attime)
					print('Order Limit is:', ordertime,'\n\n')
					time.sleep(cycletime)
					firstbuyskip = False
					continue
				#else:
				buytime = True
				selltime = False

	if lasttrend is None:
		pass
	elif lasttrend == trend:
		orderbook = client.get_orderbook_ticker(symbol=pair)
		if trend == 'uptrend' and selltime is True:
			print('Tried to sell again\n\n')
			'''attime = time.strftime('%X %x %Z')
			print(attime)
			startprice = float(orderbook['askPrice'])
			print('Peak price was:', peakprice)
			trend = 'downtrend'
			lasttrend = 'uptrend'
			print('Start price and sell out is now:', startprice,'\n')'''
			rebalancing = rebalancing+1
			peakprice = None
			selltime = False
			time.sleep(cycletime)
			continue
		elif trend == 'downtrend' and buytime is True:
			print('Tried to buy again\n\n')
			'''attime = time.strftime('%X %x %Z')
			print(attime)
			startprice = float(orderbook['bidPrice'])
			print('Peak price was:', peakprice)
			print('Start price and buy back is now:', startprice,'\n')
			trend = 'uptrend'
			lasttrend = 'downtrend'''''
			rebalancing = rebalancing+1
			peakprice = None
			buytime = False
			time.sleep(cycletime)
			continue

	if buytime is True:
		try:
			print('\n\nTime To place buy order')
			print('-=-=-=-=-=-=-=-=-=-=-=-=-==-=-=\n')
			print('Start price is:', startprice)
			print('Peak price is', peakprice)
			print('Peakprice difference is', abs(startprice - peakprice))
			print('Pair price is', pairprice)
			print('final price to buy right now is:', ordertime)
			attime = time.strftime('%X %x %Z')
			print(attime,'\n')

			# Get highest askprice price to buy in
			orderbook = client.get_orderbook_ticker(symbol=pair)

			#Check if balance is enough to place order
			checkbal = float(Balance.assetbalance(asset2))
			#print(asset2, ' balance is', checkbal)
			if Balance.minNotional(pairinfo) >= 1:
				if checkbal < float(Balance.minNotional(pairinfo)):
					print('Not enough balance to buy at',pairprice,', Starting cycle over\n')
					buyprice = float(orderbook['askPrice'])

					if mode == 'testing':
						if startorder is True or lastsellprice is None:
							lastbuyprice = buyprice
							pass
						elif lasttrend != 'downtrend':
							pricediff = Balance.profit_calculator(lastsellprice, buyprice)
							print('price difference is:', abs(pricediff))
							btc_after_fees = Balance.us_value_in_btc(cash, pairprice)
							realprofit = abs(pricediff) * btc_after_fees
							print('Realprofit is:', realprofit)
							if buyprice > lastsellprice:
								cash = cash - abs(realprofit)
								print(Fore.RED + 'last sell price was', lastsellprice)
								print(Fore.RED + 'bought for', buyprice, 'and lost', Balance.format(realprofit), 'profit')
								print(Fore.RED + 'Cash',  Balance.format(cash))


							else:
								cash = cash + abs(realprofit)
								print(Fore.GREEN + 'last sell price was', lastsellprice)
								print(Fore.GREEN + 'bought for', buyprice, 'and made ', Balance.format(realprofit), 'profit')
								print(Fore.GREEN + 'Cash is now:', cash)
							print('Total cash is now', cash)


					#if lasttrend != 'downtrend':
					lastbuyprice = buyprice
					startprice = buyprice
					trend = 'uptrend'
					profitfault = 0
					rebalancing = 0

					firstbuyskip = True
					startorder = False
					peakprice = None
					buytime = False
					lasttrend = 'downtrend'
					print('-=-=-=-=-=-=-=-==-= End of buy cycle1 =-=-=-=-=-=-=-=-==-\n')
					time.sleep(cycletime)
					continue

			elif Balance.minNotional(pairinfo) < 1:
				finalbal = float(checkbal) * float(pairprice)
				if finalbal < Balance.minNotional(pairinfo):
					print('Not enough balance to buy at',pairprice,', Starting cycle over\n')
					buyprice = float(orderbook['askPrice'])

					if mode == 'testing':
						if startorder is True or lastsellprice is None:
							print('Startorder was true or lastprice was none. Setting lastbuyprice')
							pass
						elif lasttrend != 'downtrend':
							pricediff = Balance.profit_calculator(lastsellprice, buyprice)
							print('price difference is:', abs(pricediff))
							btc_after_fees = Balance.us_value_in_btc(cash, pairprice)
							realprofit = abs(pricediff) * btc_after_fees
							print('Realprofit is:', realprofit)
							if buyprice > lastsellprice:
								cash = cash - abs(realprofit)
								print(Fore.RED + 'last sell price was', lastsellprice)
								print(Fore.RED + 'bought for', buyprice, 'and lost', Balance.format(realprofit),
								      'profit')
								print(Fore.RED + 'Cash', Balance.format(cash))


							else:
								cash = cash + abs(realprofit)
								print(Fore.GREEN + 'last sell price was', lastsellprice)
								print(Fore.GREEN + 'bought for', buyprice, 'and made ', Balance.format(realprofit),
								      'profit')
								print(Fore.GREEN + 'Cash is now:', cash)
							print('Total cash is now', cash)


					#if lasttrend != 'downtrend':
					lastbuyprice = buyprice
					startprice = buyprice
					trend = 'uptrend'
					profitfault = 0
					rebalancing = 0
					firstbuyskip = True
					startorder = False
					peakprice = None
					buytime = False
					lasttrend = 'downtrend'
					print('-=-=-=-=-=-=-=-==-= End of buy cycle2 =-=-=-=-=-=-=-=-==-\n')
					time.sleep(cycletime)
					continue
			print('Pair is:', pair)

			# Start buy order
			if checkbal > float(1.0):
				maxqty = Orders.maxusquantity(checkbal, orderbook['askPrice'], pairinfo)
			else:
				maxqty = checkbal / float(Binancewebsocket.btcres_array[0]['p'])

			maxqty = Orders.lotamount(float(maxqty), pairinfo)
			maxqty = float(maxqty)
			#print('Max quantity is', maxqty, ' for buy order')

			if mode == 'testing':
				print('Would have placed buy order here')
			print('Bought back in at:', orderbook['askPrice'],'\n')
			buyprice = float(orderbook['askPrice'])

			# Wait till order has been filled
			if mode == 'live':
				order = client.order_limit_buy(symbol=pair, quantity=maxqty, price=orderbook['askPrice'])
				while True:
					checkorder = Orders.checkorderstatus(pair, order['orderId'])
					if checkorder == "FILLED":
						print('Buy order has gone through')
						if startorder is True or lastsellprice is None:
							print('Startorder was true or lastprice was none. Setting lastbuyprice')
							pass
						elif lasttrend != 'downtrend':
							pricediff = Balance.profit_calculator(lastsellprice, buyprice)
							print('price difference is:', abs(pricediff))
							print('Maxqty was', maxqty)
							btc_after_fees = Balance.us_value_in_btc(maxqty, buyprice)
							realprofit = abs(pricediff) * btc_after_fees
							print('Realprofit is:', realprofit)
							btc = Balance.assetbalance(asset1)
							realprofit = btc * realprofit
							if buyprice > lastsellprice:
								cash = checkbal - abs(realprofit)
								print(Fore.RED + 'last sell price was', lastsellprice)
								print(Fore.RED + 'bought for', buyprice, 'and lost', Balance.format(realprofit),
								      'profit')
								print(Fore.RED + 'Cash', Balance.format(cash))
							else:
								cash = checkbal + abs(realprofit)
								print(Fore.GREEN + 'last sell price was', lastsellprice)
								print(Fore.GREEN + 'bought for', buyprice, 'and made ', Balance.format(realprofit),
								      'profit')
								print(Fore.GREEN + 'Cash is now:', cash)
								playsound('Cheering.mp3')
							print('Total cash is now', cash)
						lastbuyprice = buyprice
						startorder = False
						break
					else:
						# print('Not filled yet')
						if float(Binancewebsocket.btcres_array[0]['p']) > float(order['price']) + (
								(float(order['price']) * 0.2) / 100):
							print('Price went too far up')
							Orders.cancelorder(pair, order['orderId'])
							break
						time.sleep(2)
			if mode == 'testing':
				if startorder is True or lastsellprice is None:
					print('Startorder was true or lastprice was none. Setting lastbuyprice')
					pass
				elif lasttrend != 'downtrend':
					pricediff = Balance.profit_calculator(lastsellprice, buyprice)
					print('price difference is:', abs(pricediff))
					btc_after_fees = Balance.us_value_in_btc(cash, pairprice)
					realprofit = abs(pricediff) * btc_after_fees
					print('Realprofit is:', realprofit)
					if buyprice > lastsellprice:
						cash = cash - abs(realprofit)
						print(Fore.RED + 'last sell price was', lastsellprice)
						print(Fore.RED + 'bought for', buyprice, 'and lost', Balance.format(realprofit), 'profit')
						print(Fore.RED + 'Cash', Balance.format(cash))


					else:
						cash = cash + abs(realprofit)
						print(Fore.GREEN + 'last sell price was', lastsellprice)
						print(Fore.GREEN + 'bought for', buyprice, 'and made ', Balance.format(realprofit), 'profit')
						print(Fore.GREEN + 'Cash is now:', cash)
					print('Total cash is now', cash)

			#if lasttrend != 'downtrend':
			lastbuyprice = buyprice
			startprice = buyprice
			trend = 'uptrend'
			firstbuyskip = True
			profitfault = 0
			rebalancing = 0
			startorder = False
			peakprice = None
			buytime = False
			lasttrend = 'downtrend'
			print('-=-=-=-=-=-=-=-==-= End of buy cycle3 =-=-=-=-=-=-=-=-==-\n')
			time.sleep(cycletime)
			continue
		except BinanceAPIException as e:
			print(e.status_code)
			print(e.message)
			continue


	elif selltime is True:
		try:
			print('\n\nTime To place sell order')
			print('-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\n')
			print('Start price is:', startprice)
			print('Peak price is', peakprice)
			print('Peakprice difference is', abs(startprice - peakprice))
			print('Pair price is', pairprice)
			print('final price to sell right now is:', ordertime)
			attime = time.strftime('%X %x %Z')
			print(attime)

			orderbook = client.get_orderbook_ticker(symbol=pair)

			#Check for enough Quantity
			checkbal = float(Orders.maxcoinquantity(asset1))
			#print(asset1, ' balance is', checkbal)
			if pairprice >= 1:
				finalbal = float(checkbal) * float(pairprice)
				if finalbal < Balance.minNotional(pairinfo):
					print('Not enough balance to sell at',pairprice,', Starting cycle over\n')
					sellprice = float(orderbook['bidPrice'])

					if mode == 'testing':
						if startorder is True or lastbuyprice is None:
							print('Startorder was true or lastprice was none. Setting lastsellprice')
							pass
						elif lasttrend != 'uptrend':
							pricediff = Balance.profit_calculator(lastbuyprice, sellprice)
							print('price difference is:', abs(pricediff))
							btc_after_fees = Balance.btc_value_after_fees(checkbal)
							realprofit = abs(pricediff) * btc_after_fees
							print('Realprofit is:', realprofit)
							if sellprice < lastbuyprice:
								cash = cash - abs(realprofit)
								print(Fore.RED + 'last buy price was', lastbuyprice)
								print(Fore.RED + 'bought for', sellprice, 'and lost', Balance.format(realprofit),
								      'profit')
								print(Fore.RED + 'Cash', Balance.format(cash))


							else:
								cash = cash + abs(realprofit)
								print(Fore.GREEN + 'last buy price was', lastbuyprice)
								print(Fore.GREEN + 'sold for', sellprice, 'and made ', Balance.format(realprofit),
								      'profit')
								print(Fore.GREEN + 'Cash is now:', cash)
							print('Total cash is now', cash)


					#if lasttrend != 'uptrend':
					lastsellprice = sellprice
					startprice = sellprice
					trend = 'downtrend'
					profitfault = 0
					rebalancing = 0
					firstsellskip = True
					startorder = False
					peakprice = None
					selltime = False
					lasttrend = 'uptrend'
					print('-=-=-=-=-=-=-=-==-= End of sell cycle1 =-=-=-=-=-=-=-=-==-\n')
					time.sleep(cycletime)
					continue
				else:
					finalbal = checkbal
			else:
				if checkbal < Balance.minNotional(pairinfo):
					print('Not enough balance to sell at',pairprice,', Starting cycle over\n')
					sellprice = float(orderbook['bidPrice'])

					if mode == 'testing':
						if startorder is True or lastbuyprice is None:
							print('Startorder was true or lastprice was none. Setting lastsellprice')
							pass
						elif lasttrend != 'uptrend':
							pricediff = Balance.profit_calculator(lastbuyprice, sellprice)
							print('price difference is:', abs(pricediff))
							btc_after_fees = Balance.btc_value_after_fees(checkbal)
							realprofit = abs(pricediff) * btc_after_fees
							print('Realprofit is:', realprofit)
							if sellprice < lastbuyprice:
								cash = cash - abs(realprofit)
								print(Fore.RED + 'last buy price was', lastbuyprice)
								print(Fore.RED + 'bought for', sellprice, 'and lost', Balance.format(realprofit),
								      'profit')
								print(Fore.RED + 'Cash', Balance.format(cash))


							else:
								cash = cash + abs(realprofit)
								print(Fore.GREEN + 'last buy price was', lastbuyprice)
								print(Fore.GREEN + 'sold for', sellprice, 'and made ', Balance.format(realprofit),
								      'profit')
								print(Fore.GREEN + 'Cash is now:', cash)
							print('Total cash is now', cash)


					#if lasttrend != 'uptrend':
					lastsellprice = sellprice
					startprice = sellprice
					trend = 'downtrend'
					firstsellskip = True
					profitfault = 0
					rebalancing = 0
					startorder = False
					peakprice = None
					selltime = False
					lasttrend = 'uptrend'
					print('-=-=-=-=-=-=-=-==-= End of sell cycle2 =-=-=-=-=-=-=-=-==-\n')
					time.sleep(cycletime)
					continue
				else:
					finalbal = checkbal

			maxqty = finalbal
			maxqty = Orders.lotamount(float(maxqty), pairinfo)
			if mode == 'testing':
				print('Would have placed sell order here')
			print('Sold out at:', orderbook['bidPrice'],'\n')
			sellprice = float(orderbook['bidPrice'])

			# Check order to be filled
			if mode == 'live':
				order = client.order_limit_sell(symbol=pair, quantity=maxqty, price=orderbook['bidPrice'])
				while True:
					checkorder = Orders.checkorderstatus(pair, order['orderId'])
					if checkorder == "FILLED":
						print('Sell order has gone through')
						if startorder is True or lastbuyprice is None:
							print('Startorder was true or lastprice was none. Setting lastsellprice')
							pass
						elif lasttrend != 'uptrend':
							pricediff = Balance.profit_calculator(lastbuyprice, sellprice)
							print('price difference is:', abs(pricediff))
							print('Maxqty was', maxqty)
							btc_after_fees = Balance.btc_value_after_fees(maxqty)
							realprofit = abs(pricediff) * btc_after_fees
							print('Realprofit is:', realprofit)
							checkbal = float(Balance.assetbalance(asset2))
							if sellprice < lastbuyprice:
								cash = checkbal - abs(realprofit)
								print(Fore.RED + 'last buy price was', lastbuyprice)
								print(Fore.RED + 'bought for', sellprice, 'and lost', Balance.format(realprofit),
								      'profit')
								print(Fore.RED + 'Cash', Balance.format(cash))
								playsound('fail.mp3')


							else:
								cash = checkbal + abs(realprofit)
								print(Fore.GREEN + 'last buy price was', lastbuyprice)
								print(Fore.GREEN + 'sold for', sellprice, 'and made ', Balance.format(realprofit),
								      'profit')
								print(Fore.GREEN + 'Cash is now:', cash)
								playsound('Cheering.mp3')
							print('Total cash is now', cash)

						lastsellprice = sellprice
						startorder = False
						break
					else:
						#print('Not filled yet')
						if float(Binancewebsocket.btcres_array[0]['p']) < float(order['price']) - ((float(order['price']) * 0.2) / 100):
							print('Price went too far down')
							Orders.cancelorder(pair, order['orderId'])
							break
						time.sleep(2)

			if mode == 'testing':
				if startorder is True or lastbuyprice is None:
					print('Startorder was true or lastprice was none. Setting lastsellprice')
					pass
				elif lasttrend != 'uptrend':
					pricediff = Balance.profit_calculator(lastbuyprice, sellprice)
					print('price difference is:', abs(pricediff))
					btc_after_fees = Balance.btc_value_after_fees(checkbal)
					realprofit = abs(pricediff) * btc_after_fees
					print('Realprofit is:', realprofit)
					if sellprice < lastbuyprice:
						cash = cash - abs(realprofit)
						print(Fore.RED + 'last buy price was', lastbuyprice)
						print(Fore.RED + 'bought for', sellprice, 'and lost', Balance.format(realprofit),
						      'profit')
						print(Fore.RED + 'Cash', Balance.format(cash))


					else:
						cash = cash + abs(realprofit)
						print(Fore.GREEN + 'last buy price was', lastbuyprice)
						print(Fore.GREEN + 'sold for', sellprice, 'and made ', Balance.format(realprofit),
						      'profit')
						print(Fore.GREEN + 'Cash is now:', cash)
					print('Total cash is now', cash)

			#if lasttrend != 'uptrend':
			lastsellprice = sellprice
			startprice = sellprice
			trend = 'downtrend'
			firstsellskip = True
			profitfault = 0
			rebalancing = 0
			startorder = False
			peakprice = None
			selltime = False
			lasttrend = 'uptrend'
			print('-=-=-=-=-=-=-=-==-= End of sell cycle3 =-=-=-=-=-=-=-=-==-\n')
			time.sleep(cycletime)
			continue
		except BinanceAPIException as e:
			print(e.status_code)
			print(e.message)
			continue

	time.sleep(waittime)

