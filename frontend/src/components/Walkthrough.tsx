import { useState } from 'react';

interface WalkthroughProps {
  onClose: () => void;
}

const Walkthrough = ({ onClose }: WalkthroughProps) => {
  const [step, setStep] = useState(0);

  const steps = [
    {
      title: "Welcome to AlphaGenome Sandbox",
      content: "This educational tool helps you explore how DNA variants affect gene regulation using Google DeepMind's AlphaGenome model.",
      tip: "This tool is for educational use only - not for medical diagnosis."
    },
    {
      title: "Getting Started",
      content: "Start by selecting one of the educational examples. Each example features a well-known disease-associated variant with detailed explanations.",
      tip: "Examples include: Sickle Cell, Cystic Fibrosis, Breast Cancer variants, and more."
    },
    {
      title: "Understanding Sequence Lengths",
      content: "AlphaGenome requires specific sequence lengths to analyze. The supported sizes are:",
      list: ["16,384 bp (16 kb) - Smallest", "131,072 bp (131 kb) - Medium", "524,288 bp (524 kb) - Large", "1,048,576 bp (1 Mb) - Maximum"],
      tip: "All examples are pre-configured with valid sequence lengths. If creating custom analyses, ensure your region matches one of these sizes."
    },
    {
      title: "Making Predictions",
      content: "Once you select an example, you can view the variant details and choose which tissues to analyze. Then click 'Predict Variant Effects' to see AlphaGenome's predictions.",
      tip: "Different tissues may show different effects due to tissue-specific gene expression patterns."
    },
    {
      title: "Interpreting Results",
      content: "Results show predicted effects on gene expression (RNA-seq) and chromatin accessibility (ATAC-seq). Compare the reference genome (green) vs. the variant (red).",
      tip: "Strong effects mean the variant significantly changes gene regulation. These are more likely to be functionally important."
    }
  ];

  const currentStep = steps[step];

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.7)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        padding: '2rem',
        maxWidth: '600px',
        width: '90%',
        boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
      }}>
        <div style={{ marginBottom: '1.5rem' }}>
          <span style={{ 
            color: '#667eea', 
            fontSize: '0.9rem',
            fontWeight: 600 
          }}>
            Step {step + 1} of {steps.length}
          </span>
          <h2 style={{ marginTop: '0.5rem', marginBottom: '1rem' }}>
            {currentStep.title}
          </h2>
          <p style={{ fontSize: '1rem', lineHeight: 1.6, color: '#333' }}>
            {currentStep.content}
          </p>
          {currentStep.list && (
            <ul style={{ 
              marginTop: '1rem', 
              paddingLeft: '1.5rem',
              fontSize: '0.95rem',
              color: '#555'
            }}>
              {currentStep.list.map((item, idx) => (
                <li key={idx} style={{ marginBottom: '0.5rem' }}>{item}</li>
              ))}
            </ul>
          )}
          {currentStep.tip && (
            <div style={{
              marginTop: '1.5rem',
              padding: '1rem',
              backgroundColor: '#e3f2fd',
              borderRadius: '4px',
              borderLeft: '4px solid #2196f3',
              fontSize: '0.9rem',
              color: '#1565c0'
            }}>
              <strong>Tip:</strong> {currentStep.tip}
            </div>
          )}
        </div>

        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <div>
            {step > 0 && (
              <button
                onClick={() => setStep(step - 1)}
                style={{
                  padding: '0.6rem 1.2rem',
                  backgroundColor: '#f5f5f5',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  marginRight: '0.5rem',
                }}
              >
                Previous
              </button>
            )}
          </div>
          <div>
            <button
              onClick={onClose}
              style={{
                padding: '0.6rem 1.2rem',
                backgroundColor: 'transparent',
                border: 'none',
                cursor: 'pointer',
                color: '#666',
                marginRight: '0.5rem',
              }}
            >
              Skip
            </button>
            {step < steps.length - 1 ? (
              <button
                onClick={() => setStep(step + 1)}
                style={{
                  padding: '0.6rem 1.2rem',
                  backgroundColor: '#667eea',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                }}
              >
                Next
              </button>
            ) : (
              <button
                onClick={onClose}
                style={{
                  padding: '0.6rem 1.2rem',
                  backgroundColor: '#4caf50',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                }}
              >
                Get Started
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Walkthrough;
