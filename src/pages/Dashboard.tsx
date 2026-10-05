import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const ruleTrendData = [
  { week: "Week 1", rules: 980 },
  { week: "Week 2", rules: 1050 },
  { week: "Week 3", rules: 1110 },
  { week: "Week 4", rules: 1180 },
  { week: "Current", rules: 1248 },
];

const recentActivity = [
  {
    action: "Rule updated",
    document: "FinCEN Circular 2024-04",
    time: "12 minutes ago",
    status: "Updated",
  },
  {
    action: "Conflict detected",
    document: "OCC Bulletin 2024-17",
    time: "38 minutes ago",
    status: "Review",
  },
  {
    action: "Document added",
    document: "AML Regulatory Update",
    time: "1 hour ago",
    status: "New",
  },
];

const Dashboard = () => {
  return (
    <div className="dashboard-page">
      {/* PAGE HEADER */}
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

      {/* STAT CARDS */}
      <section className="stats-grid">
        <div className="stat-card">
          <span>ACTIVE GOVERNING RULES</span>
          <strong>1,248</strong>
          <small className="positive">↑ 14 this quarter</small>
        </div>

        <div className="stat-card">
          <span>RULE CONFLICTS</span>
          <strong>38</strong>
          <small className="negative">5 require review</small>
        </div>

        <div className="stat-card">
          <span>AVG. RESOLUTION TIME</span>
          <strong>1.4s</strong>
          <small className="positive">↓ 23% from last month</small>
        </div>

        <div className="stat-card warning">
          <span>PENDING REVIEW</span>
          <strong>5</strong>
          <small className="negative">Priority attention</small>
        </div>
      </section>

      {/* CHART + VERIFICATION */}
      <section className="dashboard-grid">
        <div className="dashboard-card large-card">
          <div className="card-header">
            <div>
              <span className="card-label">REGULATORY PIPELINE</span>
              <h3>Rule Convergence</h3>
            </div>

            <span className="badge">LIVE</span>
          </div>

          <div className="chart-container">
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={ruleTrendData}>
                <CartesianGrid
                  strokeDasharray="3 3"
                  vertical={false}
                />

                <XAxis
                  dataKey="week"
                  tick={{ fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                />

                <YAxis
                  tick={{ fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                />

                <Tooltip />

                <Line
                  type="monotone"
                  dataKey="rules"
                  stroke="#1745c4"
                  strokeWidth={3}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* RULE VERIFIER */}
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

            <span>Transaction Type</span>
            <strong>Cross-border Transfer</strong>

            <button className="primary-button full-width">
              Run Rule Validation
            </button>
          </div>
        </div>
      </section>

      {/* CONFLICT QUEUE */}
      <section className="dashboard-card">
        <div className="card-header">
          <div>
            <span className="card-label">LIVE CONFLICT QUEUE</span>
            <h3>Rules Requiring Attention</h3>
          </div>

          <button className="text-button">View all</button>
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

          <div className="conflict-row">
            <div>
              <strong>AML Regulatory Update</strong>
              <span>Suspicious transaction monitoring</span>
            </div>

            <span className="risk low">LOW</span>

            <button className="secondary-button">
              Review
            </button>
          </div>
        </div>
      </section>

      {/* RECENT ACTIVITY */}
      <section className="dashboard-card">
        <div className="card-header">
          <div>
            <span className="card-label">AUDIT ACTIVITY</span>
            <h3>Recent Compliance Activity</h3>
          </div>

          <button className="text-button">View audit trail</button>
        </div>

        <div className="activity-list">
          {recentActivity.map((activity, index) => (
            <div className="activity-row" key={index}>
              <div className="activity-indicator"></div>

              <div className="activity-info">
                <strong>{activity.action}</strong>
                <span>{activity.document}</span>
              </div>

              <span className="activity-time">
                {activity.time}
              </span>

              <span className="activity-status">
                {activity.status}
              </span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default Dashboard;