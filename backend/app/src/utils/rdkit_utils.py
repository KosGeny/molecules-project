from rdkit.Chem import MolFromSmiles
from .logger import app_logger
from typing import List
from ...db.models.molecule import MoleculeBase


def validate_smiles(smiles: str) -> bool:
    try:
        mol = MolFromSmiles(smiles)
        if mol is None:
            return False
        return True
    except Exception as e:
        app_logger.error(f"Error validating SMILES {smiles}: {e}")
        return False


def find_substructure_matches(
    molecules: List[MoleculeBase], substructure_smiles: str
) -> List[MoleculeBase]:
    sub_molecule = MolFromSmiles(substructure_smiles)
    if sub_molecule is None:
        raise ValueError(f"Incorrect SMILES of substructure: {substructure_smiles}")

    matching_molecules = []
    for molecule in molecules:
        target_molecule = MolFromSmiles(molecule.smiles)
        if target_molecule is None:
            continue
        if target_molecule.HasSubstructMatch(sub_molecule):
            matching_molecules.append(molecule)
    return matching_molecules
