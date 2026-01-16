from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Tuple
from ...db.models.molecule import MoleculeBase
from ..utils.rdkit_utils import validate_smiles, find_substructure_matches
from ..core.exceptions import InvalidSmilesException
from ..utils.logger import app_logger
from ..utils.cache_decorator import cache_result, invalidate_function_cache


class SearchService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    @cache_result(
        ttl=600,
        key_prefix="substructure_search",
        include_args=True,
        exclude_args=["limit", "offset"],
    )
    async def _get_full_search_results(
        self,
        query_smiles: str,
        limit: int = 10000,
        offset: int = 0,
    ) -> Tuple[List[MoleculeBase], int]:
        result = await self.db.execute(select(MoleculeBase))
        all_molecules = result.scalars().all()

        matching_molecules = find_substructure_matches(all_molecules, query_smiles)

        total_count = len(matching_molecules)
        app_logger.info(
            f"Found {total_count} molecules matching substructure: {query_smiles}"
        )
        return matching_molecules, total_count

    async def substructure_search(
        self, query_smiles: str, limit: int = 100, offset: int = 0
    ) -> Tuple[List[MoleculeBase], int]:
        if not validate_smiles(query_smiles):
            raise InvalidSmilesException(query_smiles)

        try:
            all_matching_molecules, total_count = await self._get_full_search_results(
                query_smiles
            )

            paginated_results = all_matching_molecules[offset : offset + limit]

            app_logger.info(
                f"Returning {len(paginated_results)} results "
                f"from cached search, total: {total_count}"
            )
            return paginated_results, total_count

        except Exception as e:
            app_logger.error(f"Search failed: {e}")
            raise

    async def invalidate_search_cache(self, query_smiles: str):
        return await invalidate_function_cache("substructure_search", query_smiles)
