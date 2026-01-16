from fastapi import HTTPException, status


class MoleculeException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class MoleculeNotFoundException(MoleculeException):
    def __init__(self, molecule_id: int):
        super().__init__(
            detail=f"Molecule with id {molecule_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class InvalidSmilesException(MoleculeException):
    def __init__(self, smiles: str):
        super().__init__(
            detail=f"Invalid SMILES format: {smiles}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class DuplicateMoleculeException(MoleculeException):
    def __init__(self, smiles: str):
        super().__init__(
            detail=f"Molecule with SMILES {smiles} already exists",
            status_code=status.HTTP_409_CONFLICT,
        )


class ValidationError(MoleculeException):
    def __init__(self, detail: str):
        super().__init__(
            detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
        )
