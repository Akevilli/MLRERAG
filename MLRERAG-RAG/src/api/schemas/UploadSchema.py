from typing import List

from pydantic import BaseModel


class UploadSchema(BaseModel):

    id_list: List[str]