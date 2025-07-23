import asyncio
import hashlib
import re
from collections import deque
from typing import List

import httpx
from bs4 import BeautifulSoup
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.pretty import pprint

# Configure logging to write to debug.log
# logging.basicConfig(
#     filename="debug.log",
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     filemode="w",
# )
console = Console()

last_hash = None
lifo_queue = deque(maxlen=4)

headers = {
    "Host": "www.reddit.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Referer": "https://www.reddit.com/r/wallstreetbets/comments/1grttc6/daily_discussion_thread_for_november_15_2024/",
    "DNT": "1",
    "Sec-GPC": "1",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Connection": "keep-alive",
    "Cookie": "edgebucket=oADCprwBYeP3VaPs2m; loid=000000000uwa0r9lim.2.1708817623886.Z0FBQUFBQmwzdjdIMFduSVZZMHNVLTFfU2czQUo1UzJJR002MFZKOHphMzRlMEw3LVNRQ1JYTVlhdFRCUHRqN1dXcEo0TWxmRHpWbkw3dlhVZVpEVGRjTjJ2M3hwSmJFLVZJekxjTzNSYngtV05DaUxjbzBTdlg5akplT3hXZWlBa0ZqdVlEX2Ryb2Q; csv=2; eu_cookie={%22opted%22:true%2C%22nonessential%22:true}; reddit_session=eyJhbGciOiJSUzI1NiIsImtpZCI6IlNIQTI1NjpsVFdYNlFVUEloWktaRG1rR0pVd1gvdWNFK01BSjBYRE12RU1kNzVxTXQ4IiwidHlwIjoiSldUIn0.eyJzdWIiOiJ0Ml91d2EwcjlsaW0iLCJleHAiOjE3NDY2MjU3MzIuMTk2NDc0LCJpYXQiOjE3MzA5ODczMzIuMTk2NDc0LCJqdGkiOiJOSUJKbGtGeFZUai1MZXhveTZQQjFuUk9YVmVWWlEiLCJjaWQiOiJjb29raWUiLCJsY2EiOjE3MDg4MTc2MjM4ODYsInNjcCI6ImVKeUtqZ1VFQUFEX193RVZBTGsiLCJ2MSI6Ijg3MTYyNzY0MDk1NTM0JTJDMjAyNC0wMi0yOFQwOSUzQTM3JTNBMTElMkM1ODI1NmQwNTEyNDAwYjk4NjRmNjQxYmE4YjdlOWI0M2E4YjMxYmE1IiwiZmxvIjoxfQ.gNxZp4X9z2pCytwZ3EwH-YZc5fSSa7lJnySREYi7CLXDRHJ6j-vesEIVk9MjKhUx2hENbP9EIVqIeVlC_b6PYDefwR-b6zzk2hSrnHu1P3tDneyD-76T-hfUL4B8_8U9FiJas8u6YMdF03I0xK6Zsb2fp-e9w_Qj04aHJE-1P-7lst2F8uZHoFHXw2hn_S5uusKNR1CMaIttM2KKPpMlkPgXO5iymuGrhVbEUoovemVBj8l7Dc_66ls__NCTDSpGQKBw6MYADObnpiQ9iTsMavy8XUPiWu9vyY88bJT9IgNbqFyI_ebHvh-CVn4TyK0ax5UIz2lV080TbyY-omJoCQ; t2_uwa0r9lim_recentclicks3=t3_1grlzqe%2Ct3_1grnww9%2Ct3_1gro9qo%2Ct3_1gr0q8x%2Ct3_1grsa76%2Ct3_1grttc6%2Ct3_13jcw3i%2Ct3_1grr7yb%2Ct3_1grsudd%2Ct3_1grokja; theme=1; __stripe_mid=dbe213e4-2c6b-42d3-9c68-2ade1ad127e8fed730; pc=u6; eu_cookie={%22opted%22:true%2C%22nonessential%22:true}; recent_srs=t5_2yrq6%2C; rdt=b10352b9a852785109b8e7fe5064920f; session=35a7919a00fde468254d0e31c4aa24dc90fd7ed2gAWVSQAAAAAAAABKOiQyZ0dB2XhvfdHbxH2UjAdfY3NyZnRflIwoOTFkOWUyMWQ4NjBhNGYzYWYyN2FmNzIyMjBjYzgwYjQwMzE2MzViMZRzh5Qu; PeachScary413_recentclicks2=t3_1c1mr41; csrf_token=b2e018aa53c2dcdb5bf763f846f3a447; reddit_chat_view=closed; reddit_chat_path=/room/!obC0tbBT_U35Wfogs9-i5DDIr9Rv9utjIGirmhGtCbI%253Areddit.com; session_tracker=cdiirjfeaorrdgpiin.0.1731683247040.Z0FBQUFBQm5OMk92bGZnU21lTUpRdUpuNV8xRTZkYVRaUzJpU2ZnVDBpVzJnbldJQVo0aFpyMzRpV2QtdU9ucElqNkYxdFIwTjVIdFd3TnRIdHI4MkF2ZkIzbkphT1MzejBDYXBhczl4QVNSUnVYcXV6ekdacWNCX0hLUzUxdnBEeF9iWmVkd2tLcjk; token_v2=eyJhbGciOiJSUzI1NiIsImtpZCI6IlNIQTI1NjpzS3dsMnlsV0VtMjVmcXhwTU40cWY4MXE2OWFFdWFyMnpLMUdhVGxjdWNZIiwidHlwIjoiSldUIn0.eyJzdWIiOiJ1c2VyIiwiZXhwIjoxNzMxNzYxNDc2LjEwMDgyOCwiaWF0IjoxNzMxNjc1MDc2LjEwMDgyOCwianRpIjoiaXk0MlRleGQ3SFUwQkxxSlcwaU9sVTBxRTdPWVRnIiwiY2lkIjoiMFItV0FNaHVvby1NeVEiLCJsaWQiOiJ0Ml91d2EwcjlsaW0iLCJhaWQiOiJ0Ml91d2EwcjlsaW0iLCJsY2EiOjE3MDg4MTc2MjM4ODYsInNjcCI6ImVKeGtrZEdPdERBSWhkLWwxejdCX3lwX05odHNjWWFzTFFhb2szbjdEVm9jazcwN2NMNGlIUDhuS0lxRkxFMnVCS0drS1dFRld0T1VOaUx2NTh5OU9aRUZTeUZUUjg0M3l3b2thVXBQVW1ONXB5bFJ3V1prTGxmYXNVS0RCNllwVlM2WjIwS1BTNXZRM0kxRnowNk1xbHhXSHRUWW8zSnBiR01LMnhQanpjWnFReXF1eTZsTVlGa29uOFdMZnZ5Ry10WS1mN2JmaEhZd3JLZ0tEX1RPdUZ4d1lfSERGSGJfbnByMGJGMndxTDNYZzlRLTEtTjI3Yk5tb2RtNV9WelB2emFTY1RtRzVpZll2N3QtQ1IxNDVIbVpVUWN3WWcwX3lyQWo2X0N2T29ES0JRV01KWWhQSTVBcmwyX19KZGl1VGY4YXR5ZC0tR2JFVFdfNHJSbW81eExFb1VfajZ6Y0FBUF9fWERfZTR3IiwicmNpZCI6IkdYa2xPQWNPZC1BOFhBcXpoaG5aYy00SVNZUThzMnIzSkM1eFlxRG5pZjgiLCJmbG8iOjJ9.V60549_nOXsMEKVraoY5pHEb6sQDs7P-ksOjzO5tYAGrn2xjQPqzw_lgqSkJY1LOHnauvf_rAyXWtJiIAgM0KAVcD4UCaMgbfdAdeSrJ9I_-QfsyqlvBFhoGmUpb7OUxcjKD61INK4imjBj8GWeq85XujCZCKIX_rluyqhh0xXQ3ILUtUKLdr5boOSzFz9zVFjM7Gn8Rxqq70XosMFz_vRkGkeDgzyltTxnaESOjujidqiGuP4S50rSeiXnauVMEynQHQ1GEFZF5EIRdjXOEuOtY1uovR0aYMhT_FJ-WWPDy_D2qRVDKFEIdukYJVNqM4FXVUxWOTR-C5d6xVstm1w",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
}


async def get_latest_comment(thread_id: str) -> str:
    response = await fetch(thread_id)
    soup = BeautifulSoup(response.text, "html.parser")
    comments = soup.find_all("shreddit-comment")
    for comment in comments:
        badges = comment.find("shreddit-comment-badges")
        stickied = badges is not None and ("stickied" in badges.attrs)
        if not stickied:
            content = comment.find(
                "div", id=lambda x: x and x.endswith("-post-rtjson-content")
            )
            if content:
                return content.text
    return ""


async def fetch(thread_id) -> httpx.Response:
    url = f"https://www.reddit.com/svc/shreddit/comments/r/wallstreetbets/t3_{thread_id}?render-mode=partial&is_lit_ssr=false"
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.get(url, headers=headers)
        return response.raise_for_status()


async def background(thread_id: str):
    global last_hash
    text = ""
    delay = 2
    with Live(Panel(text), screen=True, auto_refresh=False) as live:
        i = 0
        while True:
            if i % 100 == 0:
                text = ""
            comment = await get_latest_comment(thread_id)
            hasher = hashlib.sha256(comment.encode("utf-8"))
            new_hash = hasher.hexdigest()
            if new_hash == last_hash:
                await asyncio.sleep(delay)
                delay = min(delay + 1, 30)
                continue
            last_hash = new_hash
            text = f"[green]#{i}[/][orange1]{comment}[/]\n" + text
            live.update(Panel(text), refresh=True)
            await asyncio.sleep(delay)
            delay = 2
            i += 1


def is_daily_thread(name: str) -> bool:
    return (
        name.startswith("daily_discussion")
        or name.startswith("what_are_your_moves_tomorrow")
        or name.startswith("weekend_discussion_thread")
    )


async def get_latest_thread_id() -> str:
    url = "https://www.reddit.com/r/wallstreetbets/"
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    post_links = soup.find_all("a", attrs={"slot": "full-post-link"})
    parts = [re.split(r"/", link["href"]) for link in post_links]
    for part in parts:
        id = part[4]
        if is_daily_thread(part[5]):
            return id
    raise ValueError({"error": "No daily thread found", "parts": parts})


async def main():
    thread_id = await get_latest_thread_id()
    await asyncio.gather(background(thread_id))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("[red]Exited[/]")
