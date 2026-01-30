import { ExampleVariant } from '../types';

interface ExamplesListProps {
  examples: ExampleVariant[];
  onSelectExample: (example: ExampleVariant) => void;
  selectedId?: string;
}

const ExamplesList = ({ examples, onSelectExample, selectedId }: ExamplesListProps) => {
  if (examples.length === 0) {
    return <div className="loading">Loading examples...</div>;
  }

  return (
    <div className="examples-grid">
      {examples.map((example) => (
        <div
          key={example.id}
          className="example-card"
          onClick={() => onSelectExample(example)}
          style={{
            borderColor: selectedId === example.id ? '#667eea' : undefined,
            backgroundColor: selectedId === example.id ? '#f0f4ff' : undefined,
          }}
        >
          <h3>{example.name}</h3>
          <p>{example.description}</p>
          {example.disease && (
            <span className="disease-tag">{example.disease}</span>
          )}
          <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: '#888' }}>
            Gene: {example.gene}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ExamplesList;
