import logging
from pathlib import Path
from urllib.parse import urlparse
import zipfile
import requests

from tqdm.auto import tqdm
#import numpy as np


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def extract_zip(path, folder):
    with zipfile.ZipFile(path, 'r') as f:
        f.extractall(folder)


def download(url, target_path, restart=False):
    filename = Path(urlparse(url).path).name
    local_path = Path(target_path).joinpath(filename)
    chunk = 10240
    if not restart and local_path.exists():
        # compare
        r = requests.get(url, stream=True)
        size = int(r.headers.get('content-length'))
        with open(local_path, "ab") as f:
            resume_byte_pos = f.tell()
            if size > resume_byte_pos:
                # resume
                logger.info(f"resume the file download from {resume_byte_pos} bytes")
                resume_header = {'Range': f'bytes={resume_byte_pos}-'}
                r = requests.get(url, headers=resume_header, stream=True)
                size = int(r.headers.get('content-length'))
                with tqdm(total=(resume_byte_pos + size), initial=resume_byte_pos,
                          unit="bytes", dynamic_ncols=True) as pbar:
                    for c in r.iter_content(chunk_size=chunk):
                        if c:
                            f.write(c)
                        pbar.update(len(c))
    else:
        # new download
        logger.info(f"download the file from {url}")
        local_path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
        r = requests.get(url, stream=True)
        size = int(r.headers.get('content-length'))
        with open(local_path, "wb") as f:
            with tqdm(total=size, unit="bytes", dynamic_ncols=True) as pbar:
                for c in r.iter_content(chunk_size=chunk):
                    if c:
                        f.write(c)
                    pbar.update(len(c))
    logger.info(f"The file has stored in '{local_path}'")
    return local_path

