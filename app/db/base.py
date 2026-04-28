from sqlalchemy.orm import declarative_base

Base = declarative_base()

from app.models.refresh_token import RefreshToken  # noqa: F401,E402
from app.models.role_permission import RolePermission  # noqa: F401,E402
from app.models.school import School  # noqa: F401,E402
from app.models.user import User  # noqa: F401,E402