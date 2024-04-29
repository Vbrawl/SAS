import pytest
from sas_commons import SendMessageRule
from datetime import datetime


def test_SendMessageRule__init():
    smr = SendMessageRule() # No error
    smr2 = SendMessageRule(datetime(2000, 1, 1), datetime(2000, 1, 2)) # No error
    smr3 = SendMessageRule(datetime(2000, 1, 1), last_executed=datetime(2000, 1, 1)) # No error
    smr4 = SendMessageRule(last_executed=datetime(2000, 1, 1), end_date=datetime(2000, 1, 1))

    with pytest.raises(ValueError):
        smr5 = SendMessageRule(start_date=datetime(2000, 1, 2), end_date=datetime(2000, 1, 1))
    with pytest.raises(ValueError):
        smr6 = SendMessageRule(start_date=datetime(2000, 1, 2), last_executed=datetime(2000, 1, 1))
    with pytest.raises(ValueError):
        smr7 = SendMessageRule(end_date=datetime(2000, 1, 1), last_executed=datetime(2000, 1, 2))