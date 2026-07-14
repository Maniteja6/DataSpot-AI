"""
Shared base model that serializes to camelCase over the wire (matching the
frontend's TypeScript types) while still letting backend code construct
instances with normal snake_case keyword arguments.

FastAPI serializes response models with `by_alias=True` by default, so any
model built on CamelModel automatically returns camelCase JSON without
touching route handlers.
"""

from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
