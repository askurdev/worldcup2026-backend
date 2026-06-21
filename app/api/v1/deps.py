from fastapi import Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db


class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number (1-indexed)"),
        page_size: int = Query(
            settings.DEFAULT_PAGE_SIZE,
            ge=1,
            le=settings.MAX_PAGE_SIZE,
            alias="pageSize",
            description="Number of items per page",
        ),
    ):
        self.page = page
        self.page_size = page_size
