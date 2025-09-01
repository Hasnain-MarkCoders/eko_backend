from pydantic import BaseModel
from typing import Optional

class ChangeNameRequest(BaseModel):
    newName: str

class ChangeImageRequest(BaseModel):
    image_url: str

class UpdateTokenRequest(BaseModel):
    notificationToken: str

class GetUserQuery(BaseModel):
    _id: Optional[str] = None 