from sqlalchemy import String, Integer, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from ..base import Base


class MoleculeBase(Base):
    __tablename__ = "molecules"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    smiles: Mapped[str] = mapped_column(Text, nullable=False)
    __table_args__ = (
        Index('idx_smiles', 'smiles'),
    )
