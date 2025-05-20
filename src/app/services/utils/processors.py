import logging
from typing import Callable, Any

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel


logger = logging.getLogger(__name__)


async def process_db_transaction(
    transaction_func: Callable, session: AsyncSession
) -> Any:
    """
    Executes a database transaction function and handles exceptions.

    Args:
        transaction_func (Callable): The function to execute within the transaction.
        session (AsynSession): The SQLAlchemy database session.

    Returns:
        Any: The result of the transaction function if successful.

    Raises:
        HTTPException: If an IntegrityError or SQLAlchemyError occurs during the transaction.
    """
    try:
        return await transaction_func()
    except IntegrityError as e:
        await session.rollback()
        logger.error(f"Integrity error: {str(e)}")
        raise HTTPException(
            detail=f"Database conflict occurred: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Unexpected DB error: {str(e)}")
        raise HTTPException(
            detail=f"{str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        await session.rollback()
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            detail=f"An unexpected error occurred: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
