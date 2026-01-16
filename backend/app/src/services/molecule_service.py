from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from ...db.models.molecule import MoleculeBase
from ..schemas.molecule import MoleculeCreate, MoleculeUpdate
from ..utils.rdkit_utils import validate_smiles
from ..core.exceptions import (
    MoleculeNotFoundException,
    InvalidSmilesException,
    DuplicateMoleculeException,
)
from ..utils.logger import app_logger
from ..utils.cache_decorator import invalidate_cache


class MoleculeService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_molecule(self, molecule_data: MoleculeCreate) -> MoleculeBase:
        if not validate_smiles(molecule_data.smiles):
            raise InvalidSmilesException(molecule_data.smiles)

        molecule_dict = molecule_data.model_dump()

        db_molecule = MoleculeBase(**molecule_dict)

        try:
            self.db.add(db_molecule)
            await self.db.commit()
            await self.db.refresh(db_molecule)
            app_logger.info(f"Created molecule with ID: {db_molecule.id}")

            await self._invalidate_search_caches()

            return db_molecule
        except IntegrityError:
            await self.db.rollback()
            raise DuplicateMoleculeException(molecule_data.smiles)

    async def update_molecule(
        self, molecule_id: int, molecule_data: MoleculeUpdate
    ) -> MoleculeBase:
        result = await self.db.execute(
            select(MoleculeBase).filter(MoleculeBase.id == molecule_id)
        )
        molecule = result.scalar_one_or_none()

        if not molecule:
            raise MoleculeNotFoundException(molecule_id)

        update_data = molecule_data.model_dump(exclude_unset=True)

        if "smiles" in update_data:
            if not validate_smiles(update_data["smiles"]):
                raise InvalidSmilesException(update_data["smiles"])

        for field, value in update_data.items():
            setattr(molecule, field, value)

        try:
            await self.db.commit()
            await self.db.refresh(molecule)
            app_logger.info(f"Updated molecule with ID: {molecule_id}")

            await self._invalidate_search_caches()

            return molecule
        except IntegrityError:
            await self.db.rollback()
            raise DuplicateMoleculeException(update_data.get("smiles", molecule.smiles))

    async def delete_molecule(self, molecule_id: int) -> bool:
        result = await self.db.execute(
            select(MoleculeBase).filter(MoleculeBase.id == molecule_id)
        )
        molecule = result.scalar_one_or_none()

        if not molecule:
            raise MoleculeNotFoundException(molecule_id)

        await self.db.delete(molecule)
        await self.db.commit()
        app_logger.info(f"Deleted molecule with ID: {molecule_id}")

        await self._invalidate_search_caches()

        return True

    async def get_molecule(self, molecule_id: int) -> Optional[MoleculeBase]:
        result = await self.db.execute(
            select(MoleculeBase).filter(MoleculeBase.id == molecule_id)
        )
        molecule = result.scalar_one_or_none()

        if not molecule:
            raise MoleculeNotFoundException(molecule_id)

        app_logger.info(f"Retrieved molecule with ID: {molecule_id}")
        return molecule

    async def get_all_molecules(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[List[MoleculeBase], int]:
        count_result = await self.db.execute(select(MoleculeBase))
        total_count = len(count_result.all())

        result = await self.db.execute(select(MoleculeBase).offset(skip).limit(limit))
        molecules = result.scalars().all()

        app_logger.info(f"Retrieved {len(molecules)} molecules")
        return molecules, total_count

    async def _invalidate_search_caches(self):
        """
        Invalidate all search-related caches when data changes
        """
        try:
            await invalidate_cache("search_results:*")
            await invalidate_cache("substructure_search:*")
            app_logger.info("Search caches invalidated")
        except Exception as e:
            app_logger.error(f"Search cache invalidation failed: {e}")
            pass
