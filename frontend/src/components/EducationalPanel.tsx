interface EducationalPanelProps {
  title: string;
  content: string;
}

const EducationalPanel = ({ title, content }: EducationalPanelProps) => {
  // Parse the content to handle markdown-like formatting
  const formattedContent = content
    .split('\n')
    .map((line, index) => {
      const trimmed = line.trim();
      if (trimmed.startsWith('- ')) {
        return <li key={index}>{trimmed.substring(2)}</li>;
      }
      if (trimmed.startsWith('Key Concepts:')) {
        return <h4 key={index} style={{ color: '#1976d2', marginTop: '1rem' }}>{trimmed}</h4>;
      }
      if (trimmed === '') {
        return <br key={index} />;
      }
      return <p key={index}>{trimmed}</p>;
    });

  return (
    <div className="educational-panel">
      <h3>About {title}</h3>
      <div>{formattedContent}</div>
    </div>
  );
};

export default EducationalPanel;
