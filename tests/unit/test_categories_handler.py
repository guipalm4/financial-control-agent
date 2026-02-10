"""Unit tests for category CRUD handlers (FEAT-011).

Includes add_categoria, list_categorias and delete_categoria handlers.
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlmodel import Session, SQLModel, create_engine, select

from src.bot.handlers.auth_helpers import get_authenticated_user
from src.db.seed import DEFAULT_CATEGORY_NAMES, seed_default_categories
from src.models import Category, User
from src.services.auth import hash_pin


@pytest.mark.asyncio
async def test_add_categoria_requires_auth() -> None:
    """add_categoria_handler: when not authenticated, replies and returns."""
    from src.bot.handlers.categories import add_categoria_handler

    test_engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(test_engine)

    update = MagicMock()
    update.effective_user = MagicMock(id=99999)
    update.message = MagicMock(text="/add_categoria Mercado", reply_text=AsyncMock())
    context = MagicMock()

    with patch("src.bot.handlers.auth_helpers.engine", test_engine):
        result = await get_authenticated_user(update)
    assert result is None

    # If not authenticated, handler should early-return without raising
    with patch("src.bot.handlers.auth_helpers.engine", test_engine):
        await add_categoria_handler(update, context)


@pytest.mark.asyncio
async def test_add_categoria_creates_custom_category() -> None:
    """Happy path: /add_categoria Mercado creates a new custom category."""
    from src.bot.handlers.categories import add_categoria_handler

    test_engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(test_engine)

    # Create authenticated user
    with Session(test_engine) as session:
        user = User(
            telegram_id=55555,
            pin_hash=hash_pin("1234"),
            last_login=datetime.now(UTC),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        user_id = user.id
        assert user_id is not None

    update = MagicMock()
    update.effective_user = MagicMock(id=55555)
    update.message = MagicMock(text="/add_categoria Mercado", reply_text=AsyncMock())
    context = MagicMock()

    with (
        patch("src.bot.handlers.auth_helpers.engine", test_engine),
        patch("src.bot.handlers.categories.engine", test_engine),
    ):
        await add_categoria_handler(update, context)

    # Check DB: one custom category plus no defaults (seed not called here)
    with Session(test_engine) as session:
        stmt = select(Category).where(Category.user_id == user_id)
        categories = list(session.exec(stmt).all())
    assert len(categories) == 1
    assert categories[0].name == "Mercado"
    assert categories[0].is_default is False

    text = update.message.reply_text.call_args[0][0]
    assert "✅ Categoria cadastrada" in text
    assert "Mercado" in text


@pytest.mark.asyncio
async def test_list_categorias_includes_default_and_custom() -> None:
    """list_categorias_handler: lists default + custom categories."""
    from src.bot.handlers.categories import list_categorias_handler

    test_engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(test_engine)

    # Create user and seed defaults + one custom category
    with Session(test_engine) as session:
        user = User(
            telegram_id=77777,
            pin_hash=hash_pin("1234"),
            last_login=datetime.now(UTC),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        user_id = user.id
        assert user_id is not None

        seed_default_categories(session, user_id)
        session.add(
            Category(
                user_id=user_id,
                name="Farmácia",
                is_default=False,
            )
        )
        session.commit()

    update = MagicMock()
    update.effective_user = MagicMock(id=77777)
    update.message = MagicMock(text="/list_categorias", reply_text=AsyncMock())
    context = MagicMock()

    with (
        patch("src.bot.handlers.auth_helpers.engine", test_engine),
        patch("src.bot.handlers.categories.engine", test_engine),
    ):
        await list_categorias_handler(update, context)

    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    # All defaults plus the custom one should appear
    for name in DEFAULT_CATEGORY_NAMES:
        assert name in text
    assert "Farmácia" in text


@pytest.mark.asyncio
async def test_delete_categoria_cannot_delete_default() -> None:
    """/delete_categoria on default category -> CATEGORY.CANNOT_DELETE_DEFAULT."""
    from src.bot.handlers.categories import delete_categoria_handler

    test_engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(test_engine)

    # Create user and seed default categories
    with Session(test_engine) as session:
        user = User(
            telegram_id=88888,
            pin_hash=hash_pin("1234"),
            last_login=datetime.now(UTC),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        user_id = user.id
        assert user_id is not None

        seed_default_categories(session, user_id)
        stmt = (
            select(Category).where(Category.user_id == user_id).where(Category.is_default == True)  # noqa: E712
        )
        default_category = session.exec(stmt).first()
        assert default_category is not None
        default_id = default_category.id
        assert default_id is not None

    update = MagicMock()
    update.effective_user = MagicMock(id=88888)
    update.message = MagicMock(text=f"/delete_categoria {default_id}", reply_text=AsyncMock())
    context = MagicMock()

    with (
        patch("src.bot.handlers.auth_helpers.engine", test_engine),
        patch("src.bot.handlers.categories.engine", test_engine),
    ):
        await delete_categoria_handler(update, context)

    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "CATEGORY.CANNOT_DELETE_DEFAULT" in text


@pytest.mark.asyncio
async def test_delete_categoria_soft_deletes_custom() -> None:
    """/delete_categoria on custom category marks deleted_at."""
    from src.bot.handlers.categories import delete_categoria_handler

    test_engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(test_engine)

    # Create user and one custom category
    with Session(test_engine) as session:
        user = User(
            telegram_id=99999,
            pin_hash=hash_pin("1234"),
            last_login=datetime.now(UTC),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        user_id = user.id
        assert user_id is not None

        created_category = Category(user_id=user_id, name="Uber", is_default=False)
        session.add(created_category)
        session.commit()
        session.refresh(created_category)
        category_id = created_category.id
        assert category_id is not None

    update = MagicMock()
    update.effective_user = MagicMock(id=99999)
    update.message = MagicMock(text=f"/delete_categoria {category_id}", reply_text=AsyncMock())
    context = MagicMock()

    with (
        patch("src.bot.handlers.auth_helpers.engine", test_engine),
        patch("src.bot.handlers.categories.engine", test_engine),
    ):
        await delete_categoria_handler(update, context)

    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "✅ Categoria" in text and "Uber" in text

    with Session(test_engine) as session:
        stmt = select(Category).where(Category.id == category_id)
        category = session.exec(stmt).first()
        assert category is not None
        assert category.deleted_at is not None
