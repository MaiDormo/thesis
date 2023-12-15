#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call

def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')

    info( '*** Adding controller\n' )
    c0 = net.addController(name='c0', controller=RemoteController, ip='192.168.56.7', port=6633)


    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)

    info( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)

    info( '*** Add links\n')
    net.addLink(h1, s1)
    
    # Add link without bandwidth limit and delay
    # net.addLink(h2, s1)

    #------------------REAL WORLD DELAY------------------

    # Add link with bandwith limit of 10 Mbps and delay of 5 ms
    # net.addLink(h2, s1, cls=TCLink, bw=10, delay='5ms')

    # Add link with bandwith limit of 5 Mbps and delay of 5 ms
    # net.addLink(h2, s1, cls=TCLink, bw=5, delay='5ms')

    # Add link with bandwith limit of 2.5 Mbps and delay of 5 ms
    # net.addLink(h2, s1, cls=TCLink, bw=2.5, delay='5ms')

    # Add link with bandwith limit of 1 Mbps and delay of 5 ms
    net.addLink(h2, s1, cls=TCLink, bw=1, delay='5ms')

    #------------------WORST CASE DELAY------------------

    # Add link with bandwith limit of 10 Mbps and delay of 200 ms
    # net.addLink(h2, s1, cls=TCLink, bw=10, delay='200ms')

    # Add link with bandwith limit of 5 Mbps and delay of 200 ms
    # net.addLink(h2, s1, cls=TCLink, bw=5, delay='200ms')

    # Add link with bandwith limit of 2.5 Mbps and delay of 200 ms
    # net.addLink(h2, s1, cls=TCLink, bw=2.5, delay='200ms')

    # Add link with bandwith limit of 1 Mbps and delay of 200 ms
    # net.addLink(h2, s1, cls=TCLink, bw=1, delay='200ms')

    #------------------PACKET DROPS MINIMAL------------------

    # Add link with bandwith limit of 10 Mbps and delay of 5 ms and packet loss of 0.1%
    # net.addLink(h2, s1, cls=TCLink, bw=10, delay='5ms', loss=0.1)

    # Add link with bandwith limit of 5 Mbps and delay of 5 ms and packet loss of 0.1%
    # net.addLink(h2, s1, cls=TCLink, bw=5, delay='5ms', loss=0.1)

    # Add link with bandwith limit of 2.5 Mbps and delay of 5 ms and packet loss of 0.1%
    # net.addLink(h2, s1, cls=TCLink, bw=2.5, delay='5ms', loss=0.1)

    # Add link with bandwith limit of 1 Mbps and delay of 5 ms and packet loss of 0.1%
    # net.addLink(h2, s1, cls=TCLink, bw=1, delay='5ms', loss=0.1)

    #------------------PACKET DROPS MAXIMAL------------------

    # Add link with bandwith limit of 10 Mbps and delay of 5 ms and packet loss of 10%
    # net.addLink(h2, s1, cls=TCLink, bw=10, delay='5ms', loss=10)

    # Add link with bandwith limit of 5 Mbps and delay of 5 ms and packet loss of 10%
    # net.addLink(h2, s1, cls=TCLink, bw=5, delay='5ms', loss=10)

    # Add link with bandwith limit of 2.5 Mbps and delay of 5 ms and packet loss of 10%
    # net.addLink(h2, s1, cls=TCLink, bw=2.5, delay='5ms', loss=10)

    # Add link with bandwith limit of 1 Mbps and delay of 5 ms and packet loss of 10%
    # net.addLink(h2, s1, cls=TCLink, bw=1, delay='5ms', loss=10)



    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s1').start([c0])

    info( '*** Post configure switches and hosts\n')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()


