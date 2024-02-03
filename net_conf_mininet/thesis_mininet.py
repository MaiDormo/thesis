#!/usr/bin/env python

import argparse
from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch, Host
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Network Parameters')
    parser.add_argument('--bw', type=int, required=True, help='Bandwidth')
    parser.add_argument('--delay', type=str, required=True, help='Delay')
    parser.add_argument('--loss', type=int, required=True, help='Loss')
    args = parser.parse_args()

    setLogLevel('info')
    create_network(args.bw, args.delay, args.loss)

def create_network(bw, delay, loss):
    # Create network
    net = Mininet(topo=None, build=False, ipBase='10.0.0.0/8')

    # Add controller
    c0 = net.addController(name='c0', controller=RemoteController, ip='192.168.56.9', port=6633)

    # Add switches
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)

    # Add hosts
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)

    # Add links
    net.addLink(h1, s1, cls=TCLink)
    net.addLink(h2, s2, cls=TCLink)

    # Add link with parameters from command-line arguments
    net.addLink(s1, s2, cls=TCLink, bw=bw, delay=delay+'ms', loss=loss)

    # Start network
    net.build()

    # Start controllers
    for controller in net.controllers:
        controller.start()

    # Start switches
    for switch in [s1, s2]:
        switch.start([c0])

    # Start CLI and stop network
    CLI(net)
    net.stop()

if __name__ == '__main__':
    main()