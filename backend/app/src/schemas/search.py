from pydantic import BaseModel, Field, field_validator
from typing import Optional
from ..utils.rdkit_utils import validate_smiles


class SubstructureSearch(BaseModel):
    smiles: str
    limit: Optional[int] = Field(100, ge=1, le=1000)

    @field_validator("smiles")
    @classmethod
    def validate_search_smiles(cls, v: str) -> str:
        if not validate_smiles(v):
            raise ValueError(f"Invalid SMILES query: {v}")
        return v
