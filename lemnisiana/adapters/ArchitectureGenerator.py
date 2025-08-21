from typing import List, Dict, Any, Protocol

class ArchitectureGenerator(Protocol):
    def propose(self, n: int = 1) -> List[Dict[str, Any]]: ...
