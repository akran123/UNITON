from pydantic import BaseModel
from typing import Literal

# 사용자 생성을 위한 요청 스키마
class GuardianBase(BaseModel):
    name: str
    fcm_token : str

    model_config = {
        "from_attributes": True  #딕셔너리 아닌 객체 속성 읽기 허용
    }

class ProtectedPersonBase(BaseModel):
    name : str
    device_id :str

    model_config = {
        "from_attributes": True  #딕셔너리 아닌 객체 속성 읽기 허용
    }


