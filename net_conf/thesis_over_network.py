#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch, Host
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import tkinter as tk
from tkinter import simpledialog

def create_network():
    # Set the bandwidth
    bw = 5  # You can change this value as needed

    # Create network
    net = Mininet(topo=None, build=False, ipBase='10.0.0.0/8')

    # Add controller
    c0 = net.addController(name='c0', controller=RemoteController, ip='10.203.0.206', port=6633)

    # Add switches
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)

    # Add hosts
    hosts = [net.addHost('h1', cls=Host, ip='10.203.0.207', defaultRoute=None)]
    hosts.extend(net.addHost(f'h{i}', cls=Host, ip=f'10.0.0.{i}', defaultRoute=None) for i in range(2, 5))

    # Add links
    net.addLink(hosts[0], s1, cls=TCLink)
    net.addLink(hosts[1], s2, cls=TCLink)
    net.addLink(s1, s2, cls=TCLink)  # Use the user-provided bandwidth
    net.addLink(s2, hosts[3], cls=TCLink)
    net.addLink(s1, hosts[2], cls=TCLink)

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

def main():
    setLogLevel('info')
    create_network()

if __name__ == '__main__':
    main()