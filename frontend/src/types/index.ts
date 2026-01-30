export interface GenomicInterval {
  chromosome: string;
  start: number;
  end: number;
}

export interface Variant {
  chromosome: string;
  position: number;
  reference_bases: string;
  alternate_bases: string;
}

export interface TrackData {
  name: string;
  data: number[];
  interval: GenomicInterval;
  color?: string;
}

export interface EffectSummary {
  max_expression_change: number | null;
  affected_tissues: string[];
  regulatory_impact: 'strong' | 'moderate' | 'weak' | 'unknown';
}

export interface PredictionResult {
  variant: Variant;
  reference_tracks: Record<string, TrackData>;
  alternate_tracks: Record<string, TrackData>;
  tissues: string[];
  effect_summary: EffectSummary;
  cached?: boolean;
}

export interface ExampleVariant {
  id: string;
  name: string;
  description: string;
  gene: string;
  disease: string | null;
  interval: GenomicInterval;
  variant: Variant;
  tissues: string[];
  educational_notes: string;
}

export interface Tissue {
  code: string;
  name: string;
}

export interface GeneInfo {
  name: string;
  chromosome: string;
  start: number;
  end: number;
}
