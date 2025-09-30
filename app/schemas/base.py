from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        model_dump_by_alias=True,
        use_enum_values=True,
    )

    def model_dump(self, **kwargs) -> dict:
        return super().model_dump(by_alias=True, **kwargs)

    def model_dump_snake_case(self, **kwargs) -> dict:
        return super().model_dump(by_alias=False, **kwargs)
