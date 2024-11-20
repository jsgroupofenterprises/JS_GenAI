from dataclasses import dataclass
from typing import List

@dataclass
class FunctionCall:
    function_name: str
    component: str
    parameters: List[str]
    return_type: str
    is_api: bool = False
    line_number: int = 0
    context_before: str = ""
    context_after: str = ""