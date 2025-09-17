from typing import Any


class Level:
    def __init__(self, level_id: int, parameters: dict[str, Any]):
        self.level_id = level_id
        self.parameters = parameters
        self.stimulus_dict = None

    def get_parameters(self) -> dict[str, Any]:
        return self.parameters
