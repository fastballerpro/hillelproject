from apps.core.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String
import uuid


class Product(Base):
    title: Mapped[str] = mapped_column(unique=True)
    price: Mapped[int]
    description: Mapped[str] = mapped_column(default='')
    uuid_id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, nullable=False)
    main_image: Mapped[str]
    images: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)