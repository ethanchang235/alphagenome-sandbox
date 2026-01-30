interface DisclaimerBannerProps {
  // No props needed
}

const DisclaimerBanner = () => {
  return (
    <div className="disclaimer-banner">
      <strong>Educational Use Only</strong> — This tool is for learning about genomics and 
      AlphaGenome predictions. It is <strong>not</strong> intended for medical diagnosis, 
      treatment decisions, or clinical use. Results should not be used for health-related decisions.
    </div>
  );
};

export default DisclaimerBanner;
