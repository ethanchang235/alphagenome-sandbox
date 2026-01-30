"""Pydantic models for GeneReg Explorer API."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class GenomicInterval(BaseModel):
    """Represents a genomic interval."""

    chromosome: str
    start: int
    end: int

    class Config:
        json_schema_extra = {
            "example": {"chromosome": "chr11", "start": 5217760, "end": 5234144}
        }


class Variant(BaseModel):
    """Represents a genomic variant."""

    chromosome: str
    position: int
    reference_bases: str
    alternate_bases: str

    class Config:
        json_schema_extra = {
            "example": {
                "chromosome": "chr11",
                "position": 5225952,
                "reference_bases": "G",
                "alternate_bases": "A",
            }
        }


class PredictionRequest(BaseModel):
    """Request model for variant prediction."""

    interval: GenomicInterval
    variant: Variant
    ontology_terms: Optional[List[str]] = None
    tissues: Optional[List[str]] = None


class TrackData(BaseModel):
    """Represents a single track of prediction data."""

    name: str
    data: List[float]
    interval: GenomicInterval
    color: Optional[str] = None


class VariantPrediction(BaseModel):
    """Complete prediction results for a variant."""

    variant: Variant
    reference_tracks: Dict[str, TrackData]
    alternate_tracks: Dict[str, TrackData]
    tissues: List[str]
    effect_summary: Optional[Dict[str, Any]] = None


class ExampleVariant(BaseModel):
    """Pre-loaded example variant for educational purposes."""

    id: str
    name: str
    description: str
    gene: str
    disease: Optional[str]
    interval: GenomicInterval
    variant: Variant
    tissues: List[str]
    educational_notes: str


class RegionInfo(BaseModel):
    """Information about a genomic region."""

    interval: GenomicInterval
    sequence: Optional[str] = None
    genes_in_region: List[str]
    available_tissues: List[str]
