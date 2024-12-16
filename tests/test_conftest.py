# test_users.py

from builtins import len
import pytest
from httpx import AsyncClient
from sqlalchemy.future import select

from app.models.user_model import User, UserRole
from app.utils.security import verify_password
from app.utils.nickname_gen import generate_nickname

@pytest.mark.asyncio
async def test_user_creation(db_session, verified_user):
    """Test that a user is correctly created and stored in the database."""
    result = await db_session.execute(select(User).filter_by(email=verified_user.email))
    stored_user = result.scalars().first()
    assert stored_user is not None
    assert stored_user.email == verified_user.email
    assert verify_password("MySuperPassword$1234", stored_user.hashed_password)

# Apply similar corrections to other test functions
@pytest.mark.asyncio
async def test_locked_user(db_session, locked_user):
    result = await db_session.execute(select(User).filter_by(email=locked_user.email))
    stored_user = result.scalars().first()
    assert stored_user.is_locked

@pytest.mark.asyncio
async def test_verified_user(db_session, verified_user):
    result = await db_session.execute(select(User).filter_by(email=verified_user.email))
    stored_user = result.scalars().first()
    assert stored_user.email_verified

@pytest.mark.asyncio
async def test_user_role(db_session, admin_user):
    result = await db_session.execute(select(User).filter_by(email=admin_user.email))
    stored_user = result.scalars().first()
    assert stored_user.role == UserRole.ADMIN

@pytest.mark.asyncio
async def test_bulk_user_creation_performance(db_session, users_with_same_role_50_users):
    result = await db_session.execute(select(User).filter_by(role=UserRole.AUTHENTICATED))
    users = result.scalars().all()
    assert len(users) == 50

@pytest.mark.asyncio
async def test_password_hashing(user):
    assert verify_password("MySuperPassword$1234", user.hashed_password)

@pytest.mark.asyncio
async def test_user_unlock(db_session, locked_user):
    locked_user.unlock_account()
    await db_session.commit()
    result = await db_session.execute(select(User).filter_by(email=locked_user.email))
    updated_user = result.scalars().first()
    assert not updated_user.is_locked

@pytest.mark.asyncio
async def test_update_professional_status(db_session, verified_user):
    verified_user.update_professional_status(True)
    await db_session.commit()
    result = await db_session.execute(select(User).filter_by(email=verified_user.email))
    updated_user = result.scalars().first()
    assert updated_user.is_professional
    assert updated_user.professional_status_updated_at is not None

@pytest.mark.asyncio
def test_nickname_number_range():
    nickname = generate_nickname()
    number = int(nickname.split('_')[2])
    assert 0 <= number <= 999, f"Number '{number}' is not in the range 0-999"

@pytest.mark.asyncio
def test_nickname_animal():
    animals = ["panda", "fox", "raccoon", "koala", "lion"]
    nickname = generate_nickname()
    animal = nickname.split('_')[1]
    assert animal in animals, f"Animal '{animal}' is not in the list of valid animals"

@pytest.mark.asyncio
def test_nickname_adjective():
    adjectives = ["clever", "jolly", "brave", "sly", "gentle"]
    nickname = generate_nickname()
    adjective = nickname.split('_')[0]
    assert adjective in adjectives, f"Adjective '{adjective}' is not in the list of valid adjectives"