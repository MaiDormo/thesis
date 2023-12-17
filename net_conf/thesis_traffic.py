#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch, Host
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import tkinter as tk
from tkinter import simpledialog

def create_network():
    # Create a Tkinter root window (without displaying it)
    root = tk.Tk()
    root.withdraw()

    # Ask the user for the bandwidth
    bw = simpledialog.askinteger("Input", "Enter the bandwidth (3, 5, or 10):", parent=root, minvalue=3, maxvalue=10)

    # Create network
    net = Mininet(topo=None, build=False, ipBase='10.0.0.0/8')

    # Add controller
    c0 = net.addController(name='c0', controller=RemoteController, ip='192.168.56.7', port=6633)

    # Add switches
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)

    # Add hosts
    hosts = []
    for i in range(1, 5):
        host = net.addHost(f'h{i}', cls=Host, ip=f'10.0.0.{i}', defaultRoute=None)
        hosts.append(host)

    # Add links
    net.addLink(hosts[0], s1, cls=TCLink, delay='5ms')
    net.addLink(hosts[1], s2, cls=TCLink, delay='5ms')
    net.addLink(s1, s2, cls=TCLink, bw=bw, delay='5ms')  # Use the user-provided bandwidth
    net.addLink(s2, hosts[3], cls=TCLink, delay='5ms')
    net.addLink(s1, hosts[2], cls=TCLink, delay='5ms')

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