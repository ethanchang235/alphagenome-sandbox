"""API endpoints for genomic regions and basic info."""

from fastapi import APIRouter, HTTPException
from models.schemas import RegionInfo, GenomicInterval

router = APIRouter(prefix="/regions", tags=["regions"])

# AlphaGenome supported sequence lengths
ALPHAGENOME_SIZES = [16384, 131072, 524288, 1048576]

# Available tissues with their UBERON ontology codes
AVAILABLE_TISSUES = [
    {"code": "UBERON:0001157", "name": "Transverse Colon"},
    {"code": "UBERON:0000014", "name": "Blood"},
    {"code": "UBERON:0000955", "name": "Brain"},
    {"code": "UBERON:0002048", "name": "Lung"},
    {"code": "UBERON:0000310", "name": "Breast"},
    {"code": "UBERON:0000160", "name": "Intestine"},
    {"code": "UBERON:0002369", "name": "Adrenal Gland"},
    {"code": "UBERON:0000946", "name": "Cardiovascular"},
    {"code": "UBERON:0002385", "name": "Muscle"},
    {"code": "UBERON:0000992", "name": "Ovary"},
]

# Common gene coordinates for quick access
# NOTE: Must use AlphaGenome-supported sizes: 16384, 131072, 524288, or 1048576 bp
GENE_COORDINATES = {
    "HBB": GenomicInterval(chromosome="chr11", start=5217760, end=5234144),  # 16384 bp
    "CFTR": GenomicInterval(
        chromosome="chr7", start=117493977, end=117625049
    ),  # 131072 bp
    "BRCA1": GenomicInterval(
        chromosome="chr17", start=42980155, end=43111227
    ),  # 131072 bp
    "BRCA2": GenomicInterval(
        chromosome="chr13", start=32249806, end=32380878
    ),  # 131072 bp
    "TP53": GenomicInterval(
        chromosome="chr17", start=7610523, end=7741595
    ),  # 131072 bp
    "APOE": GenomicInterval(
        chromosome="chr19", start=45403749, end=45420133
    ),  # 16384 bp
    "LCT": GenomicInterval(
        chromosome="chr2", start=136084358, end=137132934
    ),  # 1048576 bp
    "EGFR": GenomicInterval(
        chromosome="chr7", start=54949025, end=55080097
    ),  # 131072 bp
}


def get_nearest_valid_size(size: int) -> int:
    """Get the nearest valid AlphaGenome sequence size."""
    for valid_size in ALPHAGENOME_SIZES:
        if size <= valid_size:
            return valid_size
    return ALPHAGENOME_SIZES[-1]  # Return largest if bigger than all


@router.get("/info/{gene_name}")
async def get_gene_region(gene_name: str) -> RegionInfo:
    """Get genomic coordinates for a gene."""
    gene_upper = gene_name.upper()
    if gene_upper not in GENE_COORDINATES:
        raise HTTPException(status_code=404, detail=f"Gene {gene_name} not found")

    interval = GENE_COORDINATES[gene_upper]
    return RegionInfo(
        interval=interval,
        genes_in_region=[gene_upper],
        available_tissues=[t["name"] for t in AVAILABLE_TISSUES],
    )


@router.get("/tissues")
async def list_tissues() -> list:
    """List all available tissue types for prediction."""
    return AVAILABLE_TISSUES


@router.get("/genes")
async def list_available_genes() -> list:
    """List genes with pre-defined coordinates."""
    return [
        {
            "name": name,
            "chromosome": interval.chromosome,
            "start": interval.start,
            "end": interval.end,
        }
        for name, interval in GENE_COORDINATES.items()
    ]


@router.get("/constraints")
async def get_constraints() -> dict:
    """Get AlphaGenome API constraints and requirements."""
    return {
        "supported_sequence_lengths": ALPHAGENOME_SIZES,
        "min_length": min(ALPHAGENOME_SIZES),
        "max_length": max(ALPHAGENOME_SIZES),
        "valid_chromosomes": [f"chr{i}" for i in range(1, 23)]
        + ["chrX", "chrY", "chrM"],
        "note": "Sequence length must be exactly one of the supported values",
    }


@router.post("/validate")
async def validate_region(interval: GenomicInterval) -> dict:
    """Validate a genomic region for AlphaGenome compatibility."""
    valid_chromosomes = [f"chr{i}" for i in range(1, 23)] + ["chrX", "chrY", "chrM"]

    errors = []
    warnings = []

    if interval.chromosome not in valid_chromosomes:
        errors.append(f"Invalid chromosome: {interval.chromosome}")

    if interval.start >= interval.end:
        errors.append("Start position must be less than end position")

    if interval.start <= 0:
        errors.append("Start position must be positive")

    region_size = interval.end - interval.start

    # AlphaGenome max window is ~1Mbp
    if region_size > 1_000_000:
        errors.append(f"Region too large ({region_size} bp). Maximum is 1,000,000 bp.")

    # Check if size is valid for AlphaGenome
    if region_size not in ALPHAGENOME_SIZES:
        nearest = get_nearest_valid_size(region_size)
        errors.append(
            f"Invalid sequence length: {region_size} bp. "
            f"AlphaGenome requires exactly one of these sizes: {ALPHAGENOME_SIZES}. "
            f"Nearest valid size: {nearest} bp."
        )

    if len(errors) > 0:
        return {"valid": False, "errors": errors, "warnings": warnings}

    return {
        "valid": True,
        "interval": interval,
        "size": region_size,
        "message": f"Valid region of {region_size:,} base pairs (AlphaGenome compatible)",
    }
