#!/usr/bin/env python3

import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup

TODAY = datetime.now()
MONTH = TODAY.month
YEAR = TODAY.year


LOGIN_URL = "https://prometeoapi.com/dashboard/login/"
DASHBOARD_URL = "https://prometeoapi.com/dashboard/"
CONFIG_URL = "https://prometeoapi.com/dashboard/settings/"
CURRENT_MONTH_HISTORY_URL = f"https://prometeoapi.com/dashboard/filter_requests/?user_id=&month={MONTH}&year={YEAR}"
USERNAME = "prueba-dev@prometeoapi.com"
PASSWORD = "thePasswordHere"


class DashboardInfo:
    """
    A class to extract all the information from the dashboard
    """

    def __init__(self, username, password):
        super(DashboardInfo, self).__init__()

        self.username = username
        self.password = password

        self.client, self.data = self._generate_client()

    def _generate_client(self):
        """
        Creates a new authenticated REQUESTS client
        """

        client = requests.session()

        client.get(LOGIN_URL)

        if "csrftoken" in client.cookies:
            csrftoken = client.cookies["csrftoken"]

        data = {
            "username": self.username,
            "password": self.password,
            "csrfmiddlewaretoken": csrftoken,
        }

        request = client.post(LOGIN_URL, data=data, headers=dict(Referer=LOGIN_URL))

        if request.url == LOGIN_URL:
            raise requests.HTTPError()

        return client, data

    def _get(self, url):
        return self.client.get(url, data=self.data)

    def _post(self, url):
        return self.client.post(url, data=self.data)

    def get_api_key(self, url=DASHBOARD_URL):
        dashboard = self._get(DASHBOARD_URL)
        dashboard_soup = BeautifulSoup(dashboard.text, features="lxml")
        return dashboard_soup.find("span", {"class": "pui-f-ubuntu-mono"}).text.strip()

    def get_name_and_last_name(self, url=CONFIG_URL):
        config = self._get(CONFIG_URL)
        config_soup = BeautifulSoup(config.text, features="lxml")

        first_name = config_soup.find("input", {"name": "first_name"})["value"]
        last_name = config_soup.find("input", {"name": "last_name"})["value"]
        return dict(first_name=first_name, last_name=last_name)

    def get_history(self, url=CURRENT_MONTH_HISTORY_URL):
        history = self._get(CURRENT_MONTH_HISTORY_URL)
        return history.json()


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 2 and args[1] in ["--help", "-h"]:
        print("Usage: script <username> <password>")

    else:
        username, password = [USERNAME, PASSWORD]

        if len(sys.argv) == 3:
            username, password = args[1:]

        try:
            info = DashboardInfo(username=username, password=password)

            return_data = {
                **info.get_name_and_last_name(),
                "api_key": info.get_api_key(),
                "history": info.get_history(),
            }

            print(return_data)
        except requests.exceptions.HTTPError:
            print("Username and password are incorrect")
        except Exception:
            print("Something happened with the request. Try again later")
