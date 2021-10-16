from abc import abstractmethod, ABC


class InterfaceTestAPI(ABC):
    """
    All test cases should cover at least these 3 scenarios.
    """

    @abstractmethod
    def test_missing_params(self) -> None:
        pass

    @abstractmethod
    def test_bad_params(self) -> None:
        pass

    @abstractmethod
    def test_valid_params(self) -> None:
        pass
