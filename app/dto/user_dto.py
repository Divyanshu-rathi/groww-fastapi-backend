from pydantic import BaseModel, EmailStr

class CreateUserDTO(BaseModel):
    username: str
    email: EmailStr
    password: str
    groww_api_key: str
    groww_secret_key: str

class LoginUserDTO(BaseModel):
    username: str
    password: str
