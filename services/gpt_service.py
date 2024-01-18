import requests
import json

chats_ids = []


def gpt_send_msg(msg):
    url = 'http://127.0.0.1:1337/v1/chat/completions'

    headers = {
        'Authorization': f'Bearer ActuallySoPohui',
        'Content-Type': 'application/json'
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": msg}
        ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        result = response.json()
        reply = result['choices'][0]['message']['content']
        print(result)
        return reply
    else:
        print()
        return f"Ошибка при отправке запроса: {response.status_code}"


gpt_send_msg('Что такое малюск')
gpt_send_msg('Что я спросил до этого?')
