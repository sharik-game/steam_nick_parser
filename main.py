import asyncio
import argparse

import load_to_excel
import user_parser
import config

async def main():
  parser = argparse.ArgumentParser(description="steam nick parser cli")
  parser.add_argument("nickname", help="Nickname of the user")
  parser.add_argument("path_to_excel", help="Path to the Excel file")
  parser.add_argument("-c", "--coroutines", type=int, default=4, help="Number of coroutines (default: 4)")
  parser.add_argument("-d", "--delay", type=float, default=0.2, help="Delay between requests (default: 0.2)")
  args = parser.parse_args()
  if not args.nickname or not args.path_to_excel:
    raise Exception("Error: both 'nickname' and 'path_to_excel' arguments are required")
  if config.DEBUG >= 3: print("User-agent:", config.user_agent)
  raw_users = await user_parser.get_data(args.nickname, args.coroutines, args.delay)
  load_to_excel.create_excel(raw_users, path=args.path_to_excel)

if __name__ == "__main__": asyncio.run(main())