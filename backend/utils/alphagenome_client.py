"""AlphaGenome client wrapper with caching and rate limiting."""

import os
import asyncio
import time
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from utils.cache import PredictionCache


class AlphaGenomeClient:
    """Wrapper around AlphaGenome API with caching and rate limiting."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ALPHAGENOME_API_KEY")
        if not self.api_key:
            raise ValueError(
                "AlphaGenome API key required. Set ALPHAGENOME_API_KEY env var."
            )

        self.cache = PredictionCache()
        self.last_request_time = 0
        self.min_request_interval = (
            0.5  # Minimum seconds between requests (2 req/sec max)
        )
        self.daily_request_count = 0
        self.daily_limit = 1000  # Conservative daily limit

        # Initialize AlphaGenome client
        try:
            from alphagenome.models import dna_client
            from alphagenome.data import genome

            self.client = dna_client.create(self.api_key)
            self.genome = genome
            self.dna_client = dna_client
            print("AlphaGenome client initialized successfully")
        except Exception as e:
            print(f"Warning: Could not initialize AlphaGenome client: {e}")
            self.client = None
            self.genome = None
            self.dna_client = None

    async def _rate_limited_request(self):
        """Ensure we don't exceed rate limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last
            await asyncio.sleep(wait_time)

        self.last_request_time = time.time()

    def _check_daily_limit(self):
        """Check if we're approaching daily request limits."""
        if self.daily_request_count >= self.daily_limit:
            raise Exception(
                "Daily API request limit reached. Please try again tomorrow."
            )

    def _extract_values(self, data_obj) -> List[float]:
        """Extract values from AlphaGenome output, handling multi-tissue data."""
        if not hasattr(data_obj, "values"):
            return []

        values = data_obj.values

        # Handle different data types
        if hasattr(values, "tolist"):
            values = values.tolist()

        # If values is a list of lists (multi-tissue), flatten by taking mean or first
        if values and isinstance(values, list) and len(values) > 0:
            # Check if first element is also a list (multi-dimensional)
            if isinstance(values[0], list):
                # Multi-tissue data: take the first tissue's data for simplicity
                # Or could calculate mean across tissues
                return [float(x) for x in values[0]]
            else:
                # Single tissue data: convert to float
                return [float(x) for x in values]

        return []

    async def predict_variant(
        self,
        interval: Dict[str, Any],
        variant: Dict[str, Any],
        tissues: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Predict variant effects with caching."""

        # Check cache first
        cached = self.cache.get(variant, interval, tissues or [])
        if cached:
            print("Cache hit for variant prediction")
            return {**cached, "cached": True}

        # Check rate limits
        await self._rate_limited_request()
        self._check_daily_limit()

        if not self.client:
            raise Exception("AlphaGenome client not initialized")

        try:
            # Create interval object using the genome module
            interval_obj = self.genome.Interval(
                chromosome=interval["chromosome"],
                start=interval["start"],
                end=interval["end"],
            )

            # Create variant object
            variant_obj = self.genome.Variant(
                chromosome=variant["chromosome"],
                position=variant["position"],
                reference_bases=variant["reference_bases"],
                alternate_bases=variant["alternate_bases"],
            )

            # Default tissues if not provided
            if not tissues:
                tissues = ["UBERON:0001157"]  # Transverse colon

            # Request predictions with proper output type from dna_client
            try:
                requested_outputs = [self.dna_client.OutputType.RNA_SEQ]
            except:
                requested_outputs = None

            outputs = self.client.predict_variant(
                interval=interval_obj,
                variant=variant_obj,
                ontology_terms=tissues,
                requested_outputs=requested_outputs,
            )

            self.daily_request_count += 1

            # Format response
            response = self._format_prediction_response(
                outputs, interval_obj, variant_obj, tissues
            )

            # Cache the result
            self.cache.set(variant, interval, tissues, response)

            return {**response, "cached": False}

        except Exception as e:
            print(f"AlphaGenome API error: {e}")
            raise Exception(f"Prediction failed: {str(e)}")

    def _format_prediction_response(
        self, outputs, interval, variant, tissues
    ) -> Dict[str, Any]:
        """Format AlphaGenome output into our API response schema."""

        response = {
            "variant": {
                "chromosome": variant.chromosome,
                "position": variant.position,
                "reference_bases": variant.reference_bases,
                "alternate_bases": variant.alternate_bases,
            },
            "interval": {
                "chromosome": interval.chromosome,
                "start": interval.start,
                "end": interval.end,
            },
            "tissues": tissues,
            "reference_tracks": {},
            "alternate_tracks": {},
            "effect_summary": {
                "max_expression_change": None,
                "affected_tissues": [],
                "regulatory_impact": "unknown",
            },
        }

        # Extract track data from outputs
        try:
            if hasattr(outputs, "reference"):
                ref = outputs.reference
                if hasattr(ref, "rna_seq"):
                    response["reference_tracks"]["rna_seq"] = {
                        "name": "Gene Expression (RNA-seq)",
                        "data": self._extract_values(ref.rna_seq),
                        "interval": {
                            "chromosome": ref.rna_seq.interval.chromosome
                            if hasattr(ref.rna_seq, "interval")
                            else interval.chromosome,
                            "start": ref.rna_seq.interval.start
                            if hasattr(ref.rna_seq, "interval")
                            else interval.start,
                            "end": ref.rna_seq.interval.end
                            if hasattr(ref.rna_seq, "interval")
                            else interval.end,
                        },
                        "color": "#4CAF50",
                    }

                if hasattr(ref, "atac_seq"):
                    response["reference_tracks"]["atac_seq"] = {
                        "name": "Chromatin Accessibility (ATAC-seq)",
                        "data": self._extract_values(ref.atac_seq),
                        "interval": {
                            "chromosome": ref.atac_seq.interval.chromosome
                            if hasattr(ref.atac_seq, "interval")
                            else interval.chromosome,
                            "start": ref.atac_seq.interval.start
                            if hasattr(ref.atac_seq, "interval")
                            else interval.start,
                            "end": ref.atac_seq.interval.end
                            if hasattr(ref.atac_seq, "interval")
                            else interval.end,
                        },
                        "color": "#2196F3",
                    }

            if hasattr(outputs, "alternate"):
                alt = outputs.alternate
                if hasattr(alt, "rna_seq"):
                    response["alternate_tracks"]["rna_seq"] = {
                        "name": "Gene Expression (RNA-seq) - Variant",
                        "data": self._extract_values(alt.rna_seq),
                        "interval": {
                            "chromosome": alt.rna_seq.interval.chromosome
                            if hasattr(alt.rna_seq, "interval")
                            else interval.chromosome,
                            "start": alt.rna_seq.interval.start
                            if hasattr(alt.rna_seq, "interval")
                            else interval.start,
                            "end": alt.rna_seq.interval.end
                            if hasattr(alt.rna_seq, "interval")
                            else interval.end,
                        },
                        "color": "#F44336",
                    }

                if hasattr(alt, "atac_seq"):
                    response["alternate_tracks"]["atac_seq"] = {
                        "name": "Chromatin Accessibility (ATAC-seq) - Variant",
                        "data": self._extract_values(alt.atac_seq),
                        "interval": {
                            "chromosome": alt.atac_seq.interval.chromosome
                            if hasattr(alt.atac_seq, "interval")
                            else interval.chromosome,
                            "start": alt.atac_seq.interval.start
                            if hasattr(alt.atac_seq, "interval")
                            else interval.start,
                            "end": alt.atac_seq.interval.end
                            if hasattr(alt.atac_seq, "interval")
                            else interval.end,
                        },
                        "color": "#FF9800",
                    }

            # Calculate effect summary
            if (
                "rna_seq" in response["reference_tracks"]
                and "rna_seq" in response["alternate_tracks"]
            ):
                ref_data = response["reference_tracks"]["rna_seq"]["data"]
                alt_data = response["alternate_tracks"]["rna_seq"]["data"]

                if ref_data and alt_data and len(ref_data) == len(alt_data):
                    changes = [abs(a - r) for r, a in zip(ref_data, alt_data)]
                    max_change = max(changes) if changes else 0
                    response["effect_summary"]["max_expression_change"] = max_change

                    if max_change > 0.5:
                        response["effect_summary"]["regulatory_impact"] = "strong"
                    elif max_change > 0.1:
                        response["effect_summary"]["regulatory_impact"] = "moderate"
                    else:
                        response["effect_summary"]["regulatory_impact"] = "weak"

        except Exception as e:
            print(f"Error formatting response: {e}")
            # Return basic response if formatting fails
            pass

        return response

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache.get_stats()

    def clear_cache(self) -> int:
        """Clear expired cache entries."""
        return self.cache.clear_expired()


# Global client instance
_alphagenome_client: Optional[AlphaGenomeClient] = None


def get_client() -> AlphaGenomeClient:
    """Get or create AlphaGenome client singleton."""
    global _alphagenome_client
    if _alphagenome_client is None:
        _alphagenome_client = AlphaGenomeClient()
    return _alphagenome_client
