from pathlib import Path
import shutil
from typing import Iterator, Optional
import urllib.request

from bs4 import BeautifulSoup
import requests


def download(cart_id: str, target_path: Path) -> None:
    output_filename = target_path / f'cart_{cart_id}.gif'

    # No need to redownload. Save resources on tic80.com.
    if output_filename.exists():
        return

    url = f'https://tic80.com/play?cart={cart_id}'
    req = requests.get(url)
    html = req.content

    cover_image_url = find_cover_image_url(html)

    img_resp = requests.get(cover_image_url, stream=True)
    if img_resp.status_code != 200:
        return

    with output_filename.open('wb') as f:
        img_resp.raw.decode_content = True
        shutil.copyfileobj(img_resp.raw, f)


def find_cover_image_url(html) -> Optional[str]:
    soup = BeautifulSoup(html, 'html5lib')
    img = soup.find('meta', {'property': 'og:image'})
    return img.attrs.get('content')


def find_cart_ids(event) -> Iterator[str]:
    for phase in event['phases']:
        for entry in phase['entries']:
            cart_id = entry.get('tic80_cart_id')
            if cart_id:
                yield cart_id


def create_cache(event, target_path: Path):
    for cart_id in find_cart_ids(event):
        download(cart_id, target_path)
