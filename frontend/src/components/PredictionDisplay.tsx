import { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { PredictionResult, TrackData } from '../types';

interface PredictionDisplayProps {
  prediction: PredictionResult;
}

const PredictionDisplay = ({ prediction }: PredictionDisplayProps) => {
  const svgRef = useRef<SVGSVGElement>(null);

  // Get effect summary class
  const getEffectClass = () => {
    if (!prediction.effect_summary) return '';
    return prediction.effect_summary.regulatory_impact;
  };

  // Get effect description
  const getEffectDescription = () => {
    const impact = prediction.effect_summary?.regulatory_impact;
    switch (impact) {
      case 'strong':
        return 'This variant shows a strong predicted effect on gene regulation with significant changes in expression patterns.';
      case 'moderate':
        return 'This variant shows a moderate predicted effect on gene regulation with noticeable but limited changes.';
      case 'weak':
        return 'This variant shows a weak predicted effect with minimal changes to gene regulation.';
      default:
        return 'Unable to determine the regulatory impact from available data.';
    }
  };

  // Render tracks using D3
  useEffect(() => {
    if (!svgRef.current || !prediction) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const margin = { top: 20, right: 30, bottom: 40, left: 60 };
    const width = 800 - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;

    const g = svg
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Get RNA-seq data
    const refTrack = prediction.reference_tracks.rna_seq;
    const altTrack = prediction.alternate_tracks.rna_seq;

    if (!refTrack || !altTrack) return;

    const refData = refTrack.data;
    const altData = altTrack.data;

    if (refData.length === 0 || altData.length === 0) return;

    // Create scales
    const xScale = d3.scaleLinear()
      .domain([0, refData.length - 1])
      .range([0, width]);

    const yMax = Math.max(
      d3.max(refData) || 0,
      d3.max(altData) || 0
    );

    const yScale = d3.scaleLinear()
      .domain([0, yMax * 1.1])
      .range([height, 0]);

    // Add axes
    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale).ticks(5));

    g.append('g')
      .call(d3.axisLeft(yScale).ticks(5));

    // Add axis labels
    g.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', 0 - margin.left)
      .attr('x', 0 - (height / 2))
      .attr('dy', '1em')
      .style('text-anchor', 'middle')
      .style('font-size', '12px')
      .text('Expression Level');

    g.append('text')
      .attr('transform', `translate(${width / 2}, ${height + margin.bottom - 5})`)
      .style('text-anchor', 'middle')
      .style('font-size', '12px')
      .text('Genomic Position (bins)');

    // Create line generator
    const line = d3.line<number>()
      .x((d, i) => xScale(i))
      .y(d => yScale(d))
      .curve(d3.curveMonotoneX);

    // Add reference line
    g.append('path')
      .datum(refData)
      .attr('fill', 'none')
      .attr('stroke', '#4CAF50')
      .attr('stroke-width', 2)
      .attr('d', line);

    // Add alternate line
    g.append('path')
      .datum(altData)
      .attr('fill', 'none')
      .attr('stroke', '#F44336')
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', '5,5')
      .attr('d', line);

    // Mark variant position
    const variantIndex = Math.floor(refData.length / 2);
    g.append('line')
      .attr('x1', xScale(variantIndex))
      .attr('x2', xScale(variantIndex))
      .attr('y1', 0)
      .attr('y2', height)
      .attr('stroke', '#333')
      .attr('stroke-width', 1)
      .attr('stroke-dasharray', '3,3');

    // Add legend
    const legend = g.append('g')
      .attr('transform', `translate(${width - 150}, 10)`);

    legend.append('line')
      .attr('x1', 0)
      .attr('x2', 20)
      .attr('y1', 0)
      .attr('y2', 0)
      .attr('stroke', '#4CAF50')
      .attr('stroke-width', 2);

    legend.append('text')
      .attr('x', 25)
      .attr('y', 4)
      .style('font-size', '12px')
      .text('Reference');

    legend.append('line')
      .attr('x1', 0)
      .attr('x2', 20)
      .attr('y1', 20)
      .attr('y2', 20)
      .attr('stroke', '#F44336')
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', '5,5');

    legend.append('text')
      .attr('x', 25)
      .attr('y', 24)
      .style('font-size', '12px')
      .text('Variant');

  }, [prediction]);

  return (
    <div className="prediction-container">
      <div className={`effect-summary ${getEffectClass()}`}>
        <h4>Predicted Effect Summary</h4>
        <p>{getEffectDescription()}</p>
        {prediction.effect_summary?.max_expression_change !== null && (
          <p>
            Maximum expression change: {prediction.effect_summary.max_expression_change.toFixed(3)}
          </p>
        )}
      </div>

      {prediction.reference_tracks.rna_seq && prediction.alternate_tracks.rna_seq && (
        <div className="track-container">
          <div className="track-header">
            <span className="track-title">Gene Expression (RNA-seq)</span>
            <div className="track-legend">
              <div className="legend-item">
                <div className="legend-color" style={{ backgroundColor: '#4CAF50' }}></div>
                <span>Reference</span>
              </div>
              <div className="legend-item">
                <div className="legend-color" style={{ backgroundColor: '#F44336' }}></div>
                <span>Variant</span>
              </div>
            </div>
          </div>
          <svg ref={svgRef}></svg>
        </div>
      )}

      {prediction.reference_tracks.atac_seq && prediction.alternate_tracks.atac_seq && (
        <div className="track-container">
          <div className="track-header">
            <span className="track-title">Chromatin Accessibility (ATAC-seq)</span>
            <div className="track-legend">
              <div className="legend-item">
                <div className="legend-color" style={{ backgroundColor: '#2196F3' }}></div>
                <span>Reference</span>
              </div>
              <div className="legend-item">
                <div className="legend-color" style={{ backgroundColor: '#FF9800' }}></div>
                <span>Variant</span>
              </div>
            </div>
          </div>
          <p style={{ color: '#666', fontSize: '0.9rem', fontStyle: 'italic' }}>
            Chromatin accessibility predictions show how the variant affects DNA accessibility 
            to transcription factors and regulatory proteins.
          </p>
        </div>
      )}

      <div style={{ marginTop: '2rem', padding: '1rem', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
        <h4>Tissues Analyzed</h4>
        <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
          {prediction.tissues.map((tissue, index) => (
            <li key={index}>{tissue}</li>
          ))}
        </ul>
        <p style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#666' }}>
          Different tissues may show different regulatory effects due to tissue-specific 
          gene expression patterns and chromatin states.
        </p>
      </div>
    </div>
  );
};

export default PredictionDisplay;
