## dont forget to star! 50 stars for an full functioned one in GoLang or py again

import asyncio
import threading
import random
from aiohttp import ClientSession
from colorama import Fore, Style

tokens = [line.strip() for line in open("index/tokens.txt").readlines()]
red, green, yellow, reset = Fore.RED, Fore.GREEN, Fore.YELLOW, Style.RESET_ALL
succ, fail, ratelimit = f"{Fore.LIGHTBLACK_EX}[{reset}+{Fore.LIGHTBLACK_EX}]{reset}", f"{Fore.LIGHTBLACK_EX}[{reset}-{Fore.LIGHTBLACK_EX}]{reset}", F"{Fore.LIGHTBLACK_EX}[{reset}?{Fore.LIGHTBLACK_EX}]{reset}"

class MessageSpammer:
    def __init__(self, content, channel_id, amount):
        self.content = content
        self.channel_id = channel_id
        self.amount = amount
        self.lock = threading.Lock()
        self.token_usage = {token: 0 for token in tokens}
        self.failed_tokens = set()
        self.stats = {"success": 0, "failures": 0, "rate_limits": 0}

    async def send_message(self, token, session):
        url = f"https://discord.com/api/v9/channels/{self.channel_id}/messages"
        headers = {"Authorization": token, "Content-Type": "application/json"}
        payload = {"content": self.content, "flags": 0}

        async with session.post(url, json=payload, headers=headers) as response:
            if response.status in [200, 201]:
                self.update_stats("success")
            elif response.status == 429:
                retry_after = (await response.json()).get("retry_after", 1)
                self.update_stats("rate_limits")
                await asyncio.sleep(retry_after)
            else:
                self.update_stats("failures")
                with self.lock:
                    self.failed_tokens.add(token)

    def rotate_token(self):
        with self.lock:
            valid_tokens = [t for t in tokens if t not in self.failed_tokens]
            if not valid_tokens:
                raise RuntimeError("All tokens failed. Aborting.")
            token = random.choice(valid_tokens)
            self.token_usage[token] += 1
            return token

    def update_stats(self, key):
        with self.lock:
            self.stats[key] += 1

    async def spam_task(self):
        async with ClientSession() as session:
            tasks = [self.send_message(self.rotate_token(), session) for _ in range(self.amount)]
            await asyncio.gather(*tasks, return_exceptions=True)

    def execute_spam(self):
        threads = []
        for _ in range(len(tokens)):
            thread = threading.Thread(target=self._run_thread)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        self.report_stats()

    def _run_thread(self):
        try:
            asyncio.run(self.spam_task())
        except Exception as e:
            print(f"{fail} Thread error: {e}")

    def report_stats(self):
        print(f"{succ} Successful Threads Amount {self.stats['success']}{reset}")
        print(f"{ratelimit} Rate Limited Threads Amount {self.stats['rate_limits']}{reset}")
        print(f"{fail} Failures {self.stats['failures']}{reset}")

def tkc(tokens):
    async def count_valid(tokens):
        return sum(1 for t in tokens if t.strip())

    async def count_empty(tokens):
        return sum(1 for t in tokens if not t.strip())

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    valid_count = loop.run_until_complete(count_valid(tokens))
    empty_count = loop.run_until_complete(count_empty(tokens))
    loop.close()

    return (
        f"{succ} Total Of {len(tokens)} Token(s) Found\n\n".strip()
    )

def main():
    banner = """
                        github.com/osnerd
       _ _   _           _                                    _
  __ _(_) |_| |__  _   _| |__     ___  ___ _ __   ___ _ __ __| |
 / _` | | __| '_ \| | | | '_ \   / _ \/ __| '_ \ / _ \ '__/ _` |
| (_| | | |_| | | | |_| | |_) | | (_) \__ \ | | |  __/ | | (_| |
 \__, |_|\__|_| |_|\__,_|_.__/   \___/|___/_| |_|\___|_|  \__,_|
 |___/                                                          
"""

    print(Fore.LIGHTBLACK_EX, banner.strip(), "\n")

    x = tkc
    print(tkc(tokens=tokens), "\n")
    content = "i have 1, 2, 3, 4 in my bank account. in my bank account in my bank account" # content aka message here 
    channel_id = "1325155055736717363"  # replace with ur actual channel id
    amount = 50 # amount of messages

    spammer = MessageSpammer(content, channel_id, amount)
    spammer.execute_spam()

main()
