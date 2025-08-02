from pydantic import BaseModel, field_validator

class TextRequest(BaseModel):
    text: str

    @field_validator('text')
    @classmethod
    def validateText(cls, value):
        if not value:
            raise ValueError("Can't be empty")
        for char in value:
            if not (char.isupper() or char == ' '):
                raise ValueError("Only uppercase letters and spaces allowed")
        return value

class TextResponse(BaseModel):
    result: str
