import "../App.css";
import "./LegalPages.css";

function Privacy() {
  return (
    <div className="legal-page">
      <div className="legal-header">
        <a href="/" className="back-link">← Back to OpenFootage</a>
      </div>

      <div className="legal-content">
        <h1>Privacy Policy — OpenFootage (Demo Version)</h1>
        <p className="legal-date">Last Updated: 13.12.2025</p>

        <p className="legal-intro">
          OpenFootage respects your privacy. This policy explains how information is handled in this demo version.
        </p>

        <h2>1. Information Collected</h2>
        <p>No user accounts are required.</p>
        <p>Limited technical data may be collected automatically:</p>
        <ul>
          <li>IP address (server logs)</li>
          <li>browser and device type</li>
          <li>pages visited</li>
          <li>search queries</li>
          <li>interaction data</li>
        </ul>
        <p>No sensitive personal data is intentionally collected.</p>

        <h2>2. Use of Data</h2>
        <p>Data may be used to:</p>
        <ul>
          <li>operate and improve the demo</li>
          <li>monitor performance</li>
          <li>fix bugs and prevent abuse</li>
        </ul>
        <p>We do not sell personal data.</p>

        <h2>3. Third-Party Services</h2>
        <p>The demo may rely on:</p>
        <ul>
          <li>Netlify (frontend hosting)</li>
          <li>Railway (backend hosting)</li>
          <li>third-party APIs (search results only)</li>
        </ul>
        <p>These services process minimal data required for functionality.</p>

        <h2>4. Data Retention</h2>
        <p>
          Logs may be retained temporarily for operational purposes and deleted at any time.
        </p>

        <h2>5. Your Rights</h2>
        <p>You may request information or deletion by contacting:</p>
        <p className="contact-email">
          📧 <a href="mailto:openfootage.demo@gmail.com">openfootage.demo@gmail.com</a>
        </p>

        <h2>6. Changes</h2>
        <p>This policy may be updated as the Service evolves.</p>
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

export default Privacy;
