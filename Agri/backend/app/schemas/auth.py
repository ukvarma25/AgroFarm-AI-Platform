from pydantic import BaseModel, EmailStr, Field, field_validator

ROLES = ("farmer", "agri_officer", "fertilizer_dealer", "admin")
SOIL_TYPES = (
    "Alluvial",
    "Black",
    "Red",
    "Laterite",
    "Arid",
    "Mountain",
    "Other",
)


class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    phone: str
    password: str = Field(..., min_length=8)
    confirm_password: str
    role: str = "farmer"
    farm_name: str = Field(..., min_length=1)
    farm_location: str = Field(..., min_length=1)
    land_size_acres: float = Field(..., gt=0)
    soil_type: str = "Other"
    lat: float | None = None
    lng: float | None = None

    @field_validator("phone")
    @classmethod
    def phone_digits(cls, value: str) -> str:
        digits = "".join(ch for ch in value if ch.isdigit())
        if len(digits) != 10:
            raise ValueError("Phone number must be 10 digits")
        return digits

    @field_validator("role")
    @classmethod
    def role_ok(cls, value: str) -> str:
        key = value.strip().lower().replace(" ", "_")
        aliases = {
            "farmer": "farmer",
            "agri_officer": "agri_officer",
            "agriofficer": "agri_officer",
            "fertilizer_dealer": "fertilizer_dealer",
            "fertilizerdealer": "fertilizer_dealer",
            "admin": "admin",
        }
        if key not in aliases:
            raise ValueError("Invalid role")
        return aliases[key]

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, value: str, info) -> str:
        password = info.data.get("password")
        if password and value != password:
            raise ValueError("Password and Confirm Password must match")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
