import "../App.css";
import "./LegalPages.css";

function Terms() {
  return (
    <div className="legal-page">
      <div className="legal-header">
        <a href="/" className="back-link">← Back to OpenFootage</a>
      </div>

      <div className="legal-content">
        <h1>Terms of Use — OpenFootage (Demo Version)</h1>
        <p className="legal-date">Last Updated: 13.12.2025</p>

        <p className="legal-intro">
          Welcome to OpenFootage (the "Service").<br />
          This Service is a demo prototype provided for testing and evaluation purposes only. It is not intended for commercial use.
        </p>

        <p className="legal-intro">
          By accessing or using this demo, you agree to these Terms of Use.
        </p>

        <h2>1. Nature of the Service</h2>
        <p>
          OpenFootage is a search and discovery interface that aggregates metadata and previews from third-party stock media providers. The Service does not host, store, upload, or distribute original media files.
        </p>
        <p>
          All media remains the property of its respective owners.
        </p>

        <h2>2. Third-Party Content & Licensing</h2>
        <p>
          Search results are retrieved from third-party providers via their public APIs, including but not limited to:
        </p>
        <ul>
          <li>Pexels</li>
          <li>Pixabay</li>
          <li>Unsplash</li>
          <li>Freesound</li>
        </ul>
        <p>
          Each provider maintains its own licensing terms. You are solely responsible for reviewing and complying with those terms before downloading or using any asset.
        </p>
        <p>
          <strong>OpenFootage does not grant licenses or usage rights for third-party content.</strong>
        </p>

        <h2>3. Demo-Only Limitations</h2>
        <p>This demo:</p>
        <ul>
          <li>may contain errors or incomplete data</li>
          <li>may change or be discontinued at any time</li>
          <li>is not guaranteed to be available or secure</li>
        </ul>
        <p>
          The Service is provided "as is", without warranties of any kind.
        </p>

        <h2>4. Acceptable Use</h2>
        <p>You agree not to:</p>
        <ul>
          <li>use the Service unlawfully</li>
          <li>attempt to scrape, overload, or disrupt the Service</li>
          <li>bypass technical limits or safeguards</li>
        </ul>
        <p>
          We may restrict access to protect the Service or providers.
        </p>

        <h2>5. Intellectual Property</h2>
        <p>
          All OpenFootage branding, interface design, and original code belong to OpenFootage.<br />
          Third-party media remains the property of its respective owners.
        </p>

        <h2>6. Copyright & Takedown Requests</h2>
        <p>
          If you believe content displayed through this demo infringes your rights, contact:
        </p>
        <p className="contact-email">
          📧 <a href="mailto:openfootage.demo@gmail.com">openfootage.demo@gmail.com</a>
        </p>
        <p>Include:</p>
        <ul>
          <li>your contact information</li>
          <li>the relevant OpenFootage page or result</li>
          <li>proof of ownership</li>
        </ul>
        <p>
          We will review requests promptly and remove any cached metadata under our control if appropriate.
        </p>

        <h2>7. Limitation of Liability</h2>
        <p>
          To the maximum extent permitted by law, OpenFootage is not liable for:
        </p>
        <ul>
          <li>misuse of third-party content</li>
          <li>licensing errors</li>
          <li>damages arising from use of this demo</li>
        </ul>
        <p>
          Users assume full responsibility for verifying content rights.
        </p>

        <h2>8. Changes</h2>
        <p>
          We may update these Terms at any time. Continued use indicates acceptance of the updated version.
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

export default Terms;
