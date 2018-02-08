from Util.LogWrapper import LogWrapper
from web3 import Web3, HTTPProvider
import json,urllib3,os,time,sys


NODE_URL = "https://www.ethernodes.org/network/1/data?draw=2&columns[0][data]=id&columns[0][name]=&columns[0][searchable]=true&columns[0][orderable]=true&columns[0][search][value]=&columns[0][search][regex]=false&columns[1][data]=host&columns[1][name]=&columns[1][searchable]=true&columns[1][orderable]=true&columns[1][search][value]=&columns[1][search][regex]=false&columns[2][data]=port&columns[2][name]=&columns[2][searchable]=true&columns[2][orderable]=true&columns[2][search][value]=&columns[2][search][regex]=false&columns[3][data]=country&columns[3][name]=&columns[3][searchable]=true&columns[3][orderable]=true&columns[3][search][value]=&columns[3][search][regex]=false&columns[4][data]=clientId&columns[4][name]=&columns[4][searchable]=true&columns[4][orderable]=true&columns[4][search][value]=&columns[4][search][regex]=false&columns[5][data]=client&columns[5][name]=&columns[5][searchable]=true&columns[5][orderable]=true&columns[5][search][value]=&columns[5][search][regex]=false&columns[6][data]=clientVersion&columns[6][name]=&columns[6][searchable]=true&columns[6][orderable]=true&columns[6][search][value]=&columns[6][search][regex]=false&columns[7][data]=os&columns[7][name]=&columns[7][searchable]=true&columns[7][orderable]=true&columns[7][search][value]=&columns[7][search][regex]=false&columns[8][data]=lastUpdate&columns[8][name]=&columns[8][searchable]=true&columns[8][orderable]=true&columns[8][search][value]=&columns[8][search][regex]=false&order[0][column]=0&order[0][dir]=asc&start=400&length=100000&search[value]=&search[regex]=false"
l = LogWrapper.getLogger()


def getFileLastModified (file):
	return os.stat(file).st_mtime

def getEthereumNodeList(readFile = None, fileTTLMillies = 24*60*60*1000):
	if readFile and os.path.exists(readFile):
		with open (readFile,encoding='utf-8') as f:
			if time.time() - getFileLastModified(readFile) > fileTTLMillies:
				l.debug('Ether node list is too old. reFetching new one')
				return getEthereumNodeList (readFile = None)
			else:
				nodes = json.load(f)
	else:
		l.debug('Fetching node list from URL')
		http = urllib3.PoolManager()
		response = http.request('GET',NODE_URL,preload_content=True)
		data = response.data.decode('utf-8')
		with open (readFile,'w',encoding='utf-8') as f:
			f.write(data)
		return getEthereumNodeList(readFile,fileTTLMillies)
	
	urls = []
	for node in nodes['data']:
		urls.append('enode://'+node['id']+'@'+node['host']+':'+str(node['port']))
	
	return urls


if __name__ == "__main__":
	import argparse
	
	parser = argparse.ArgumentParser()
	parser.add_argument("nodeRpcUrl", help="RPC Url for an Geth node")
	parser.add_argument("localFileCache", help="local file path to save cached node data")
	args = parser.parse_args()
	
	nodeList = getEthereumNodeList(args.localFileCache)
	l.info("got", len(nodeList),'nodes')
	
	l.info ("connecting to local node", args.nodeRpcUrl)
	web3 = Web3(HTTPProvider(args.nodeRpcUrl))
	
	i=1
	for enode in nodeList:
		l.debug("Adding peer:",enode)
		try:
			web3.admin.addPeer(enode)
		except ValueError as v:
			l.debug('Error with adding node:',enode,'error:',v)
		if i % 20 == 0:
			l.info('waiting for added peers to connect...')
			time.sleep(5)
			peers = web3.admin.peers
			if peers:
				l.info('peers were successfully connected!')
				break
			else:
				l.info("No luck. Adding more nodes")
		i+=1
	l.info('Done! current connected peers:', peers)
	
