import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.src.utils.rdkit_utils import validate_smiles, find_substructure_matches
from app.db.models.molecule import MoleculeBase


def test_validate_smiles_valid():
    """Test valid SMILES strings"""
    valid_smiles = [
        "CCO",
        "CC(=O)O",
        "C1CCCCC1",
        "CC1=CC=CC=C1",
    ]
    for smiles in valid_smiles:
        assert validate_smiles(smiles) is True


def test_validate_smiles_invalid():
    """Test invalid SMILES strings"""
    invalid_smiles = [
        "invalid",
        "CC(X)CC",
        "C1CC2",
    ]
    for smiles in invalid_smiles:
        assert validate_smiles(smiles) is False


def test_find_substructure_matches():
    """Test substructure matching"""
    molecules = [
        MoleculeBase(id=1, name="Acetic acid", smiles="CC(=O)O"),
        MoleculeBase(id=2, name="Ethanol", smiles="CCO"),
        MoleculeBase(id=3, name="Formic acid", smiles="C(=O)O"),
    ]
    matches = find_substructure_matches(molecules, "C(=O)O")
    assert len(matches) == 2
    match_names = [m.name for m in matches]
    assert "Acetic acid" in match_names
    assert "Formic acid" in match_names
    assert "Ethanol" not in match_names
