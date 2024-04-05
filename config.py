from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName

from collections import namedtuple
import os

User = namedtuple("User", "nickname, description, location, name, link, profile_link, other_nicknames")

class DebugSingleton:
  def __init__(self): self.value = os.getenv("DEBUG", 2)
  def __call__(self, x): self.value = x
  def __bool__(self) -> bool: return self.value != 0
  def __ge__(self, x) -> bool: return self.value >= x
DEBUG = DebugSingleton()

user_agent_rotator = UserAgent(software_names=SoftwareName.CHROME.value, limit=1)
user_agent = user_agent_rotator.get_user_agents()[0]['user_agent']
# print(user_agent)
cookies = {
  'sessionid': 'cd69d7f77596eefa5ec8e72b',
  'steamCountry': 'RU%7C19b6bd2272ce64e812a0b5fd6b177c44',
  'timezoneOffset': '10800,0',
}

headers = {
  'Accept': '*/*',
  'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
  'Cache-Control': 'no-cache',
  'Connection': 'keep-alive',
  # 'Cookie': 'sessionid=cd69d7f77596eefa5ec8e72b; steamCountry=RU%7C19b6bd2272ce64e812a0b5fd6b177c44; timezoneOffset=10800,0',
  'Pragma': 'no-cache',
  'Referer': 'https://steamcommunity.com/search/users/?text=%D0%A2%D1%83%D1%82+%D0%BD%D0%B8%D0%BA',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'User-Agent': user_agent,
  # Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
  'X-Requested-With': 'XMLHttpRequest',
  'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
}

NICKS_IN_ONE_PAGE = 20

BaseUrlProfile = "https://steamcommunity.com/"