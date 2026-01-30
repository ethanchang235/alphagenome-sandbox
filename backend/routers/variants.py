"""API endpoints for variant predictions."""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from models.schemas import (
    PredictionRequest,
    VariantPrediction,
    GenomicInterval,
    Variant,
)
from utils.alphagenome_client import get_client, AlphaGenomeClient

router = APIRouter(prefix="/variants", tags=["variants"])


@router.post("/predict", response_model=VariantPrediction)
async def predict_variant(
    request: PredictionRequest, client: AlphaGenomeClient = Depends(get_client)
) -> VariantPrediction:
    """
    Predict the functional impact of a genomic variant using AlphaGenome.

    Returns predictions for gene expression, chromatin accessibility,
    splicing patterns, and transcription factor binding across specified tissues.
    """
    try:
        # Convert to dicts for cache key generation
        interval_dict = {
            "chromosome": request.interval.chromosome,
            "start": request.interval.start,
            "end": request.interval.end,
        }

        variant_dict = {
            "chromosome": request.variant.chromosome,
            "position": request.variant.position,
            "reference_bases": request.variant.reference_bases,
            "alternate_bases": request.variant.alternate_bases,
        }

        tissues = request.tissues or request.ontology_terms or ["UBERON:0001157"]

        # Get prediction from AlphaGenome
        result = await client.predict_variant(
            interval=interval_dict, variant=variant_dict, tissues=tissues
        )

        # Convert to response model
        return VariantPrediction(
            variant=request.variant,
            reference_tracks=result.get("reference_tracks", {}),
            alternate_tracks=result.get("alternate_tracks", {}),
            tissues=result.get("tissues", tissues),
            effect_summary=result.get("effect_summary"),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/validate")
async def validate_variant(chromosome: str, position: int, ref: str, alt: str) -> dict:
    """
    Validate a variant format and check if it can be analyzed.
    """
    # Basic validation
    valid_chromosomes = [f"chr{i}" for i in range(1, 23)] + ["chrX", "chrY", "chrM"]

    errors = []

    if chromosome not in valid_chromosomes:
        errors.append(f"Invalid chromosome: {chromosome}")

    if position <= 0:
        errors.append("Position must be positive")

    valid_bases = set("ATCGatcg")
    if not all(base in valid_bases for base in ref):
        errors.append(f"Invalid reference bases: {ref}")

    if not all(base in valid_bases for base in alt):
        errors.append(f"Invalid alternate bases: {alt}")

    if len(errors) > 0:
        return {"valid": False, "errors": errors}

    return {
        "valid": True,
        "variant": {
            "chromosome": chromosome,
            "position": position,
            "reference_bases": ref.upper(),
            "alternate_bases": alt.upper(),
        },
    }
