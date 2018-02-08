# EthereumBootstrapBypass
A censorship bypass for Ethereum's single point of failure bootstap nodes gets blocked


Ethereum peer discovery protocol is based on the DevP2p, which uses bootstrap nodes in order to initial the p2p network by getting you the first nodes to connect to. 
Bootstrap nodes are embedded in the ethereum client. These Geth, these are 5 ip addresses which are hard coded into the binary.
When a vanilla node is ran on the first time, the node will attempt to contact one of these ip address at the specified port in order to get bootstrapped with an initial list of nodes to connect to.
Since there are only 5 ip address (for Ethereum mainNet), this can be a big single point of failure for censoring Ethereum. If these Ip/port comboes gets blocked by a firewall / ISP, a vanilla node will not be able to find any peers and could not connect to the Ethereum network.
#What can be done?
Well, the problem is basically finding at least one Ethereum node for our vanilla node to connect to. Once found, the nodes will start to gossip between themselves, telling each other about other nodes they know about.
This simple script will download a recent list of all Ethereum nodes from ethernodes.org, and add them to a running Geth instance on at the time. It will keep adding peers untill a peer is successfully connected. Geth node will take it from there ;)

#Running EthereumBootstrapBypass
