# Ошбики

### №1
После появления данной ошибки добавил "глобальный" tyr/except на весь код. И кажется, что это помогло. Бот больше не падал из-за такой ошибки. Но потом она повторилась опять) Как лечить? 
```
2021-09-15 04:36:49,835 (__init__.py:653 MainThread) ERROR - TeleBot: "A request to the Telegram API was unsuccessful. 
Error code: 403. Description: Forbidden: bot was blocked by the user"
```

```
2021-10-03 10:38:14,524 (__init__.py:663 MainThread) ERROR - TeleBot: "A request to the Telegram API was unsuccessful. 
Error code: 403. Description: Forbidden: bot was blocked by the user"
```

### №2
Пока не смог выяснить причину возникновения данной ошибки. Кажется, что что-то не так с загружаемыми данными ('2021_lake_results_for_bot.csv'). Но так как такая ошибка встречается достаточно редко, то просто сделал обработку этого места. Бот не падает, а я записываю в лог данные о пользователе у которого случилась эта ошибка. 

```
File "bot_0.1.1_public.py", line 277, in <module>
    bot.polling()
  File "/home/skv_sale/bot/venvBOT/lib/python3.8/site-packages/telebot/__init__.py", line 633, in polling
    self.__threaded_polling(non_stop, interval, timeout, long_polling_timeout, allowed_updates)
  File "/home/skv_sale/bot/venvBOT/lib/python3.8/site-packages/telebot/__init__.py", line 692, in __threaded_polling
    raise e
  File "/home/skv_sale/bot/venvBOT/lib/python3.8/site-packages/telebot/__init__.py", line 655, in __threaded_polling
    self.worker_pool.raise_exceptions()
  File "/home/skv_sale/bot/venvBOT/lib/python3.8/site-packages/telebot/util.py", line 130, in raise_exceptions
    raise self.exception_info
  File "/home/skv_sale/bot/venvBOT/lib/python3.8/site-packages/telebot/util.py", line 82, in run
    task(*args, **kwargs)
  File "bot_0.1.1_public.py", line 170, in handle_title
    user_time, user_group_count, target_user = user_data(message.text.lower(), users)
  File "bot_0.1.1_public.py", line 53, in user_data
    user_time = df[df['name'] == target_user]['time'].values[0]
IndexError: index 0 is out of bounds for axis 0 with size 0
```

### №3
В этом случае я вообще не понимаю, что произошло с ботом. Почему упал и как это нужно вылечить? 

```
Traceback (most recent call last):
  File "/home/skv_sale/bot/venvBOT/lib/python3.8/site-packages/urllib3/connectionpool.py", line 445, in _make_request
    six.raise_from(e, None)
  File "<string>", line 3, in raise_from
  File "/home/skv_sale/bot/venvBOT/lib/python3.8/site-packages/urllib3/connectionpool.py", line 440, in _make_request
    httplib_response = conn.getresponse()
  File "/usr/lib/python3.8/http/client.py", line 1344, in getresponse
    response.begin()
  File "/usr/lib/python3.8/http/client.py", line 307, in begin
    version, status, reason = self._read_status()
  File "/usr/lib/python3.8/http/client.py", line 268, in _read_status
    line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
  File "/usr/lib/python3.8/socket.py", line 669, in readinto
    return self._sock.recv_into(b)
  File "/usr/lib/python3.8/ssl.py", line 1241, in recv_into
    return self.read(nbytes, buffer)
  File "/usr/lib/python3.8/ssl.py", line 1099, in read
    return self._sslobj.read(len, buffer)
socket.timeout: The read operation timed out

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/skv_sale/bot/venvBOT/lib/python3.8/site-packages/requests/adapters.py", line 439, in send
    resp = conn.urlopen(
  File "/home/skv_sale/bot/venvBOT/lib/python3.8/site-packages/urllib3/connectionpool.py", line 755, in urlopen
    retries = retries.increment(
  File "/home/skv_sale/bot/venvBOT/lib/python3.8/site-packages/urllib3/util/retry.py", line 532, in increment
    raise six.reraise(type(error), error, _stacktrace)
  File "/home/skv_sale/bot/venvBOT/lib/python3.8/site-packages/urllib3/packages/six.py", line 770, in reraise
    raise value
  File "/home/skv_sale/bot/venvBOT/lib/python3.8/site-packages/urllib3/connectionpool.py", line 699, in urlopen
    httplib_response = self._make_request(
  File "/home/skv_sale/bot/venvBOT/lib/python3.8/site-packages/urllib3/connectionpool.py", line 447, in _make_request
    self._raise_timeout(err=e, url=url, timeout_value=read_timeout)
  File "/home/skv_sale/bot/venvBOT/lib/python3.8/site-packages/urllib3/connectionpool.py", line 336, in _raise_timeout
    raise ReadTimeoutError(
urllib3.exceptions.ReadTimeoutError: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=25)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "bot_0.1.2_public.py", line 271, in <module>
    bot.polling()
  File "/home/skv_sale/bot/venvBOT/lib/python3.8/site-packages/telebot/__init__.py", line 633, in polling
    self.__threaded_polling(non_stop, interval, timeout, long_polling_timeout, allowed_updates)
  File "/home/skv_sale/bot/venvBOT/lib/python3.8/site-packages/telebot/__init__.py", line 692, in __threaded_polling
```

# Вопросы
### 1
Как сделать так, чтобы при перезапуске бота (если я его перезапускаю) пользователям не валились все сообщения с самого первого?

### 2
Буду рад любым рекомендациям, чтобы сделать бота более стабильным с минимальными изменением кода )
