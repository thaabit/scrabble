from abc import ABC, abstractmethod
from sqlmodel import SQLModel

class SQLModelBase(SQLModel, ABC):
    def __init__(self, **kwargs):
        self.pre_init()
        super().__init__(**kwargs)
        self.post_init()

    def pre_init(self): pass
    def post_init(self): pass

    def update(self, **kwargs):
        self.pre_update()
        super().update(**kwargs)
        self.post_update()

    def pre_update(self): pass
    def post_update(self): pass
