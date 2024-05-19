from __future__ import annotations
from datetime import datetime
from . import Constants
from pytz import timezone


class datetimezone():
    __timezone__ = timezone(Constants.DEFAULT_TIMEZONE)

    def __init__(self, dt:datetime) -> None:
        self.dt = self.recompile(dt)
        self.tz = self.__timezone__

    @classmethod
    def now(cls):
        return cls(datetime.now(cls.__timezone__))
    
    @classmethod
    def recompile(cls, dt:datetime, tz = None) -> datetime:
        if tz is None: tz = cls.__timezone__
        return datetime(
            dt.year, dt.month, dt.day,
            dt.hour, dt.minute, dt.second, dt.microsecond,
            tz, fold=dt.fold)
    
    @classmethod
    def set_tz(cls, tz):
        cls.__timezone__ = tz

    def get(self) -> datetime:
        if self.tz != self.__timezone__:
            self.dt = self.recompile(self.dt)
            self.tz = self.__timezone__
        return self.dt