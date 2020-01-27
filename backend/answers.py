from ip import Ip
from help import *
import random

class Answers():
    BAD_REQUEST_ANSWER = 'моя твоя не понимай'
    BAD_ANSWER_STICKER_LIST=[   'CAADBAADIQADmDVxAkNQwGGebphEFgQ',
                                'CAADBAADJwADmDVxAguchI9CI5-dFgQ',
                                'CAADBAADGwADmDVxApFTHg4W1PB8FgQ',
                                'CAADBAADEwADmDVxAp3k1xTFyNcyFgQ']
        
    def getAnswer(self, message, app):
        if message == '/start':
            return  'Добро пожаловать в калькулятор сетей\n' + \
                    'для получения справки используйте команду /help'
        
        if message == '/stats':
            chats = 'Пользователи бота\n'
            for user in app.chats:
                chats += app.chats[user]['user_name'] + '\n'
            return chats
        
        if message[:5] == '/help':
            return getHelp(message)

        if message[:2] == '/:':
            flag_divide = True
            parts = message.split()
            prefixlen_diff = int(parts[0].replace('/:',''))
            message = message[2:]
        else:
            flag_divide = False

        messages=message.split() # split input by space
        addresses = []
        ip = Ip()
        for message_part in messages:
            address = ip.getAddress(message_part)
            if address:
                addresses.append(address)

        if len(addresses) == 0:
            return self.BAD_REQUEST_ANSWER

        if len(addresses) == 1:
            if flag_divide:
                if addresses[0]['omitted_octets'] == 4:
                    return self.BAD_REQUEST_ANSWER
                dividers = {2: 1, 4: 2, 8: 3, 16: 4, 32: 8}
                if prefixlen_diff not in dividers:
                    return 'можно делить только на 2, 4, 8, 16, 32'
                if addresses[0]['network'].prefixlen + dividers[prefixlen_diff] > 32:
                    return 'слишком большой делитель'
                network_list = ip.divNetworks(addresses[0], dividers[prefixlen_diff])
                answer  = 'Делим сеть на {}\n'.format(prefixlen_diff)
                for network in network_list:
                    answer += network['network'] + '\n'
                return answer
            else:
                info = ip.getInfo(addresses[0])
                return ip.getAnswer(info)
        else:   # sum network
            networks = []
            max_omitted_octets = 0
            for address in addresses:
                max_omitted_octets = max(max_omitted_octets, address['omitted_octets'])
                networks.append(address['network'])
            network_sum = ip.sumNetworks(networks)
            network = network_sum.network_address
            networks_parts = str(network).split('.')
            network_address = str(network)
            if max_omitted_octets == 3:
                network_address = 'XXX.YYY.ZZZ.{}'.format(networks_parts[3])
            if max_omitted_octets == 2:
                network_address = 'XXX.YYY.{}.{}'.format(networks_parts[2], networks_parts[3])
            if max_omitted_octets == 1:
                network_address = 'XXX.{}.{}.{}'.format(networks_parts[1], networks_parts[2], networks_parts[3])
            info = ip.getInfo({'omitted_octets': max_omitted_octets,
                               'address': network_address,
                               'network': network_sum})
            return ip.getAnswer(info)


    def getHelpKeyboard(self):
        button_1 = {'text': 'Как указать IP-адрес', 'callback_data': '/help ip-address'}
        button_2 = {'text': 'Как указать маску', 'callback_data': '/help netmask'}
        button_3 = {'text': 'Как указать префикс', 'callback_data': '/help prefix'}
        button_4 = {'text': 'Суммирование сетей', 'callback_data': '/help summary'}
        button_5 = {'text': 'Деление сетей', 'callback_data': '/help divide'}
        return {'inline_keyboard': [[button_1],[button_2],[button_3],[button_4],[button_5]]}

    def getSticker(self):
        random_index = random.randint(1, len(self.BAD_ANSWER_STICKER_LIST)) - 1
        return self.BAD_ANSWER_STICKER_LIST[random_index]