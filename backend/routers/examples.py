"""Educational examples of famous disease-associated variants."""

from fastapi import APIRouter, HTTPException
from typing import List
from models.schemas import ExampleVariant, GenomicInterval, Variant

router = APIRouter(prefix="/examples", tags=["examples"])

# Pre-loaded educational examples
# NOTE: AlphaGenome requires specific sequence lengths: 16384, 131072, 524288, or 1048576 bp
EXAMPLES = [
    ExampleVariant(
        id="sickle_cell",
        name="Sickle Cell Mutation (HBB Glu6Val)",
        description="A single base change (A→T) in the beta-globin gene causes sickle cell disease. This is one of the most well-studied disease variants.",
        gene="HBB",
        disease="Sickle Cell Disease",
        # AlphaGenome minimum: 16384 bp, centered on variant at position 5225952
        interval=GenomicInterval(chromosome="chr11", start=5217760, end=5234144),
        variant=Variant(
            chromosome="chr11",
            position=5225952,
            reference_bases="A",
            alternate_bases="T",
        ),
        tissues=["UBERON:0000014", "UBERON:0002385"],  # Blood, Muscle
        educational_notes="""
        This variant (rs334) changes the 6th amino acid of hemoglobin beta chain 
        from glutamic acid to valine. Use the visualization to see how this 
        mutation affects gene expression in blood cells vs. other tissues.
        
        Key Concepts:
        - Missense mutation: Changes one amino acid
        - Recessive inheritance: Need two copies to show disease
        - Heterozygote advantage: Carriers have malaria resistance
        """,
    ),
    ExampleVariant(
        id="cftr_df508",
        name="CFTR ΔF508 (Cystic Fibrosis)",
        description="A deletion of three base pairs removes phenylalanine at position 508 of the CFTR protein, causing the most common form of cystic fibrosis.",
        gene="CFTR",
        disease="Cystic Fibrosis",
        # AlphaGenome: 131072 bp, centered on variant at position 117559513
        interval=GenomicInterval(chromosome="chr7", start=117493977, end=117625049),
        variant=Variant(
            chromosome="chr7",
            position=117559513,
            reference_bases="ATCT",
            alternate_bases="ATT",
        ),
        tissues=["UBERON:0002048", "UBERON:0000946"],  # Lung, Cardiovascular
        educational_notes="""
        The ΔF508 mutation deletes one codon (CTT), removing phenylalanine at 
        position 508. This causes the CFTR protein to misfold and be degraded.
        
        Key Concepts:
        - In-frame deletion: Removes 3 bases (1 amino acid)
        - Protein misfolding: Affects protein stability
        - Affects multiple organs: Lungs, pancreas, sweat glands
        """,
    ),
    ExampleVariant(
        id="brca1_5382",
        name="BRCA1 5382insC (Breast Cancer)",
        description="An insertion of cytosine creates a frameshift mutation in BRCA1, leading to truncated protein and increased cancer risk.",
        gene="BRCA1",
        disease="Hereditary Breast/Ovarian Cancer",
        # AlphaGenome: 131072 bp, centered on variant at position 43045691
        interval=GenomicInterval(chromosome="chr17", start=42980155, end=43111227),
        variant=Variant(
            chromosome="chr17",
            position=43045691,
            reference_bases="A",
            alternate_bases="AC",
        ),
        tissues=["UBERON:0000310", "UBERON:0000992"],  # Breast, Ovary
        educational_notes="""
        This frameshift insertion disrupts the reading frame of BRCA1, 
        leading to a premature stop codon and non-functional protein.
        
        Key Concepts:
        - Frameshift mutation: Alters all downstream amino acids
        - Nonsense-mediated decay: mRNA is degraded
        - Tumor suppressor: Loss leads to genomic instability
        """,
    ),
    ExampleVariant(
        id="lactase_persistence",
        name="Lactase Persistence Regulatory Variant",
        description="A regulatory variant upstream of the LCT gene maintains lactase expression into adulthood, allowing milk digestion.",
        gene="LCT",
        disease=None,
        # AlphaGenome: 1048576 bp (1Mb), centered on variant at position 136608646
        interval=GenomicInterval(chromosome="chr2", start=136084358, end=137132934),
        variant=Variant(
            chromosome="chr2",
            position=136608646,
            reference_bases="G",
            alternate_bases="A",
        ),
        tissues=["UBERON:0000160", "UBERON:0001157"],  # Intestine, Colon
        educational_notes="""
        This is an enhancer variant (not in the gene itself) that affects 
        when the lactase gene is turned off. Most mammals and ancient humans 
        become lactose intolerant after weaning.
        
        Key Concepts:
        - Regulatory variant: Outside the coding region
        - Enhancer function: Controls gene expression timing
        - Evolutionary adaptation: Spread with dairy farming
        - Geographic distribution: Common in European populations
        """,
    ),
    ExampleVariant(
        id="apoe4",
        name="APOE ε4 (Alzheimer's Risk)",
        description="A common variant in APOE increases risk for Alzheimer's disease and affects lipid metabolism.",
        gene="APOE",
        disease="Alzheimer's Disease (risk factor)",
        # AlphaGenome minimum: 16384 bp, centered on variant at position 45411941
        interval=GenomicInterval(chromosome="chr19", start=45403749, end=45420133),
        variant=Variant(
            chromosome="chr19",
            position=45411941,
            reference_bases="T",
            alternate_bases="C",
        ),
        tissues=["UBERON:0000955", "UBERON:0002048"],  # Brain, Lung
        educational_notes="""
        APOE ε4 is the strongest genetic risk factor for late-onset Alzheimer's. 
        One copy increases risk ~3x; two copies increase risk ~12x.
        
        Key Concepts:
        - Risk variant: Increases probability but not deterministic
        - Pleiotropic effects: Also affects cholesterol transport
        - Population genetics: High frequency despite disease association
        - Not all carriers develop disease: Environmental factors matter
        """,
    ),
]


@router.get("", response_model=List[ExampleVariant])
async def list_examples() -> List[ExampleVariant]:
    """Get all educational example variants."""
    return EXAMPLES


@router.get("/{example_id}", response_model=ExampleVariant)
async def get_example(example_id: str) -> ExampleVariant:
    """Get a specific example variant by ID."""
    for example in EXAMPLES:
        if example.id == example_id:
            return example
    raise HTTPException(status_code=404, detail=f"Example {example_id} not found")
