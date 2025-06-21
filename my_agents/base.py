from abc import ABC, abstractmethod

class BaseAgent(ABC):
    @abstractmethod
    async def can_answer(self, question: str) -> bool:
        pass

    @abstractmethod
    async def answer(self, question: str) -> str:
        pass
