import pytest
from unittest.mock import AsyncMock
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.administrator.admin_queries import test_call, add_specialization


@pytest.mark.asyncio
async def test_messages():
    mock = AsyncMock(spec=Message)


    mock.answer = AsyncMock()
    mock.text = 'Да'
    await test_call(mock)
    # print(mock.call_args)
    mock.answer.assert_called_once_with('No')


@pytest.mark.asyncio
async def test_add_specialization():
    mock = AsyncMock(spec=CallbackQuery)
    mock_state = AsyncMock(spec=FSMContext)
    mock.data = 'add_specialization'
    mock.message = AsyncMock()
    mock.message.answer = AsyncMock()
    await add_specialization(mock, mock_state)
    mock.message.answer.assert_called_once_with(
        'Наберите код и название специальности, например:\n'
        '<i>18.03.01 «Инновационные технологии международных нефтегазовых корпораций»</i>',
        parse_mode='HTML'
    )