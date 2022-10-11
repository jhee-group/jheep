from ..schemas.filestore import sFile
from ..models.filestore import mFile
from ..services.files import validate_url, get_file_contents, get_file_sha256_hash


class FileObject:

    def __init__(self, obj: sFile | mFile):
        self.obj = obj

    async def validate(self) -> bool:
        full_path = await self.obj.get_full_path()
        return validate_url(full_path)

    async def get_contents(self) -> bytes | None:
        full_path = await self.obj.get_full_path()
        contents = await anext(get_file_contents(full_path))
        return contents

    async def get_hash(self) -> str | None:
        full_path = await self.obj.get_full_path()
        sha256 = await get_file_sha256_hash(full_path.url)
        return sha256
