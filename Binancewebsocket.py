import config
from binance.websockets import BinanceSocketManager
from Balance import *
import time
from binance.enums import *

bm = BinanceSocketManager(config.bclient)

btcres_array = []
ltcres_array = []
bccres_array = []
bnbres_array = []
neores_array = []
ethres_array = []
adxres_array = []
klinesocket = []

closing = []

count = 0
FIXED_SIZE = 200
movingarray = 30

def movingaverage(pair, interval):
	#Get Closing Klines for Moving Average
	candles = client.get_klines(symbol=pair, interval=interval)
	for prices in candles:
		closing.insert(0, float(prices[4]))
		if len(closing) > movingarray:
			del closing[-1]
	return closing

def btcprocess_message(msg):
	global btcres_array, bm
	if msg['e'] == 'error':
		print('Error msg:',msg['e'])
		bm.close()
		time.sleep(1)
		initiate()
	else:
		# Insert at first position
		btcres_array.insert(0, msg)
		if len(btcres_array) > FIXED_SIZE:
			# Remove last message when btcres_array size is > of FIXED_SIZE
			del btcres_array[-1]
		return btcres_array #make_post_calculations(btcres_array)

def bccprocess_message(msg):
	global bccres_array, bm
	# Insert at first position
	bccres_array.insert(0, msg)
	if len(bccres_array) > FIXED_SIZE:
		# Remove last message when btcres_array size is > of FIXED_SIZE
		del bccres_array[-1]
	return bccres_array #make_post_calculations(btcres_array)

def ltcprocess_message(msg):
	global ltcres_array, bm
	# Insert at first position
	ltcres_array.insert(0, msg)
	if len(ltcres_array) > FIXED_SIZE:
		# Remove last message when btcres_array size is > of FIXED_SIZE
		del ltcres_array[-1]
	return ltcres_array #make_post_calculations(btcres_array)

def bnbprocess_message(msg):
	global bnbres_array, bm
	# Insert at first position
	bnbres_array.insert(0, msg)
	if len(bnbres_array) > FIXED_SIZE:
		# Remove last message when btcres_array size is > of FIXED_SIZE
		del bnbres_array[-1]
	return bnbres_array #make_post_calculations(btcres_array)

def neoprocess_message(msg):
	global neores_array, bm
	# Insert at first position
	neores_array.insert(0, msg)
	if len(neores_array) > FIXED_SIZE:
		# Remove last message when btcres_array size is > of FIXED_SIZE
		del neores_array[-1]
	return neores_array #make_post_calculations(btcres_array)

def ethprocess_message(msg):
	global ethres_array, bm
	# Insert at first position
	ethres_array.insert(0, msg)
	if len(ethres_array) > FIXED_SIZE:
		# Remove last message when btcres_array size is > of FIXED_SIZE
		del ethres_array[-1]
	return ethres_array #make_post_calculations(btcres_array)

def adxprocess_message(msg):
	global ethres_array, bm
	# Insert at first position
	adxres_array.insert(0, msg)
	if len(adxres_array) > FIXED_SIZE:
		# Remove last message when btcres_array size is > of FIXED_SIZE
		del adxres_array[-1]
	return adxres_array #make_post_calculations(btcres_array)

def kline_socket_stream(msg):
	global klinesocket, bm
	full = 0
	# Insert at first position
	klinesocket.insert(0, msg)
	if len(klinesocket) > FIXED_SIZE:
		# Remove last message when btcres_array size is > of FIXED_SIZE
		del klinesocket[-1]

	return klinesocket  # make_post_calculations(btcres_array)

def averageprice(array):
	pairprice = array
	prices = list()
	for dictionary in pairprice:
		#print(dictionary['p'])
		prices.append(float(dictionary['p']))
	average = sum(prices)/ len(prices)
	average = Balance.format(average)
	#print('There are', len(prices),' in the array')
	#print('The average is:', average)
	return float(average)


def process_m_message(msg):
	print("stream: {} data: {}".format(msg['stream'], msg['data']))

class MessageHandler(object):
	def __getattr__(self, name):
		def method(*args):
			print('Tried to handle method ' + name)
			if args:
				print('It had arguments: ' + str(args))
		return method

def user_socket():
	mh = MessageHandler()
	user_func = getattr(mh, 'user_socket')
	kline_func = getattr(mh, 'kline_socket')
	api_key = config.bkey
	api_secret = config.bsecret
	client = config.bclient
	bm = BinanceSocketManager(config.bclient)
	#kline_key = bm.start_kline_socket('BNBBTC', kline_func, '1m')
	user_key = bm.start_user_socket(user_func)
	bm.start()


def initiate():

	global bm, conn_trade

	# Setup Socket
	bm = BinanceSocketManager(config.bclient)

	# then start the socket manager
	conn_trade = bm.start_trade_socket('BTCUSDT', btcprocess_message)
	conn_tradeeth = bm.start_trade_socket('ETHUSDT', ethprocess_message)
	connaggtrade = bm.start_symbol_ticker_socket('BTCUSDT',bccprocess_message)
	kline_key = bm.start_kline_socket('BTCUSDT',kline_socket_stream, interval='1m')

	# start the socket
	bm.start()
	#time.sleep(82800)
	return conn_trade


def findkeys(node, kv):
	if isinstance(node, list):
		for i in node:
			for x in findkeys(i, kv):
				yield x
	elif isinstance(node, dict):
		if kv in node:
			yield node[kv]
		for j in node.values():
			for x in findkeys(j, kv):
				yield x

initiate()
#user_socket()




