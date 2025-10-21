#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel

class LinuxRouter(Node):
    "Node that acts as a router."
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl -w net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()

class MyTopo(Topo):
    def build(self):
        # Add routers
        r1 = self.addNode('r1', cls=LinuxRouter, ip='10.0.0.1/24')
        r2 = self.addNode('r2', cls=LinuxRouter, ip='10.0.1.2/24')
        r3 = self.addNode('r3', cls=LinuxRouter, ip='10.0.3.2/24')

        # Add hosts
        h1 = self.addHost('h1', ip='10.0.0.2/24', defaultRoute='via 10.0.0.1')
        h2 = self.addHost('h2', ip='10.0.2.2/24', defaultRoute='via 10.0.2.1')
        h3 = self.addHost('h3', ip='10.0.4.2/24', defaultRoute='via 10.0.4.1')

        # Link hosts ke router
        self.addLink(h1, r1, intfName2='r1-eth0', params2={'ip': '10.0.0.1/24'})
        self.addLink(h2, r2, intfName2='r2-eth1', params2={'ip': '10.0.2.1/24'})
        self.addLink(h3, r3, intfName2='r3-eth1', params2={'ip': '10.0.4.1/24'})

        # Link antar router
        self.addLink(r1, r2,
                     intfName1='r1-eth1', params1={'ip': '10.0.1.1/24'},
                     intfName2='r2-eth0', params2={'ip': '10.0.1.2/24'})

        self.addLink(r2, r3,
                     intfName1='r2-eth2', params1={'ip': '10.0.3.1/24'},
                     intfName2='r3-eth0', params2={'ip': '10.0.3.2/24'})

def run():
    topo = MyTopo()
    net = Mininet(topo=topo, link=TCLink)
    net.start()

    # Tambahkan routing statis
    r1 = net.get('r1')
    r2 = net.get('r2')
    r3 = net.get('r3')

    r1.cmd('ip route add 10.0.2.0/24 via 10.0.1.2')
    r1.cmd('ip route add 10.0.3.0/24 via 10.0.1.2')
    r1.cmd('ip route add 10.0.4.0/24 via 10.0.1.2')

    r2.cmd('ip route add 10.0.0.0/24 via 10.0.1.1')
    r2.cmd('ip route add 10.0.4.0/24 via 10.0.3.2')

    r3.cmd('ip route add 10.0.0.0/24 via 10.0.3.1')
    r3.cmd('ip route add 10.0.2.0/24 via 10.0.3.1')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
