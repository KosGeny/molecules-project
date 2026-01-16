from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ....db.base import get_db
from ...services.molecule_service import MoleculeService
from ...services.search_service import SearchService
from ...schemas.molecule import (
    MoleculeCreate,
    MoleculeUpdate,
    MoleculeResponse,
    MoleculeSearchRequest,
    PaginatedResponse,
    PaginatedSearchResponse,
)
from ...core.exceptions import MoleculeException, ValidationError
from ...utils.logger import app_logger
from fastapi import UploadFile, File
import csv
import io


def get_molecule_service(db: AsyncSession = Depends(get_db)) -> MoleculeService:
    return MoleculeService(db)


def get_search_service(db: AsyncSession = Depends(get_db)) -> SearchService:
    return SearchService(db)


router = APIRouter(prefix="/molecules", tags=["molecules"])


@router.post("/", response_model=MoleculeResponse)
async def create_molecule(
    molecule: MoleculeCreate,
    service: MoleculeService = Depends(get_molecule_service),
):
    try:
        created_molecule = await service.create_molecule(molecule)
        return MoleculeResponse.model_validate(created_molecule)
    except ValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except MoleculeException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/{molecule_id}", response_model=MoleculeResponse)
async def get_molecule(
    molecule_id: int,
    service: MoleculeService = Depends(get_molecule_service),
):
    try:
        molecule = await service.get_molecule(molecule_id)
        return MoleculeResponse.model_validate(molecule)
    except MoleculeException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.put("/{molecule_id}", response_model=MoleculeResponse)
async def update_molecule(
    molecule_id: int,
    molecule_update: MoleculeUpdate,
    service: MoleculeService = Depends(get_molecule_service),
):
    try:
        updated_molecule = await service.update_molecule(molecule_id, molecule_update)
        return MoleculeResponse.model_validate(updated_molecule)
    except MoleculeException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.delete("/{molecule_id}")
async def delete_molecule(
    molecule_id: int,
    service: MoleculeService = Depends(get_molecule_service),
):
    try:
        success = await service.delete_molecule(molecule_id)
        if success:
            return {"message": f"Molecule {molecule_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Molecule not found")
    except MoleculeException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/", response_model=PaginatedResponse)
async def get_molecules(
    skip: int = Query(0, ge=0),
    limit: int = Query(3, ge=1, le=1000),
    service: MoleculeService = Depends(get_molecule_service),
):
    try:
        molecules, total_count = await service.get_all_molecules(skip=skip, limit=limit)
        responses = [MoleculeResponse.model_validate(mol) for mol in molecules]

        pages = (total_count + limit - 1) // limit

        return PaginatedResponse(
            items=responses,
            total=total_count,
            page=(skip // limit) + 1,
            size=limit,
            pages=pages,
        )
    except MoleculeException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/search", response_model=PaginatedSearchResponse)
async def search_molecules(
    search_request: MoleculeSearchRequest,
    search_service: SearchService = Depends(get_search_service),
    service: MoleculeService = Depends(get_molecule_service),
):
    try:
        results, total_count = await search_service.substructure_search(
            query_smiles=search_request.query,
            limit=search_request.limit,
            offset=search_request.offset,
        )
        responses = [MoleculeResponse.model_validate(mol) for mol in results]

        pages = (total_count + search_request.limit - 1) // search_request.limit
        page = (search_request.offset // search_request.limit) + 1

        return PaginatedSearchResponse(
            items=responses,
            total=total_count,
            page=page,
            size=search_request.limit,
            pages=pages,
            query=search_request.query,
        )
    except MoleculeException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/upload")
async def upload_molecules(
    file: UploadFile = File(...),
    service: MoleculeService = Depends(get_molecule_service),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    contents = await file.read()

    decoded_content = contents.decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded_content))

    created_count = 0
    for row in reader:
        try:
            molecule_data = MoleculeCreate(
                name=row.get("name"), smiles=row.get("smiles", "")
            )
            await service.create_molecule(molecule_data)
            created_count += 1
        except Exception as e:
            app_logger.warning(f"Failed to create molecule from row: {row}, error: {e}")
            continue

    return {"message": f"Successfully uploaded {created_count} molecules"}
