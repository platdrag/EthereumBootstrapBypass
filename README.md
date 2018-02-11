# Ethereum Bootstrap Bypass


**A censorship bypass for Ethereum's single point of failure: When bootstrap nodes gets blocked**


Ethereum's wire protocol is built on [DevP2p](https://github.com/ethereum/wiki/wiki/%C3%90%CE%9EVp2p-Wire-Protocol) over [RPLx](https://github.com/ethereum/devp2p/blob/master/rlpx.md), a cryptographic peer-to-peer network and protocol suite. 

The protocol is using bootstrap nodes to initialize the p2p network by getting you the first nodes to connect to. 
Node discovery and network formation are implemented via a kademlia-like UDP. For bootstrap, each client uses built in bootstrap nodes which indicates the node to other nodes available to connect to.

Bootstrap nodes are embedded in the ethereum clients. For [Geth](https://github.com/ethereum/go-ethereum/tree/b4e05adcc7c40e7f77839bad350df625094940ed), there are 6 ip addresses [hard coded](https://github.com/ethereum/go-ethereum/blob/b4e05adcc7c40e7f77839bad350df625094940ed/params/bootnodes.go) into the binary.
For [parity](https://github.com/paritytech/parity), there are 17 in a [config file](https://github.com/paritytech/parity/blob/b50fb71dd1d29dfde2a6c7e1830447cf30896c31/ethcore/res/ethereum/foundation.json).


Since there are only a few bootstrap nodes, **this is a big single point of failure for censoring Ethereum**. A firewall / ISP blocking these Ip/ports will render a vanilla node unable to find any peers and therefore cannot connect to the Ethereum network.

Simulating a blocked node is easy. just follow these steps:
1. make sure the data direcrory for geth is empty in order to start a vanilla node:

 `rm -rf ~/.ethereum/` 

2. Block bootstrap nodes in iptables:

``` -A OUTPUT -d 52.16.188.185 -j DROP
iptables -A OUTPUT -d 13.93.211.84 -j DROP
iptables -A OUTPUT -d 191.235.84.50 -j DROP
iptables -A OUTPUT -d 13.75.154.138 -j DROP
iptables -A OUTPUT -d 52.74.57.123 -j DROP
iptables -A OUTPUT -d 5.1.83.226 -j DROP
```
3. run Geth

`./geth`

Geth does not progress after initial init. Now lets watch iptables and confirm that geth attempts to send packets and gets blocked:

`watch -n 2 -d iptables -nvL`

![iptables blocking ips](https://github.com/platdrag/EthereumBootstrapBypass/blob/master/img/iptables.gif?raw=true)

### What can be done?

The solution is basically to find at least one Ethereum node for our vanilla node to connect to. Once found, the nodes will start to gossiping between themselves, telling each other about other nodes they know about.

This can be done manually by connecting to a running geth with a console: 

`./geth attach` 

and add the enode url:

`web3.admin.addPeer('enode://03cac0e580a8dcfdd9e63d27efbb4f13f0de42cff18fb0d0c11a0c4332388dc6de84cadb88d357f2026414fb6e5753a8230c4b448f835c4c334888f474989f7a@39.104.104.43:30303')`

This will trigger asynchronous attempt to connect that peer. Since not all nodes will connect with you node, we need to try a few nodes untill success. This is where our little script come in.

The script will download a recent list of all Ethereum nodes from [ethernodes.org](https://ethernodes.org/network/1), and add them to a running Geth instance one at the time. It will keep adding peers until a peer is successfully connected. Geth node will take it from there ;)



### Running EthereumBootstrapBypass

```
usage: etherBootStrapBypass.py [-h] nodeRpcUrl localFileCache

positional arguments:
  nodeRpcUrl      RPC Url for an Geth node
  localFileCache  local file path to save cached node data
  ```
  

example:

`python3 ./etherBootStrapBypass.py http://localhost:8546 ./nodes.list`


#### Dependencies 
```
python3
web3
```


