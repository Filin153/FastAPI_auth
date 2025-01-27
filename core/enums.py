from enum import Enum


class RoleEnum(str, Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"

class StatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"

class TotpKeyType(str, Enum):
    base32 = "base32"
    hex = "hex"

class QrTypeSaveEnum(str, Enum):
    SVG = "svg"
    BYTES = "bytes"