from app.db.session import Base
from .DataStorage import *
from .UserBase import *
from .Service import *

# Automatically populate __all__ to include all classes inheriting from Base
__all__ = [
    name for name, obj in globals().items()
    if isinstance(obj, type) and issubclass(obj, Base) and obj is not Base
]