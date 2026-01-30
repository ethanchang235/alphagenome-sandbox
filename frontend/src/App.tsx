import { useState, useEffect } from 'react';
import { 
  GenomicInterval, 
  Variant, 
  PredictionResult, 
  ExampleVariant,
  Tissue
} from './types';
import { 
  fetchExamples, 
  fetchTissues, 
  predictVariant 
} from './utils/api';
import VariantEditor from './components/VariantEditor';
import PredictionDisplay from './components/PredictionDisplay';
import ExamplesList from './components/ExamplesList';
import EducationalPanel from './components/EducationalPanel';
import DisclaimerBanner from './components/DisclaimerBanner';
import Walkthrough from './components/Walkthrough';

function App() {
  // State
  const [examples, setExamples] = useState<ExampleVariant[]>([]);
  const [tissues, setTissues] = useState<Tissue[]>([]);
  const [selectedExample, setSelectedExample] = useState<ExampleVariant | null>(null);
  // Default to sickle cell example values (valid AlphaGenome size: 16384 bp)
  const [currentInterval, setCurrentInterval] = useState<GenomicInterval>({
    chromosome: 'chr11',
    start: 5217760,
    end: 5234144,
  });
  const [currentVariant, setCurrentVariant] = useState<Variant>({
    chromosome: 'chr11',
    position: 5225952,
    reference_bases: 'A',
    alternate_bases: 'T',
  });
  const [selectedTissues, setSelectedTissues] = useState<string[]>(['UBERON:0001157']);
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showWalkthrough, setShowWalkthrough] = useState(true);

  // Load examples and tissues on mount
  useEffect(() => {
    const loadData = async () => {
      try {
        const [examplesData, tissuesData] = await Promise.all([
          fetchExamples(),
          fetchTissues(),
        ]);
        setExamples(examplesData);
        setTissues(tissuesData);
      } catch (err) {
        console.error('Failed to load initial data:', err);
        setError('Failed to load examples and tissues. Please try refreshing.');
      }
    };

    loadData();
  }, []);

  // Handle example selection
  const handleSelectExample = (example: ExampleVariant) => {
    setSelectedExample(example);
    setCurrentInterval(example.interval);
    setCurrentVariant(example.variant);
    setSelectedTissues(example.tissues);
    setPrediction(null);
    setError(null);
  };

  // Handle variant change
  const handleVariantChange = (variant: Variant) => {
    setCurrentVariant(variant);
    setPrediction(null);
  };

  // Handle prediction request
  const handlePredict = async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await predictVariant(
        currentInterval,
        currentVariant,
        selectedTissues
      );
      setPrediction(result);
    } catch (err: any) {
      console.error('Prediction failed:', err);
      
      // Provide helpful error messages
      let errorMsg = 'Failed to get prediction. Please check your inputs and try again.';
      
      if (err.response?.data?.detail) {
        errorMsg = err.response.data.detail;
      } else if (err.message?.includes('Sequence length')) {
        errorMsg = `Invalid sequence length. AlphaGenome requires regions of exactly 16,384, 131,072, 524,288, or 1,048,576 base pairs. Please select an example or adjust your region size.`;
      } else if (err.message?.includes('API key')) {
        errorMsg = 'AlphaGenome API key not configured. Please add your API key to the .env file.';
      }
      
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      {showWalkthrough && (
        <Walkthrough onClose={() => setShowWalkthrough(false)} />
      )}

      <header className="header">
        <h1>GeneReg Explorer</h1>
        <p>Educational Tool for Exploring AlphaGenome Predictions</p>
      </header>

      <DisclaimerBanner />

      <main className="main-content">
        <section className="examples-section">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <h2>Educational Examples</h2>
            <button 
              className="btn btn-secondary" 
              onClick={() => setShowWalkthrough(true)}
              style={{ fontSize: '0.9rem', padding: '0.4rem 0.8rem' }}
            >
              Show Tutorial
            </button>
          </div>
          <p>Select an example to explore a famous disease-associated variant:</p>
          <ExamplesList 
            examples={examples} 
            onSelectExample={handleSelectExample}
            selectedId={selectedExample?.id}
          />
        </section>

        <section className="control-panel">
          <h2>Variant Configuration</h2>
          
          {!selectedExample && (
            <div style={{
              backgroundColor: '#fff3cd',
              border: '1px solid #ffc107',
              borderRadius: '4px',
              padding: '1rem',
              marginBottom: '1rem',
              color: '#856404'
            }}>
              Please select an educational example above to load a valid genomic region. 
              The region fields are pre-configured for AlphaGenome compatibility.
            </div>
          )}
          
          <VariantEditor
            interval={currentInterval}
            variant={currentVariant}
            tissues={tissues}
            selectedTissues={selectedTissues}
            onVariantChange={handleVariantChange}
            onTissuesChange={setSelectedTissues}
          />

          <div className="button-group" style={{ marginTop: '1rem' }}>
            <button 
              className="btn btn-primary"
              onClick={handlePredict}
              disabled={loading}
            >
              {loading ? 'Analyzing...' : 'Predict Variant Effects'}
            </button>
            <button 
              className="btn btn-secondary"
              onClick={() => {
                setPrediction(null);
                setSelectedExample(null);
              }}
            >
              Clear Results
            </button>
          </div>

          {error && (
            <div className="error" style={{ marginTop: '1rem' }}>
              {error}
            </div>
          )}
        </section>

        {selectedExample && (
          <EducationalPanel 
            title={selectedExample.name}
            content={selectedExample.educational_notes}
          />
        )}

        {prediction && (
          <section className="results-section">
            <h2>Prediction Results</h2>
            {prediction.cached && (
              <div style={{ 
                background: '#e3f2fd', 
                padding: '0.5rem', 
                borderRadius: '4px',
                marginBottom: '1rem',
                fontSize: '0.9rem'
              }}>
                Result loaded from cache
              </div>
            )}
            <PredictionDisplay prediction={prediction} />
          </section>
        )}
      </main>

      <footer className="footer">
        <p>
          Built for educational purposes using Google DeepMind's AlphaGenome API.{' '}
          <a 
            href="https://deepmind.google.com/science/alphagenome" 
            target="_blank" 
            rel="noopener noreferrer"
          >
            Learn more about AlphaGenome
          </a>
        </p>
        <p style={{ marginTop: '0.5rem', fontSize: '0.85rem', opacity: 0.8 }}>
          Not for medical diagnosis. For research and educational use only.
        </p>
      </footer>
    </div>
  );
}

export default App;
