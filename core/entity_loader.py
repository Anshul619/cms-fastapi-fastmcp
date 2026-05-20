import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


BASE_DIR = Path(__file__).resolve().parent.parent
ENTITY_PATH = BASE_DIR / "entities"


class EntityFieldDefinition(BaseModel):
    name: str
    type: Literal["string", "text", "integer", "float", "boolean", "datetime"]
    required: bool = False
    default: Any | None = None
    max_length: int | None = None
    min_length: int | None = None
    pattern: str | None = None
    minimum: int | float | None = None
    maximum: int | float | None = None
    enum: list[Any] | None = None

    @model_validator(mode="after")
    def validate_field(self) -> "EntityFieldDefinition":
        if self.name == "id":
            raise ValueError("Field name 'id' is reserved.")

        if self.type not in {"string", "text"} and (self.max_length is not None or self.min_length is not None):
            raise ValueError("min_length and max_length are only supported for string and text fields.")

        if self.type not in {"string", "text"} and self.pattern is not None:
            raise ValueError("pattern is only supported for string and text fields.")

        if self.type not in {"integer", "float"} and (self.minimum is not None or self.maximum is not None):
            raise ValueError("minimum and maximum are only supported for integer and float fields.")

        if self.min_length is not None and self.max_length is not None and self.min_length > self.max_length:
            raise ValueError("min_length cannot be greater than max_length.")

        if self.minimum is not None and self.maximum is not None and self.minimum > self.maximum:
            raise ValueError("minimum cannot be greater than maximum.")

        if self.enum is not None:
            if len(self.enum) == 0:
                raise ValueError("enum must contain at least one value.")

            unsupported_enum_types = {"datetime", "boolean"}
            if self.type in unsupported_enum_types:
                raise ValueError(f"enum is not supported for {self.type} fields.")

            if self.default is not None and self.default not in self.enum:
                raise ValueError("default must be one of the enum values.")

        return self


class EntityDefinition(BaseModel):
    entity: str
    table_name: str
    fields: list[EntityFieldDefinition] = Field(default_factory=list)

    @property
    def resource_name(self) -> str:
        return self.entity

    @property
    def class_name(self) -> str:
        return "".join(part.capitalize() for part in self.entity.split("_"))

    @model_validator(mode="after")
    def validate_entity(self) -> "EntityDefinition":
        field_names = [field.name for field in self.fields]
        if len(field_names) != len(set(field_names)):
            raise ValueError(f"Entity '{self.entity}' contains duplicate field names.")

        return self


def load_entities(entity_path: Path = ENTITY_PATH) -> list[EntityDefinition]:
    entities: list[EntityDefinition] = []

    if not entity_path.exists():
        return entities

    for file_path in sorted(entity_path.glob("*.json")):
        with file_path.open("r", encoding="utf-8") as file_handle:
            raw_entity = json.load(file_handle)

        entities.append(EntityDefinition.model_validate(raw_entity))

    _validate_unique_entities(entities)
    return entities


def _validate_unique_entities(entities: list[EntityDefinition]) -> None:
    entity_names = [entity.entity for entity in entities]
    table_names = [entity.table_name for entity in entities]

    if len(entity_names) != len(set(entity_names)):
        raise ValueError("Duplicate entity names found in entity definitions.")

    if len(table_names) != len(set(table_names)):
        raise ValueError("Duplicate table names found in entity definitions.")