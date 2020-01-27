import aiohttp
from aiohttp import web, WSMsgType

from answers import Answers

class GetUpdate(web.View):

    async def send_sticker(self, message):
        session = aiohttp.ClientSession(connector = aiohttp.TCPConnector(ssl = False));
        api_url = 'https://api.telegram.org/bot{}/sendSticker'.format(self.request.app.token)
        await session.post(api_url, data=message)
        await session.close()

    async def send_message(self, message):
        session = aiohttp.ClientSession(connector = aiohttp.TCPConnector(ssl = False));
        api_url = 'https://api.telegram.org/bot{}/sendMessage'.format(self.request.app.token)
        await session.post(api_url, data=message)
        await session.close()

    async def send_answer_callback_query(self, message):
        session = aiohttp.ClientSession(connector = aiohttp.TCPConnector(ssl = False));
        api_url = 'https://api.telegram.org/bot{}/answerCallbackQuery'.format(self.request.app.token)
        await session.post(api_url, data=message)
        await session.close()


    async def post(self):
        json_data = await self.request.json()
        answers = Answers()

        # save userdata for statistic
        if 'callback_query' in json_data: # press button on inline keyboard
            button_data = json_data['callback_query']['data']
            answer_data = { 'chat_id': json_data['callback_query']['from']['id'],
                            'text': answers.getAnswer(button_data, self.request.app)}
            await self.send_answer_callback_query({'callback_query_id': json_data['callback_query']['id']})
            await self.send_message(answer_data)
            return web.json_response({})

        user_id = json_data['message']['from']['id']
        username = json_data['message']['from'].get('username','')
        first_name = json_data['message']['from'].get('first_name','')
        last_name = json_data['message']['from'].get('last_name','')
        user_data = {'user_id': user_id,
                     'user_name': '{} ({} {})'.format(username, first_name, last_name)}
        if user_id not in self.request.app.chats:
            self.request.app.chats[user_id] = user_data
            self.request.app.logger.info(user_data)

        chat_id = json_data['message']['chat']['id']
        if 'text' in json_data['message']:
            text = json_data['message']['text']

            answer = answers.getAnswer(text,self.request.app)

            if text[:5] == '/help':
                result_data = { 'method': 'sendMessage',
                                'chat_id': chat_id,
                                'text': answers.getAnswer(text, self.request.app),
                                'reply_to_message_id': json_data['message']['message_id'],
                                'reply_markup': answers.getHelpKeyboard()}
            else:
                result_data = {'method': 'sendMessage','chat_id': chat_id, 'text': answer}
        else:
            result_data = {'method': 'sendMessage','chat_id': chat_id, 'text': answers.BAD_REQUEST_ANSWER}

        
        if result_data['text'] == answers.BAD_REQUEST_ANSWER:
            sticker_data = {'chat_id': chat_id,
                            'sticker': answers.getSticker()}
            await self.send_sticker(sticker_data)

        return web.json_response(result_data)
