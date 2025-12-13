import "../App.css";
import "./LegalPages.css";

function Attribution() {
  return (
    <div className="legal-page">
      <div className="legal-header">
        <a href="/" className="back-link">← Back to OpenFootage</a>
      </div>

      <div className="legal-content">
        <h1>Source Providers & Attribution</h1>

        <p className="legal-intro">
          OpenFootage displays results from third-party providers. All media remains subject to each provider's license terms.
        </p>

        <h2>Current Providers</h2>
        <ul className="provider-list">
          <li><strong>Unsplash</strong> — <a href="https://unsplash.com" target="_blank" rel="noopener noreferrer">unsplash.com</a></li>
          <li><strong>Pexels</strong> — <a href="https://pexels.com" target="_blank" rel="noopener noreferrer">pexels.com</a></li>
          <li><strong>Pixabay</strong> — <a href="https://pixabay.com" target="_blank" rel="noopener noreferrer">pixabay.com</a></li>
          <li><strong>Freesound</strong> — <a href="https://freesound.org" target="_blank" rel="noopener noreferrer">freesound.org</a></li>
        </ul>

        <p className="legal-warning">
          <strong>Users must always verify licenses on the provider's website before use.</strong>
        </p>
      </div>

      <footer className="legal-footer">
        <p>© 2025 OpenFootage — Demo Version</p>
        <p>OpenFootage does not host or license media files.<br />
        All assets belong to their respective owners.</p>
        <p>Copyright inquiries: <a href="mailto:openfootage.demo@gmail.com">openfootage.demo@gmail.com</a></p>
      </footer>
    </div>
  );
}

export default Attribution;
