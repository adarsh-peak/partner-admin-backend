from pydantic import BaseModel


class ConsentInBound(BaseModel):
    CompanyID: int
    ContactID: int
    RoleID: int
