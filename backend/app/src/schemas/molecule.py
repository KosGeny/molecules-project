from pydantic import BaseModel, Field, field_validator
from typing import Optional
from ..utils.rdkit_utils import validate_smiles


class MoleculeBase(BaseModel):
    name: str = Field(..., min_length=2)
    smiles: str

    @field_validator("smiles")
    @classmethod
    def validate_smiles_str(cls, v):
        if not validate_smiles(v):
            raise ValueError(f"Invalid SMILES string: {v}")
        return v


class MoleculeCreate(MoleculeBase):
    pass


class MoleculeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2)
    smiles: Optional[str]

    @field_validator("smiles")
    @classmethod
    def validate_smiles_str(cls, v):
        if v is not None and not validate_smiles(v):
            raise ValueError(f"Invalid SMILES string: {v}")
        return v


class MoleculeResponse(MoleculeBase):
    id: int
    smiles: str

    class Config:
        from_attributes = True


class MoleculeSearchRequest(BaseModel):
    query: str = Field(..., description="Substructure SMILES pattern")
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0, description="Pagination offset")


class PaginatedResponse(BaseModel):
    items: list[MoleculeResponse]
    total: int
    page: int
    size: int
    pages: int


class PaginatedSearchResponse(PaginatedResponse):
    query: str
