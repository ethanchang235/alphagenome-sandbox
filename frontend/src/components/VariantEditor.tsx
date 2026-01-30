import { GenomicInterval, Variant, Tissue } from '../types';

interface VariantEditorProps {
  interval: GenomicInterval;
  variant: Variant;
  tissues: Tissue[];
  selectedTissues: string[];
  onVariantChange: (variant: Variant) => void;
  onTissuesChange: (tissues: string[]) => void;
}

const VariantEditor = ({
  interval,
  variant,
  tissues,
  selectedTissues,
  onVariantChange,
  onTissuesChange,
}: VariantEditorProps) => {
  const handlePositionChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const position = parseInt(e.target.value) || 0;
    onVariantChange({ ...variant, position });
  };

  const handleRefChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onVariantChange({ ...variant, reference_bases: e.target.value.toUpperCase() });
  };

  const handleAltChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onVariantChange({ ...variant, alternate_bases: e.target.value.toUpperCase() });
  };

  const handleTissueToggle = (tissueCode: string) => {
    if (selectedTissues.includes(tissueCode)) {
      onTissuesChange(selectedTissues.filter(t => t !== tissueCode));
    } else {
      onTissuesChange([...selectedTissues, tissueCode]);
    }
  };

  return (
    <div>
      <div className="input-group">
        <label>
          Chromosome
          <input 
            type="text" 
            value={interval.chromosome} 
            disabled 
            style={{ width: '80px' }}
          />
        </label>
        <label>
          Region Start
          <input 
            type="number" 
            value={interval.start} 
            disabled 
            style={{ width: '120px' }}
          />
        </label>
        <label>
          Region End
          <input 
            type="number" 
            value={interval.end} 
            disabled 
            style={{ width: '120px' }}
          />
        </label>
      </div>

      <div className="input-group">
        <label>
          Variant Position
          <input 
            type="number" 
            value={variant.position} 
            onChange={handlePositionChange}
            style={{ width: '140px' }}
          />
        </label>
        <label>
          Reference (Ref)
          <input 
            type="text" 
            value={variant.reference_bases} 
            onChange={handleRefChange}
            style={{ width: '100px', textTransform: 'uppercase' }}
            maxLength={10}
          />
        </label>
        <span style={{ alignSelf: 'center', fontSize: '1.5rem' }}>→</span>
        <label>
          Alternate (Alt)
          <input 
            type="text" 
            value={variant.alternate_bases} 
            onChange={handleAltChange}
            style={{ width: '100px', textTransform: 'uppercase' }}
            maxLength={10}
          />
        </label>
      </div>

      <div style={{ marginTop: '1rem' }}>
        <label style={{ display: 'block', marginBottom: '0.5rem' }}>
          Select Tissues for Analysis:
        </label>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {tissues.map((tissue) => (
            <label
              key={tissue.code}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.25rem',
                padding: '0.4rem 0.8rem',
                backgroundColor: selectedTissues.includes(tissue.code) 
                  ? '#e3f2fd' 
                  : '#f5f5f5',
                border: `1px solid ${selectedTissues.includes(tissue.code) 
                  ? '#2196f3' 
                  : '#ddd'}`,
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '0.9rem',
              }}
            >
              <input
                type="checkbox"
                checked={selectedTissues.includes(tissue.code)}
                onChange={() => handleTissueToggle(tissue.code)}
                style={{ margin: 0 }}
              />
              {tissue.name}
            </label>
          ))}
        </div>
      </div>

      <div style={{ 
        marginTop: '1rem', 
        padding: '0.75rem', 
        backgroundColor: '#f5f5f5', 
        borderRadius: '4px',
        fontFamily: 'monospace',
        fontSize: '0.9rem'
      }}>
        <strong>Current Variant:</strong><br />
        {variant.chromosome}:{variant.position} {variant.reference_bases}&gt;{variant.alternate_bases}
      </div>
    </div>
  );
};

export default VariantEditor;
