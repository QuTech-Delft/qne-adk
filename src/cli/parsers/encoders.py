import json
from typing import Dict, Any


class JSONEncoder:
    """Class to use in place of apistar's default JSONEncoder

    This encoder will encode complex numbers z as an object {"re": x, "im": y} with x equal to the real part of z and y
    equal to the imaginary part of z.
    """
    media_type = "application/json"

    @staticmethod
    def encode_complex(z: complex) -> Dict[str, float]:
        if isinstance(z, complex):
            return {"re": z.real, "im": z.imag}
        raise TypeError(f"Object of type {z.__class__.__name__} is not JSON serializable.")

    @staticmethod
    def encode(options: Dict[str, Any], content: Dict[str, Any]) -> None:
        options["json"] = json.loads(json.dumps(content, default=JSONEncoder.encode_complex))
