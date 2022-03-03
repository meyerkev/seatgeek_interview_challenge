"""
Our backend server and implicit database
"""
from enum import Enum
import logging
import threading

# CR: Should these be merged?


class SeatStatus(Enum):
    """
    For QUERY commands, the service should return:
    * FREE if the queried seat hasn't been previously reserved or bought
    * RESERVED if the seat has been reserved but not yet bought,
    * SOLD when the seat has already been bought
    """
    FREE = 1
    RESERVED = 2
    SOLD = 3


class ReturnStatus(Enum):
    """
    Query return values
    """
    OK = 4
    FAIL = 5


class Seat():
    """
    A seat is an id, a state, and a lock for threading purposes
    """

    def __init__(self, seat_id, status):
        self._seat_id = seat_id
        self._status = status
        # CR: This is a lot of locks.  Discuss alternate strategies (DB-level?)
        # TODO: Convert to read-write lock ala https://gist.github.com/tylerneylon/a7ff6017b7a1f9a506cf75aa23eacfd6  # pylint: disable=C0301
        self._lock = threading.Lock()

    @property
    def seat_id(self):
        return self._seat_id

    @property
    def status(self):
        with self._lock:
            return self._status

    def reserve(self):
        """
        For RESERVE commands, the service must return:
        * OK if the seat was previously FREE
        * FAIL otherwise
        """
        with self._lock:
            # Avoid using self.status while holding the lock!
            if self._status != SeatStatus.FREE:
                return ReturnStatus.FAIL
            self._status = SeatStatus.RESERVED
            return ReturnStatus.OK

    def buy(self):
        """
        For BUY commands, the service must return:
        * OK if the service was previously marked as RESERVED.
        * FAIL otherwise
        """
        with self._lock:
            if self._status != SeatStatus.RESERVED:
                return ReturnStatus.FAIL
            self._status = SeatStatus.SOLD
            return ReturnStatus.OK


# This would literally be a DB, so I don't feel awkward about it being a global
# Alt. would be singleton, especially if we use non-seat-level locking
SEAT_DB = {}
VALID_ACTIONS = ["QUERY", "RESERVE", "BUY"]


def take_action(action, seat_id):
    """
    Returns a status

    The server should return responses according to these rules:
    * We assume that any seat that has not been reserved or bought exists
      and is FREE
    * For RESERVE commands, the service must return OK if the seat was
      previously FREE. If the seat was in any other state, the response should
      be FAIL
    * For BUY commands, the service must return OK if the service was
      previously marked as RESERVED. If the seat was in any other state,
      the response should be FAIL
    * For QUERY commands, the service should return FREE if the queried seat
      hasn't been previously reserved or bought, RESERVED if the seat has been
      reserved but not yet bought, and SOLD when the seat has already been
      bought
    * The service should return FAIL for any unknown or invalid message it
      receives
    """
    if not action in VALID_ACTIONS:
        logging.info("Invalid action %s", action)
        return ReturnStatus.FAIL

    # Possible TODO: Can we do something interesting with
    # collections.defaultdict constructors?
    seat = SEAT_DB.get(seat_id)
    if seat is None:
        seat = Seat(seat_id, SeatStatus.FREE)
        SEAT_DB[seat_id] = seat

    if action == "QUERY":  # pylint: disable=R1705
        # SELECT status FROM seats WHERE seat_id==<seat_id>
        return seat.status
    elif action == "RESERVE":
        return seat.reserve()
    elif action == "BUY":
        return seat.buy()

    # You should never get here
    logging.warning("Valid Action %s was reported as invalid", action)
    return ReturnStatus.FAIL


def process_message(message):
    # This could be done with regex, but let's just run a split
    # Input string is ACTION: seat\n
    logging.debug("Message: %s", message)
    try:
        action, seat = message.split(": ")
        seat = seat.strip()
    except ValueError:  # No : , so list is of len 1 and cannot be split
        logging.info("Message %s could not be parsed", message)
        return ReturnStatus.FAIL.name

    return take_action(action, seat).name
