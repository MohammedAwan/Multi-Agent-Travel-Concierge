from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72, description="Password max 72 bytes")
    full_name: str = Field(default="", description="Display name")

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., max_length=72)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"