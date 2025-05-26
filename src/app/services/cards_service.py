
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.persistence.cards.card import Card
from app.schemas.card import CardCreate, CardResponse
from app.services.utils.processors import process_db_transaction

async def create_card(
    session: AsyncSession,
    user_id: UUID,        # <— now a UUID
    card: CardCreate
) -> CardResponse:
    async def _create():
        db_obj = Card.model_validate(
            card,
            update={"user_id": user_id}
        )
        session.add(db_obj)

        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ValueError("A card with this number already exists")

        await session.refresh(db_obj)
        return CardResponse.create(db_obj)

    return await process_db_transaction(session=session, func=_create)
