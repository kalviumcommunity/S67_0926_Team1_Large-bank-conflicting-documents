const Dashboard = () => {
  return (
    <div className="dashboard-page">
      <div className="page-heading">
        <div>
          <span className="eyebrow">EXECUTIVE RISK & COMPLIANCE</span>

          <h2>Compliance Overview</h2>

          <p>
            Monitor regulatory rules, conflicts, and compliance activity
            across your organization.
          </p>
        </div>

        <button className="primary-button">
          + Run Compliance Check
        </button>
      </div>

      <section className="stats-grid">
        <div className="stat-card">
          <span>ACTIVE GOVERNING RULES</span>
          <strong>1,248</strong>
          <small>↑ 14 this quarter</small>
        </div>

        <div className="stat-card">
          <span>RULE CONFLICTS</span>
          <strong>38</strong>
          <small>5 require review</small>
        </div>

        <div className="stat-card">
          <span>AVG. RESOLUTION TIME</span>
          <strong>1.4s</strong>
          <small>↓ 23% from last month</small>
        </div>

        <div className="stat-card warning">
          <span>PENDING REVIEW</span>
          <strong>5</strong>
          <small>Priority attention</small>
        </div>
      </section>

      <section className="dashboard-grid">
        <div className="dashboard-card large-card">
          <div className="card-header">
            <div>
              <span className="card-label">REGULATORY PIPELINE</span>
              <h3>Rule Convergence</h3>
            </div>

            <span className="badge">LIVE</span>
          </div>

          <div className="chart-placeholder">
            <div className="chart-line"></div>

            <div className="chart-labels">
              <span>Week 1</span>
              <span>Week 2</span>
              <span>Week 3</span>
              <span>Week 4</span>
              <span>Current</span>
            </div>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-header">
            <div>
              <span className="card-label">RULE VERIFIER</span>
              <h3>Transaction Check</h3>
            </div>
          </div>

          <div className="verification-box">
            <span>Transaction Amount</span>
            <strong>$450,000 USD</strong>

            <span>Jurisdiction</span>
            <strong>United States</strong>

            <button className="primary-button full-width">
              Run Rule Validation
            </button>
          </div>
        </div>
      </section>

      <section className="dashboard-card">
        <div className="card-header">
          <div>
            <span className="card-label">LIVE CONFLICT QUEUE</span>
            <h3>Rules Requiring Attention</h3>
          </div>

          <button className="text-button">
            View all
          </button>
        </div>

        <div className="conflict-list">
          <div className="conflict-row">
            <div>
              <strong>FinCEN Circular 2024-04</strong>
              <span>Cross-border transaction reporting</span>
            </div>

            <span className="risk high">HIGH</span>

            <button className="secondary-button">
              Resolve
            </button>
          </div>

          <div className="conflict-row">
            <div>
              <strong>OCC Bulletin 2024-17</strong>
              <span>Risk-based customer verification</span>
            </div>

            <span className="risk medium">MEDIUM</span>

            <button className="secondary-button">
              Review
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Dashboard;