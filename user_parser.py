import asyncio
from concurrent.futures import ProcessPoolExecutor
import json

import aiohttp
from bs4 import BeautifulSoup, ResultSet
import tqdm

import config

def create_tasks(number_of_workers, coro, *args):
  tasks: list[asyncio.Task] = []
  for _ in range(number_of_workers):
      task = asyncio.create_task(coro(*args))
      tasks.append(task)
  return tasks
def cancel_tasks(tasks): [task.cancel() for task in tasks]

def form_user_profile_link(link: str) -> str:
  if link.startswith(f"{config.BaseUrlProfile}profiles/"): return f"{config.BaseUrlProfile}profiles/{link[36:]}/ajaxaliases" # len("https://steamcommunity.com/profiles/") = 36
  elif link.startswith(f"{config.BaseUrlProfile}id/"): return f"{config.BaseUrlProfile}id/{link[30:]}/ajaxaliases" # len("https://steamcommunity.com/id/") = 30
  else: raise Exception(f"Invalid link to user profile: {link}")

def parse_users(res: str) -> list[config.User]:
  html = json.loads(res)["html"]
  soup = BeautifulSoup(html, features="lxml")
  links_and_name: ResultSet = soup.find_all("div", class_="searchPersonaInfo")
  profile_links = []
  for link_and_name in links_and_name:
    link: str = link_and_name.a["href"]
    user_list: list = link_and_name.text.strip().split("\t")
    user_list = list(filter(None, [item.strip() for item in user_list]))
    try: 
      link_and_name.find("img")["src"]
      if len(user_list) <= 2: 
        name = ""
        location = user_list[1]
      else: 
        name= user_list[1]
        location = user_list[2]
    except TypeError: 
      location = ""
      if len(user_list) > 1: name = user_list[1]
      else: name = ""
    user = config.User(user_list[0], "", location, name, link, form_user_profile_link(link), [])
    profile_links.append(user)
  return profile_links

def parse_desc(html: str):
  soup = BeautifulSoup(html, features="lxml")
  try: desc = soup.find("div", class_="profile_summary").text.strip() # type: ignore
  except AttributeError: desc = ""
  return desc

async def make_req(session: aiohttp.ClientSession, url: str, return_json: bool = False, urls_bar: tqdm.tqdm | None = None):
  res: aiohttp.ClientResponse = await session.get(url)
  if not res.ok: raise Exception(f"response code: {res.status}, response: {res.text}")
  if config.DEBUG >= 2 and urls_bar is not None: urls_bar.update(1)
  try:
    if not return_json: return await res.text(encoding="utf-8")
    else: return await res.json(encoding="utf-8")
  except aiohttp.client_exceptions.ContentTypeError: # type: ignore
    if config.DEBUG >= 2: urls_bar.set_description(f"can not parse response {res.status} link:{url}") # type: ignore
    elif config.DEBUG: print(f"can not parse response {res.status} link:{url}")
    return 1

async def make_urls(session: aiohttp.ClientSession, nickname: str) -> tuple[asyncio.Queue[str], int, int]:
  base_url = f"{config.BaseUrlProfile}search/SearchCommunityAjax?text={nickname.replace(' ', '+')}&&filter=false&&sessionid=cd69d7f77596eefa5ec8e72b&&steamid_user=false"
  res = await make_req(session, base_url+"&&page=1")
  assert res != 1
  res_js = json.loads(res)
  total_users = res_js["search_result_count"]
  pages = (total_users+config.NICKS_IN_ONE_PAGE-1) // config.NICKS_IN_ONE_PAGE
  urls_queue = asyncio.Queue()
  for i in range(1, pages+1):
    url = f"{base_url}&&page={i}" 
    await urls_queue.put(url)
  return urls_queue, total_users, pages

async def get_user_profile(session: aiohttp.ClientSession, user_profiles_queue: asyncio.Queue, raw_users: list[list[list[config.User]]], delay: float, urls_bar: tqdm.tqdm):
  while not user_profiles_queue.empty():
    user_profile: dict[str, tuple[int, int, int]] = await user_profiles_queue.get()
    user_profile_link: str = list(user_profile.keys())[0]
    i, j, k = user_profile[user_profile_link]
    user_profile_json = await make_req(session, user_profile_link, True, urls_bar)
    user_profile_desc = await make_req(session, user_profile_link.replace("/ajaxaliases", ""), urls_bar=urls_bar)
    user_profile_desc = parse_desc(user_profile_desc) # type: ignore
    if user_profile_desc != "": raw_users[i][j][k] = raw_users[i][j][k]._replace(description=user_profile_desc)
    await asyncio.sleep(delay)
    if user_profile_json == 1:
      user_profiles_queue.task_done()
      continue
    try:
      current_other_nicknames = [other_nickname["newname"] for other_nickname in user_profile_json][1:] # type: ignore
      for current_other_nickname in current_other_nicknames:
        raw_users[i][j][k].other_nicknames.append(current_other_nickname)
    except Exception as ex:
      print(f"Error: {ex}, link: {user_profile_link}")
    user_profiles_queue.task_done()

async def get_pages(session: aiohttp.ClientSession, urls_queue: asyncio.Queue, urls_bar: tqdm.tqdm):
  raw_users = []
  while not urls_queue.empty():
    url = await urls_queue.get()
    res = await make_req(session, url, urls_bar=urls_bar)
    loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
    with ProcessPoolExecutor() as pool:
      current_raw_users: list[User] = await loop.run_in_executor(pool, parse_users, res) # type: ignore
    raw_users.append(current_raw_users)
    urls_queue.task_done()
  return raw_users

async def get_data(nickname: str, coroutines: int = 4, delay: float = 0.2):
  session: aiohttp.ClientSession = aiohttp.ClientSession(headers=config.headers, cookies=config.cookies)
  urls_queue, total_users, pages = await make_urls(session, nickname)
  total_req = total_users * 2 + pages 
  if config.DEBUG >= 3: print("urls_queue len:", urls_queue.qsize())
  if config.DEBUG >= 2: urls_bar = tqdm.tqdm(total=total_req)
  user_profiles_queue = asyncio.Queue()
  pages_getters = create_tasks(coroutines, get_pages, session, urls_queue, urls_bar)
  raw_users = await asyncio.gather(*pages_getters)
  await urls_queue.join()
  cancel_tasks(pages_getters)
  for i in range(len(raw_users)):
    for j in range(len(raw_users[i])):
      for k in range(len(raw_users[i][j])):
        link: str = raw_users[i][j][k].profile_link
        task: dict[str, tuple[int, int, int]] = {link: (i, j, k)}
        await user_profiles_queue.put(task)
  user_profiles_getter = create_tasks(coroutines*4, get_user_profile, session, user_profiles_queue, raw_users, delay, urls_bar)
  await asyncio.gather(*user_profiles_getter)
  await user_profiles_queue.join()
  cancel_tasks(user_profiles_getter)
  await session.close()
  if config.DEBUG >= 2: urls_bar.close()
  if config.DEBUG >= 4:
    with open("output.txt", "w", encoding="utf-8") as file: file.write(str(raw_users))
    print("Writing in file output2.txt was successfull")
  return raw_users

if __name__ == "__main__":
  asyncio.run(get_data("Тут ник"))