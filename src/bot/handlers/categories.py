""" "Handlers for category CRUD: /add_categoria, /list_categorias, /delete_categoria (FEAT-011)."""

import logging
from datetime import UTC, datetime

from sqlalchemy import func
from sqlmodel import Session, select
from telegram import Update
from telegram.ext import ContextTypes

from src.bot.handlers.auth_helpers import get_authenticated_user
from src.db.engine import engine
from src.models import Category

logger = logging.getLogger(__name__)


async def add_categoria_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Create a new custom category for the authenticated user.

    Usage: /add_categoria <nome>
    """
    message = update.message
    if not message:
        return

    db_user = await get_authenticated_user(update)
    if db_user is None:
        return

    text = (message.text or "").strip()
    parts = text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await message.reply_text(
            "Uso: /add_categoria <nome>\n"
            "Exemplo: /add_categoria Farmácia\n"
            "code: CATEGORY.NAME_REQUIRED"
        )
        return

    raw_name = parts[1].strip()
    name = raw_name[:50]

    with Session(engine) as session:
        # Check duplicate (case-insensitive, not deleted, default or custom)
        stmt = (
            select(Category)
            .where(Category.user_id == db_user.id)
            .where(Category.deleted_at == None)  # noqa: E711
            .where(func.lower(Category.name) == name.lower())
        )
        existing = session.exec(stmt).first()
        if existing is not None:
            await message.reply_text(
                "❌ Já existe uma categoria com esse nome.\ncode: CATEGORY.DUPLICATE"
            )
            return

        category = Category(
            user_id=db_user.id,
            name=name,
            is_default=False,
        )
        session.add(category)
        session.commit()
        session.refresh(category)

    await message.reply_text(f"✅ Categoria cadastrada: {category.name} (ID: {category.id})")


async def list_categorias_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all (default + custom) active categories for the user."""
    message = update.message
    if not message:
        return

    db_user = await get_authenticated_user(update)
    if db_user is None:
        return

    with Session(engine) as session:
        stmt = (
            select(Category)
            .where(Category.user_id == db_user.id)
            .where(Category.deleted_at == None)  # noqa: E711
            .order_by(Category.is_default.desc(), Category.name)  # type: ignore[attr-defined]
        )
        categories = list(session.exec(stmt).all())

    if not categories:
        await message.reply_text(
            "📋 Você ainda não tem categorias cadastradas.\n"
            "As categorias padrão serão criadas automaticamente no primeiro uso."
        )
        return

    lines: list[str] = ["📋 Suas categorias:\n"]
    for c in categories:
        label = "padrão" if c.is_default else "personalizada"
        lines.append(f"• {c.name} ({label}) — ID: {c.id}")

    await message.reply_text("\n".join(lines))


async def delete_categoria_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Soft delete a custom category by id.

    Usage: /delete_categoria <id>
    """
    message = update.message
    if not message:
        return

    db_user = await get_authenticated_user(update)
    if db_user is None:
        return

    text = (message.text or "").strip()
    parts = text.split()
    if len(parts) < 2:
        await message.reply_text(
            "Uso: /delete_categoria <id>\nUse /list_categorias para ver os IDs das suas categorias."
        )
        return

    try:
        category_id = int(parts[1])
    except ValueError:
        await message.reply_text("❌ ID deve ser um número.\ncode: CATEGORY.NOT_FOUND")
        return

    category_name: str | None = None
    with Session(engine) as session:
        stmt = (
            select(Category)
            .where(Category.id == category_id)
            .where(Category.user_id == db_user.id)
            .where(Category.deleted_at == None)  # noqa: E711
        )
        category = session.exec(stmt).first()

        if category is None:
            await message.reply_text("❌ Categoria não encontrada.\ncode: CATEGORY.NOT_FOUND")
            return

        if category.is_default:
            await message.reply_text(
                "❌ Não é possível excluir categorias padrão.\ncode: CATEGORY.CANNOT_DELETE_DEFAULT"
            )
            return

        category_name = category.name
        category.deleted_at = datetime.now(UTC)
        session.add(category)
        session.commit()

    await message.reply_text(f'✅ Categoria "{category_name}" removida.')
