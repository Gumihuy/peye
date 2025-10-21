#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info


class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl -w net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class MyTopo(Topo):
    def build(self):
        # Router
        r1 = self.addNode('r1', cls=LinuxRouter, ip='10.0.0.1/24')
        r2 = self.addNode('r2', cls=LinuxRouter, ip='10.0.2.1/24')
        r3 = self.addNode('r3', cls=LinuxRouter, ip='10.0.4.1/24')

        # Host
        h1 = self.addHost('h1', ip='10.0.0.2/24', defaultRoute='via 10.0.0.1')
        h2 = self.addHost('h2', ip='10.0.2.2/24', defaultRoute='via 10.0.2.1')
        h3 = self.addHost('h3', ip='10.0.4.2/24', defaultRoute='via 10.0.4.1')

        # Koneksi host-router
        self.addLink(h1, r1, intfName2='r1-eth0', params2={'ip': '10.0.0.1/24'})
        self.addLink(h2, r2, intfName2='r2-eth1', params2={'ip': '10.0.2.1/24'})
        self.addLink(h3, r3, intfName2='r3-eth1', params2={'ip': '10.0.4.1/24'})

        # Koneksi antar router
        self.addLink(r1, r2,
                     intfName1='r1-eth1', params1={'ip': '10.0.1.1/30'},
                     intfName2='r2-eth0', params2={'ip': '10.0.1.2/30'})
        self.addLink(r2, r3,
                     intfName1='r2-eth2', params1={'ip': '10.0.3.1/30'},
                     intfName2='r3-eth0', params2={'ip': '10.0.3.2/30'})


def run():
    topo = MyTopo()
    net = Mininet(topo=topo, link=TCLink, controller=None)
    net.start()

    info('\n*** Setting Routing Antar Router ***\n')
    r1, r2, r3 = net['r1'], net['r2'], net['r3']

    # Routing antar router
    r1.cmd('ip route add 10.0.2.0/24 via 10.0.1.2')
    r1.cmd('ip route add 10.0.3.0/30 via 10.0.1.2')
    r1.cmd('ip route add 10.0.4.0/24 via 10.0.1.2')

    r2.cmd('ip route add 10.0.0.0/24 via 10.0.1.1')
    r2.cmd('ip route add 10.0.4.0/24 via 10.0.3.2')

    r3.cmd('ip route add 10.0.0.0/24 via 10.0.3.1')
    r3.cmd('ip route add 10.0.2.0/24 via 10.0.3.1')

    info('\n*** Tes koneksi dari h1 ke h2 dan h3 ***\n')
    h1 = net['h1']
    h1.cmdPrint('ping -c 2 10.0.2.2')
    h1.cmdPrint('ping -c 2 10.0.4.2')

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
