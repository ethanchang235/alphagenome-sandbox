import axios from 'axios';
import { 
  GenomicInterval, 
  Variant, 
  PredictionResult, 
  ExampleVariant,
  Tissue,
  GeneInfo
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchExamples = async (): Promise<ExampleVariant[]> => {
  const response = await api.get('/examples');
  return response.data;
};

export const fetchExample = async (id: string): Promise<ExampleVariant> => {
  const response = await api.get(`/examples/${id}`);
  return response.data;
};

export const fetchTissues = async (): Promise<Tissue[]> => {
  const response = await api.get('/regions/tissues');
  return response.data;
};

export const fetchGenes = async (): Promise<GeneInfo[]> => {
  const response = await api.get('/regions/genes');
  return response.data;
};

export const predictVariant = async (
  interval: GenomicInterval,
  variant: Variant,
  tissues: string[]
): Promise<PredictionResult> => {
  const response = await api.post('/variants/predict', {
    interval,
    variant,
    tissues,
  });
  return response.data;
};

export const validateVariant = async (
  chromosome: string,
  position: number,
  ref: string,
  alt: string
): Promise<{ valid: boolean; errors?: string[]; variant?: Variant }> => {
  const response = await api.get('/variants/validate', {
    params: { chromosome, position, ref, alt },
  });
  return response.data;
};
