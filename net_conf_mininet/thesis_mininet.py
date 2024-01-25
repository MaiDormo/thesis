#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch, Host
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink
from tkinter import Tk, Label, Entry, Button, StringVar, ttk

def main():
    setLogLevel('info')
    create_network()

def create_network():
    # Create network
    net = Mininet(topo=None, build=False, ipBase='10.0.0.0/8')

    # Add controller
    c0 = net.addController(name='c0', controller=RemoteController, ip='192.168.56.7', port=6633)

    # Add switches
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)

    # Add hosts
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)

    # Add links
    net.addLink(h1, s1, cls=TCLink)
    net.addLink(h2, s2, cls=TCLink)

# Create GUI for inputting link parameters
    root = Tk()
    root.title("Network Parameters")

    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=('N', 'W', 'E', 'S'))
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    bw = StringVar()
    delay = StringVar()
    loss = StringVar()

    ttk.Label(mainframe, text="Bandwidth").grid(column=1, row=1, sticky=('W', 'E'))
    bw_entry = ttk.Entry(mainframe, width=7, textvariable=bw)
    bw_entry.grid(column=2, row=1, sticky=('W', 'E'))

    ttk.Label(mainframe, text="Delay").grid(column=1, row=2, sticky=('W', 'E'))
    delay_entry = ttk.Entry(mainframe, width=7, textvariable=delay)
    delay_entry.grid(column=2, row=2, sticky=('W', 'E'))

    ttk.Label(mainframe, text="Loss").grid(column=1, row=3, sticky=('W', 'E'))
    loss_entry = ttk.Entry(mainframe, width=7, textvariable=loss)
    loss_entry.grid(column=2, row=3, sticky=('W', 'E'))

    ttk.Button(mainframe, text="Submit", command=root.quit).grid(column=2, row=4, sticky='W')

    for child in mainframe.winfo_children(): 
        child.grid_configure(padx=5, pady=5)

    bw_entry.focus()
    root.bind('<Return>', lambda e: root.quit())

    root.mainloop()

    # Add link with parameters from GUI
    net.addLink(s1, s2, cls=TCLink, bw=int(bw.get()), delay=delay.get()+'ms', loss=int(loss.get()))


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
