"""
Utility functions related to databases.
"""
from functools import wraps
import random

from django.db import transaction


MYSQL_MAX_INT = (2 ** 31) - 1


def unnested_atomic(using=None, savepoint=True):

    connection = transaction.get_connection(using)
    #if connection.in_atomic_block:
    #    raise Exception("Cannot be nested {}", connection.savepoint_ids)

    # Bare decorator: @atomic -- although the first argument is called
    # `using`, it's actually the function being decorated.
    if callable(using):
        return transaction.Atomic(transaction.DEFAULT_DB_ALIAS, savepoint)(using)
    # Decorator: @atomic(...) or context manager: with atomic(...): ...
    else:
        return transaction.Atomic(using, savepoint)


def atomic_with_read_committed(func):
    """
    Decorator which executes the decorated function inside a transaction with isolation level set to READ COMMITTED.

    If the function returns a response the transaction is committed and if the function raises an exception the
    transaction is rolled back.

    Raises TransactionManagementError if there is already a transaction open.

    Note: This only works on MySQL.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):  # pylint: disable=missing-docstring

        connection = transaction.get_connection()
        if connection.vendor == 'mysql':
            # The isolation level cannot be changed while a transaction is in progress. So we close any existing one.
            if connection.in_atomic_block:
                raise transaction.TransactionManagementError('Cannot change isolation level. A transaction is open.')

            # This will set the transaction isolation level to READ COMMITTED for the next transaction.
            cursor = connection.cursor()
            cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")

        with transaction.commit_on_success():
            return func(*args, **kwargs)

    return wrapper


def generate_int_id(minimum=0, maximum=MYSQL_MAX_INT, used_ids=None):
    """
    Return a unique integer in the range [minimum, maximum], inclusive.
    """
    if used_ids is None:
        used_ids = []

    cid = random.randint(minimum, maximum)

    while cid in used_ids:
        cid = random.randint(minimum, maximum)

    return cid
