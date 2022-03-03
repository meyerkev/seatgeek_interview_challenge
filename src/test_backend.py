# pylint: disable=W0613, W0621
from collections import namedtuple
from unittest import mock
import pytest


import backend


@pytest.fixture
def free_seat():
    return backend.Seat('test', backend.SeatStatus.FREE)


@pytest.fixture
def reserved_seat():
    return backend.Seat('test', backend.SeatStatus.RESERVED)


@pytest.fixture
def sold_seat():
    return backend.Seat('test', backend.SeatStatus.SOLD)


def test_empty_seat():
    s = backend.Seat('my_seat', backend.SeatStatus.FREE)
    assert s.seat_id == 'my_seat'
    assert s.status == backend.SeatStatus.FREE


def test_reserve_free_seat(free_seat):
    assert free_seat.reserve() == backend.ReturnStatus.OK
    assert free_seat.status == backend.SeatStatus.RESERVED


def test_reserve_reserved_seat(reserved_seat):
    assert reserved_seat.reserve() == backend.ReturnStatus.FAIL
    assert reserved_seat.status == backend.SeatStatus.RESERVED


def test_reserve_sold_seat(sold_seat):
    assert sold_seat.reserve() == backend.ReturnStatus.FAIL
    assert sold_seat.status == backend.SeatStatus.SOLD


def test_buy_free_seat(free_seat):
    assert free_seat.buy() == backend.ReturnStatus.FAIL
    assert free_seat.status == backend.SeatStatus.FREE


def test_buy_reserved_seat(reserved_seat):
    assert reserved_seat.buy() == backend.ReturnStatus.OK
    assert reserved_seat.status == backend.SeatStatus.SOLD


def test_buy_sold_seat(sold_seat):
    assert sold_seat.buy() == backend.ReturnStatus.FAIL
    assert sold_seat.status == backend.SeatStatus.SOLD


def test_reserve_then_buy_free_seat(free_seat):
    assert free_seat.reserve() == backend.ReturnStatus.OK
    assert free_seat.status == backend.SeatStatus.RESERVED
    assert free_seat.buy() == backend.ReturnStatus.OK
    assert free_seat.status == backend.SeatStatus.SOLD


def test_reserve_then_buy_reserved_seat(reserved_seat):
    assert reserved_seat.reserve() == backend.ReturnStatus.FAIL
    assert reserved_seat.status == backend.SeatStatus.RESERVED
    assert reserved_seat.buy() == backend.ReturnStatus.OK
    assert reserved_seat.status == backend.SeatStatus.SOLD


def test_reserve_then_buy_sold_seat(sold_seat):
    assert sold_seat.reserve() == backend.ReturnStatus.FAIL
    assert sold_seat.status == backend.SeatStatus.SOLD
    assert sold_seat.buy() == backend.ReturnStatus.FAIL
    assert sold_seat.status == backend.SeatStatus.SOLD


@pytest.fixture
def mock_global_seatdb(monkeypatch):
    assert not backend.SEAT_DB
    monkeypatch.setattr(backend, "SEAT_DB", {})


def test_empty_seat_db(mock_global_seatdb):
    pass


@pytest.fixture
def mock_seat(monkeypatch):
    mock_seat_class = mock.Mock()
    mock_seat_class.return_value = mock.Mock()
    monkeypatch.setattr(backend, "Seat", mock_seat_class)
    return mock_seat_class


def test_take_action_invalid_action(mock_global_seatdb, mock_seat):
    backend.take_action("INVALID", "who_cares_really")

    mock_seat.return_value.assert_not_called()
    assert not backend.SEAT_DB


def test_take_action_query_new_seat(mock_global_seatdb):
    assert not backend.SEAT_DB
    seat_id = "test123"

    assert backend.take_action("QUERY", seat_id) == backend.SeatStatus.FREE

    stored_seat = backend.SEAT_DB[seat_id]
    assert stored_seat.seat_id == seat_id
    assert stored_seat.status == backend.SeatStatus.FREE
    assert len(backend.SEAT_DB) == 1


def test_take_action_reserve_new_seat(mock_global_seatdb):
    assert not backend.SEAT_DB
    seat_id = "test123"

    assert backend.take_action("RESERVE", seat_id) == backend.ReturnStatus.OK

    stored_seat = backend.SEAT_DB[seat_id]
    assert stored_seat.seat_id == seat_id
    assert stored_seat.status == backend.SeatStatus.RESERVED
    assert len(backend.SEAT_DB) == 1


def test_take_action_buy_new_seat(mock_global_seatdb):
    assert not backend.SEAT_DB
    seat_id = "test123"

    assert backend.take_action("BUY", seat_id) == backend.ReturnStatus.FAIL

    stored_seat = backend.SEAT_DB[seat_id]
    assert stored_seat.seat_id == seat_id
    assert stored_seat.status == backend.SeatStatus.FREE
    assert len(backend.SEAT_DB) == 1


def test_full_workflow(mock_global_seatdb):
    assert not backend.SEAT_DB
    seat_id = "test123"

    assert backend.take_action("QUERY", seat_id) == backend.SeatStatus.FREE
    stored_seat = backend.SEAT_DB[seat_id]
    assert stored_seat.seat_id == seat_id
    assert stored_seat.status == backend.SeatStatus.FREE

    assert backend.take_action("BUY", seat_id) == backend.ReturnStatus.FAIL
    assert stored_seat.status == backend.SeatStatus.FREE

    assert backend.take_action("RESERVE", seat_id) == backend.ReturnStatus.OK
    assert stored_seat.status == backend.SeatStatus.RESERVED

    assert backend.take_action("QUERY", seat_id) == backend.SeatStatus.RESERVED
    assert stored_seat.status == backend.SeatStatus.RESERVED

    assert backend.take_action("RESERVE", seat_id) == backend.ReturnStatus.FAIL
    assert stored_seat.status == backend.SeatStatus.RESERVED

    assert backend.take_action("BUY", seat_id) == backend.ReturnStatus.OK
    assert stored_seat.status == backend.SeatStatus.SOLD

    assert backend.take_action("QUERY", seat_id) == backend.SeatStatus.SOLD
    assert stored_seat.status == backend.SeatStatus.SOLD

    assert len(backend.SEAT_DB) == 1


def test_multiple_seats(mock_global_seatdb, mock_seat):
    assert not backend.SEAT_DB
    mock_seat.return_value.status = "TEST"

    for _id in [1, 2, 1, 3, 1, 1, 1, 1, 1]:
        assert backend.take_action("QUERY", _id) == "TEST"
    assert mock_seat.call_count == 3
    assert set(backend.SEAT_DB.keys()) == {1, 2, 3}


def make_message(action, seat):
    return f'{action}: {seat}\n'


mock_return = namedtuple("mock_return", ["name"])


@pytest.fixture
def mock_take_action(monkeypatch):
    m = mock.Mock(return_value=mock_return(name="MOCK"))
    monkeypatch.setattr(backend, "take_action", m)
    return m


def test_process_message_works(mock_take_action):
    action = "TEST_ACTION"
    seat = "test123"
    message = make_message(action, seat)

    assert backend.process_message(message) == "MOCK"
    mock_take_action.assert_called_once_with(action, seat)


def test_process_message_bad(mock_take_action):
    message = "BLAH BLAH BLAH"

    assert backend.process_message(message) == "FAIL"
    mock_take_action.assert_not_called()
