import logging

import requests

logger = logging.getLogger(__name__)


class Qiita():
    def __init__(self):
        logger.debug("init")

    def validate(self, account_id):
        response = requests.get('https://qiita.com/' + account_id)
        if response.status_code == requests.codes.ok:
            return True
        else:
            return False


class Zenn():
    def __init__(self):
        logger.debug("init")

    def validate(self, account_id):
        response = requests.get('https://zenn.dev/' + account_id)
        if response.status_code == requests.codes.ok:
            return True
        else:
            return False


class Connpass():
    def __init__(self):
        logger.debug("init")

    def validate(self, account_id):
        response = requests.get('https://connpass.com/user/' + account_id)
        if response.status_code == requests.codes.ok:
            return True
        else:
            return False
