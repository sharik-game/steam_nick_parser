import asyncio
import sys

import load_to_excel
import user_parser
import config

async def main():
  if len(sys.argv) == 2 and sys.argv[1] == "-h" or sys.argv[1] == "--help":
    print(f"Usage: {__name__} nickname path_to_excel coroutines: int = 4 delay: float = 0.2")
    print("You can also set env DEBUG: int = 2 higher -> more information")
    return 0
  if len(sys.argv) <= 2: raise Exception(f"Usage: {__name__} nickname path_to_excel")
  if config.DEBUG >= 3: print("User-agent:", config.user_agent)
  if len(sys.argv) >= 5: raw_users = await user_parser.get_data(sys.argv[1], int(sys.argv[3]), float(sys.argv[4]))
  elif len(sys.argv) >= 4: raw_users = await user_parser.get_data(sys.argv[1], int(sys.argv[3]))
  else: await user_parser.get_data(sys.argv[1])
  load_to_excel.create_excel(raw_users, path=sys.argv[2])

if __name__ == "__main__": asyncio.run(main())