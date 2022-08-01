from typing import AsyncGenerator
import hashlib

from furl import furl
import aiofiles
from fs import open_fs
from fs.errors import InvalidPath


def validate_url(url: str):
    try:
        fu = furl(url)
        root = str(f"{fu.scheme}://{fu.netloc}/")
        path = str(fu.path)
        fs = open_fs(root)
        fs.validatepath(path)
        return True
    except InvalidPath:
        return False
    except Exception as e:
        raise e


async def get_file_contents(url: furl, chunk_size: int = -1) -> AsyncGenerator[bytes, None]:
    async with aiofiles.open(str(url.path), 'rb') as f:
        chunk = await f.read(chunk_size)
        yield chunk


async def get_file_sha256_hash(url: furl) -> str:
    chksum_hash = hashlib.sha256()
    async for chunk in get_file_contents(url, 4096):
        chksum_hash.update(chunk)
    return chksum_hash.hexdigest()
