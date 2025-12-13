import "../App.css";
import "./LegalPages.css";

function DMCA() {
  return (
    <div className="legal-page">
      <div className="legal-header">
        <a href="/" className="back-link">← Back to OpenFootage</a>
      </div>

      <div className="legal-content">
        <h1>Copyright & Takedown Policy — OpenFootage (Demo Version)</h1>
        <p className="legal-date">Last Updated: 13.12.2025</p>

        <p className="legal-intro">
          OpenFootage does not host original media files. Content is retrieved from third-party providers.
        </p>

        <p>
          If you believe content displayed through this demo infringes your copyright, contact:
        </p>

        <p className="contact-email">
          📧 <a href="mailto:openfootage.demo@gmail.com">openfootage.demo@gmail.com</a>
        </p>

        <p>Include:</p>
        <ul>
          <li>your name and contact details</li>
          <li>the relevant OpenFootage result or page</li>
          <li>proof of ownership</li>
        </ul>

        <p>
          We will review valid requests and remove any cached metadata under our control when appropriate.
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

export default DMCA;
