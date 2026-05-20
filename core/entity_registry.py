from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field, create_model
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, select
from sqlalchemy.orm import Session

from core.database import Base, get_db
from core.entity_loader import EntityDefinition, EntityFieldDefinition, load_entities


class ORMReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


@dataclass(frozen=True)
class EntityRuntime:
    definition: EntityDefinition
    model: type[Base]
    create_schema: type[BaseModel]
    update_schema: type[BaseModel]
    read_schema: type[BaseModel]
    router: APIRouter


class EntityRegistry:
    def __init__(self) -> None:
        self.entities: dict[str, EntityRuntime] = {}
        self._built = False

    def build(self) -> "EntityRegistry":
        if self._built:
            return self

        for definition in load_entities():
            runtime = self._build_runtime(definition)
            self.entities[definition.resource_name] = runtime

        self._built = True
        return self

    @property
    def routers(self) -> list[APIRouter]:
        return [runtime.router for runtime in self.entities.values()]

    def _build_runtime(self, definition: EntityDefinition) -> EntityRuntime:
        model = self._build_model(definition)
        create_schema = self._build_create_schema(definition)
        update_schema = self._build_update_schema(definition)
        read_schema = self._build_read_schema(definition)
        router = self._build_router(definition, model, create_schema, update_schema, read_schema)
        return EntityRuntime(definition, model, create_schema, update_schema, read_schema, router)

    def _build_model(self, definition: EntityDefinition) -> type[Base]:
        attributes: dict[str, Any] = {
            "__tablename__": definition.table_name,
            "id": Column(Integer, primary_key=True),
        }

        for field in definition.fields:
            column_kwargs: dict[str, Any] = {"nullable": not field.required}
            if field.default is not None:
                column_kwargs["default"] = field.default

            attributes[field.name] = Column(self._sqlalchemy_type(field), **column_kwargs)

        return type(definition.class_name, (Base,), attributes)

    def _build_create_schema(self, definition: EntityDefinition) -> type[BaseModel]:
        fields: dict[str, tuple[Any, Any]] = {}
        for field in definition.fields:
            fields[field.name] = self._pydantic_field(field, partial=False)

        return create_model(f"{definition.class_name}Create", **fields)

    def _build_update_schema(self, definition: EntityDefinition) -> type[BaseModel]:
        fields: dict[str, tuple[Any, Any]] = {}
        for field in definition.fields:
            fields[field.name] = self._pydantic_field(field, partial=True)

        return create_model(f"{definition.class_name}Update", **fields)

    def _build_read_schema(self, definition: EntityDefinition) -> type[BaseModel]:
        fields: dict[str, tuple[Any, Any]] = {"id": (int, ...)}

        for field in definition.fields:
            python_type = self._python_type(field)
            if not field.required and field.default is None:
                fields[field.name] = (python_type | None, None)
            elif field.default is not None:
                fields[field.name] = (python_type, field.default)
            else:
                fields[field.name] = (python_type, ...)

        return create_model(f"{definition.class_name}Read", __base__=ORMReadSchema, **fields)

    def _build_router(
        self,
        definition: EntityDefinition,
        model: type[Base],
        create_schema: type[BaseModel],
        update_schema: type[BaseModel],
        read_schema: type[BaseModel],
    ) -> APIRouter:
        router = APIRouter(prefix=f"/{definition.resource_name}", tags=[definition.resource_name])
        list_response_model = list[read_schema]
        entity_label = definition.resource_name

        def get_or_404(item_id: int, db: Session):
            instance = db.get(model, item_id)
            if instance is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{entity_label} {item_id} not found")
            return instance

        @router.post(
            "/",
            response_model=read_schema,
            status_code=status.HTTP_201_CREATED,
            name=f"create_{definition.resource_name}",
        )
        def create_item(payload: create_schema, db: Session = Depends(get_db)):
            instance = model(**payload.model_dump(exclude_unset=True))
            db.add(instance)
            db.commit()
            db.refresh(instance)
            return instance

        @router.get("/", response_model=list_response_model, name=f"list_{definition.resource_name}")
        def list_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
            statement = select(model).offset(skip).limit(limit)
            return db.scalars(statement).all()

        @router.get("/{item_id}", response_model=read_schema, name=f"get_{definition.resource_name}")
        def get_item(item_id: int, db: Session = Depends(get_db)):
            return get_or_404(item_id, db)

        @router.put("/{item_id}", response_model=read_schema, name=f"replace_{definition.resource_name}")
        def replace_item(item_id: int, payload: create_schema, db: Session = Depends(get_db)):
            instance = get_or_404(item_id, db)
            for field_name, value in payload.model_dump(exclude_unset=True).items():
                setattr(instance, field_name, value)

            db.commit()
            db.refresh(instance)
            return instance

        @router.patch("/{item_id}", response_model=read_schema, name=f"update_{definition.resource_name}")
        def update_item(item_id: int, payload: update_schema, db: Session = Depends(get_db)):
            instance = get_or_404(item_id, db)
            for field_name, value in payload.model_dump(exclude_unset=True).items():
                setattr(instance, field_name, value)

            db.commit()
            db.refresh(instance)
            return instance

        @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, name=f"delete_{definition.resource_name}")
        def delete_item(item_id: int, db: Session = Depends(get_db)):
            instance = get_or_404(item_id, db)
            db.delete(instance)
            db.commit()
            return Response(status_code=status.HTTP_204_NO_CONTENT)

        return router

    def _pydantic_field(self, field: EntityFieldDefinition, partial: bool) -> tuple[Any, Any]:
        python_type = self._python_type(field)
        field_info = self._field_info(field)

        if partial:
            return (python_type | None, Field(default=None, **field_info))

        if field.required and field.default is None:
            return (python_type, Field(..., **field_info))

        if field.default is not None:
            return (python_type, Field(default=field.default, **field_info))

        return (python_type | None, Field(default=None, **field_info))

    def _field_info(self, field: EntityFieldDefinition) -> dict[str, Any]:
        field_info: dict[str, Any] = {}

        if field.min_length is not None:
            field_info["min_length"] = field.min_length
        if field.max_length is not None:
            field_info["max_length"] = field.max_length
        if field.pattern is not None:
            field_info["pattern"] = field.pattern
        if field.minimum is not None:
            field_info["ge"] = field.minimum
        if field.maximum is not None:
            field_info["le"] = field.maximum
        return field_info

    def _sqlalchemy_type(self, field: EntityFieldDefinition):
        if field.type == "string":
            return String(field.max_length or 255)
        if field.type == "text":
            return Text()
        if field.type == "integer":
            return Integer()
        if field.type == "float":
            return Float()
        if field.type == "boolean":
            return Boolean()
        if field.type == "datetime":
            return DateTime(timezone=True)

        raise ValueError(f"Unsupported field type: {field.type}")

    def _python_type(self, field: EntityFieldDefinition):
        if field.enum is not None:
            return Literal.__getitem__(tuple(field.enum))

        if field.type in {"string", "text"}:
            return str
        if field.type == "integer":
            return int
        if field.type == "float":
            return float
        if field.type == "boolean":
            return bool
        if field.type == "datetime":
            return datetime

        raise ValueError(f"Unsupported field type: {field.type}")


entity_registry = EntityRegistry()