from app.persistence.cards.card import Card
from app.schemas.card import CardCreate, CardResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.utils.processors import process_db_transaction


async def create_card(session: AsyncSession, card: CardCreate) -> CardResponse:
    async def _create():
        db_obj = Card.model_validate(card)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return CardResponse.create(db_obj)

    return await process_db_transaction(
        session=session,
        func=_create,
    )
