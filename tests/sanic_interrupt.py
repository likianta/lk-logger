"""
pip install lk-utils, requests, sanic
py examples/edge_cases/sanic_interrupt.py
"""
from time import sleep

import requests
from lk_utils import new_thread
from sanic import Sanic

app = Sanic('lklogger-interrupt-test')


@app.route('/')
async def index(_):
    # return text('ok')
    raise Exception('test error')


@new_thread()
def test_request():
    sleep(0.5)
    requests.get('http://localhost:2000')


if __name__ == '__main__':
    # webbrowser.open('http://localhost:2000')
    test_request()
    app.run('localhost', 2000)
