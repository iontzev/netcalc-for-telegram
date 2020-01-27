import ipaddress

class Ip():
        
    def getPrefix(self, text):
        if text[0:1] == '.': # в виде netmask_part
            netmask_raw = text[1:]
            netmask = ''
            netmask_list = netmask_raw.split('.')
            for i in range(4-len(netmask_list)):
                netmask = '255.' + netmask
            netmask = netmask + netmask_raw
            return netmask
        elif text.isdigit():
            if int(text) > 32 or int(text) == 0:
                netmask_raw = text
                netmask = ''
                netmask_list = netmask_raw.split('.')
                for i in range(4-len(netmask_list)):
                    netmask = '255.' + netmask
                netmask = netmask + netmask_raw
                return netmask
            else:
                return text
        else:
            return text

    def getAddress(self, text):
        if text[:1] == '/': # netmask or prefix
            prefix = self.getPrefix(text[1:])
            ip = '192.168.0.0'
            try:
                address = { 'omitted_octets': 4,
                            'address':'/{prefix}'.format(prefix=prefix),
                            'network': ipaddress.ip_network('{ip}/{prefix}'.format(ip=ip, prefix=prefix), strict=False)
                            }
            except:
                address = False
        else: # ip(or part)/netmask(or prefix)
            text_split = text.split('/')
            address = False
            if len(text_split) == 2:
                ip = text_split[0]
                omitted_octets = 0
                prefix = self.getPrefix(text_split[1])
                ip_parts = ip.split('.')
                masked_ip=ip
                if len(ip_parts) == 1:
                    ip='192.168.0.{}'.format(ip_parts[0])
                    masked_ip='XXX.YYY.ZZZ.{}'.format(ip_parts[0])
                    omitted_octets = 3
                elif len(ip_parts) == 2:
                    ip='192.168.{}.{}'.format(ip_parts[0], ip_parts[1])
                    masked_ip='XXX.YYY.{}.{}'.format(ip_parts[0], ip_parts[1])
                    omitted_octets = 2
                elif len(ip_parts) == 3:
                    ip='192.{}.{}.{}'.format(ip_parts[0], ip_parts[1], ip_parts[2])
                    masked_ip='XXX.{}.{}.{}'.format(ip_parts[0], ip_parts[1], ip_parts[2])
                    omitted_octets = 1
                try:
                    address = { 'omitted_octets': omitted_octets,
                                'address': '{ip}'.format(ip=masked_ip),
                                'network': ipaddress.ip_network('{ip}/{prefix}'.format(ip=ip, prefix=prefix), strict=False)
                                }
                except:
                    address = False

        return address

    def getInfo(self, address):
        net = address['network']
        address['info'] = {'prefix': net.prefixlen,
                            'netmask': net.netmask,
                            'wildcard': net.hostmask,
                            'network_address': net.network_address,
                            'broadcast_address': net.broadcast_address,
                            'hosts': max(net.num_addresses-2,0)}
        return address


    def getAnswer(self, info):
        net = info['info']
        if info['omitted_octets'] == 4: # netmask or prefix
            answer  = 'prefix - {}\n'.format(net['prefix'])
            answer += 'netmask - {}\n'.format(net['netmask'])
            answer += 'wildcard - {}\n'.format(net['wildcard'])
            answer += 'количество хостов - {}\n'.format(net['hosts'])

        else: # ip-address with netmask
            if info['omitted_octets'] * 8 > net['prefix']:
                return 'недостаточно данных. возможно слишком короткий префикс'
            answer  = 'IP-адрес - {}/{}\n'.format(info['address'], net['prefix'])
            answer += 'prefix - {}\n'.format(net['prefix'])
            answer += 'netmask - {}\n'.format(net['netmask'])
            answer += 'wildcard - {}\n'.format(net['wildcard'])
            broadcast_parts = str(net['broadcast_address']).split('.')
            network_parts = str(net['network_address']).split('.')
            if info['omitted_octets'] == 3:
                answer += 'адрес сети - XXX.YYY.ZZZ.{}\n'.format(network_parts[3])
                answer += 'broadcast - XXX.YYY.ZZZ.{}\n'.format(broadcast_parts[3])
            if info['omitted_octets'] == 2:
                answer += 'адрес сети - XXX.YYY.{}.{}\n'.format(network_parts[2], network_parts[3])
                answer += 'broadcast - XXX.YYY.{}.{}\n'.format(broadcast_parts[2], broadcast_parts[3])
            if info['omitted_octets'] == 1:
                answer += 'адрес сети - XXX.{}.{}.{}\n'.format(network_parts[1], network_parts[2], network_parts[3])
                answer += 'broadcast - XXX.{}.{}.{}\n'.format(broadcast_parts[1], broadcast_parts[2], broadcast_parts[3])
            if info['omitted_octets'] == 0:
                answer += 'адрес сети - {}\n'.format(net['network_address'])
                answer += 'broadcast - {}\n'.format(net['broadcast_address'])
            answer += 'количество хостов - {}\n'.format(net['hosts'])
        return answer

    def sumNetworks(self, network_list):
        if len(network_list) == 1:
            return network_list[0]
        else:
            base_network = network_list[0]
            base_prefix = base_network.prefixlen
            for new_prefix in range(base_prefix, -1, -1):
                new_network = base_network.supernet(new_prefix=new_prefix)
                print('test', new_network)
                for network in network_list:
                    print('compare with', network)
                    if not network.subnet_of(new_network):
                        break
                else:
                    return new_network
            return base_network
            
    def divNetworks(self, network, prefixlen_diff=1):
        networks = network['network'].subnets(prefixlen_diff=prefixlen_diff)
        answer = []
        for net in networks:
            ip_parts = str(net.network_address).split('.')
            if network['omitted_octets'] == 3:
                answer.append({'network': 'XXX.YYY.ZZZ.{}'.format(ip_parts[3]) + '/' + str(net.prefixlen)})
            if network['omitted_octets'] == 2:
                answer.append({'network': 'XXX.YYY.{}.{}'.format(ip_parts[2], ip_parts[3]) + '/' + str(net.prefixlen)})
            if network['omitted_octets'] == 1:
                answer.append({'network': 'XXX.{}.{}.{}'.format(ip_parts[1], ip_parts[2], ip_parts[3]) + '/' + str(net.prefixlen)})
            if network['omitted_octets'] == 0:
                answer.append({'network': str(net.network_address) + '/' + str(net.prefixlen)})
        return answer


