from __future__ import annotations
from pydantic import BaseModel, ConfigDict


class VM(BaseModel):
    """
    Base model with JSON-friendly settings.
    """

    model_config = ConfigDict(
        frozen=False,
        populate_by_name=True,
        str_strip_whitespace=True,
        ser_json_inf_nan="null",
        validate_assignment=True,
        arbitrary_types_allowed=False,
        use_enum_values=True,
    )
