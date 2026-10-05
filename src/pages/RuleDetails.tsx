import { useNavigate, useParams } from "react-router-dom";

type RuleDetailsData = {
  id: number;
  name: string;
  regulator: string;
  category: string;
  effectiveDate: string;
  jurisdiction: string;
  risk: "High" | "Medium" | "Low";
  description: string;
  requirement: string;
  source: string;
};

const ruleDetails: Record<number, RuleDetailsData> = {
  1: {
    id: 1,
    name: "FinCEN Circular 2024-04",
    regulator: "FinCEN",
    category: "Cross-border Transactions",
    effectiveDate: "Jan 15, 2024",
    jurisdiction: "United States",
    risk: "High",
    description:
      "Requirements governing reporting and monitoring of cross-border financial transactions.",
    requirement:
      "Cross-border transactions must be reviewed against applicable reporting thresholds and customer verification requirements before processing.",
    source: "FinCEN Circular 2024-04",
  },

  2: {
    id: 2,
    name: "OCC Bulletin 2024-17",
    regulator: "OCC",
    category: "Customer Verification",
    effectiveDate: "Feb 02, 2024",
    jurisdiction: "United States",
    risk: "Medium",
    description:
      "Risk-based customer verification requirements for regulated financial institutions.",
    requirement:
      "Financial institutions should apply appropriate customer verification controls based on transaction risk and customer profile.",
    source: "OCC Bulletin 2024-17",
  },

  3: {
    id: 3,
    name: "AML Regulatory Update",
    regulator: "RBI",
    category: "AML Monitoring",
    effectiveDate: "Mar 11, 2024",
    jurisdiction: "India",
    risk: "Low",
    description:
      "Regulatory guidance covering suspicious transaction monitoring and anti-money laundering controls.",
    requirement:
      "Institutions should maintain appropriate monitoring procedures for identifying and escalating suspicious financial activity.",
    source: "AML Regulatory Update",
  },

  4: {
    id: 4,
    name: "KYC Requirements 2024",
    regulator: "RBI",
    category: "KYC Compliance",
    effectiveDate: "Apr 01, 2024",
    jurisdiction: "India",
    risk: "Medium",
    description:
      "Current customer identification and KYC compliance requirements.",
    requirement:
      "Customer identity and required KYC information must be verified and maintained according to applicable regulatory requirements.",
    source: "KYC Requirements 2024",
  },

  5: {
    id: 5,
    name: "Transaction Monitoring Framework",
    regulator: "FinCEN",
    category: "Transaction Monitoring",
    effectiveDate: "May 18, 2024",
    jurisdiction: "United States",
    risk: "High",
    description:
      "Framework for monitoring financial transactions and identifying potentially suspicious activity.",
    requirement:
      "Transactions should be monitored using appropriate risk-based controls and escalated when suspicious patterns are detected.",
    source: "Transaction Monitoring Framework",
  },

  6: {
    id: 6,
    name: "Customer Due Diligence Notice",
    regulator: "OCC",
    category: "Due Diligence",
    effectiveDate: "Jun 05, 2024",
    jurisdiction: "United States",
    risk: "Low",
    description:
      "Guidance covering customer due diligence procedures and ongoing monitoring.",
    requirement:
      "Institutions should maintain appropriate customer due diligence procedures throughout the customer relationship.",
    source: "Customer Due Diligence Notice",
  },
};

function RuleDetails() {
  const { id } = useParams();
  const navigate = useNavigate();

  const rule = ruleDetails[Number(id)];

  if (!rule) {
    return (
      <div className="rule-details-page">
        <div className="rule-not-found">
          <h2>Rule Not Found</h2>

          <p>
            The requested regulatory rule could not be found.
          </p>

          <button
            className="primary-button"
            onClick={() => navigate("/rules")}
          >
            Back to Active Rules
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="rule-details-page">
      {/* HEADER */}
      <div className="rule-details-top">
        <button
          className="back-button"
          onClick={() => navigate("/rules")}
        >
          ← Back to Active Rules
        </button>
      </div>

      {/* RULE HEADER */}
      <section className="rule-details-header">
        <div>
          <span className="eyebrow">
            REGULATORY GOVERNANCE
          </span>

          <h2>{rule.name}</h2>

          <p>{rule.description}</p>
        </div>

        <div className="rule-detail-status">
          <span className="status-dot"></span>
          Active
        </div>
      </section>

      {/* SUMMARY */}
      <section className="rule-detail-grid">
        <div className="rule-info-card">
          <span className="card-label">REGULATOR</span>
          <strong>{rule.regulator}</strong>
        </div>

        <div className="rule-info-card">
          <span className="card-label">CATEGORY</span>
          <strong>{rule.category}</strong>
        </div>

        <div className="rule-info-card">
          <span className="card-label">EFFECTIVE DATE</span>
          <strong>{rule.effectiveDate}</strong>
        </div>

        <div className="rule-info-card">
          <span className="card-label">JURISDICTION</span>
          <strong>{rule.jurisdiction}</strong>
        </div>
      </section>

      {/* MAIN CONTENT */}
      <section className="rule-detail-content">
        <div className="rule-detail-main">
          {/* GOVERNING REQUIREMENT */}
          <div className="rule-detail-card">
            <div className="card-header">
              <div>
                <span className="card-label">
                  GOVERNING REQUIREMENT
                </span>

                <h3>Compliance Requirement</h3>
              </div>

              <span
                className={`rule-risk ${rule.risk.toLowerCase()}`}
              >
                {rule.risk} Risk
              </span>
            </div>

            <p className="requirement-text">
              {rule.requirement}
            </p>
          </div>

          {/* COMPLIANCE STATUS */}
          <div className="rule-detail-card">
            <span className="card-label">
              COMPLIANCE STATUS
            </span>

            <h3>Current Governing Status</h3>

            <div className="compliance-check">
              <div className="check-icon">✓</div>

              <div>
                <strong>Currently governing</strong>

                <span>
                  This rule is currently marked as an active
                  governing requirement.
                </span>
              </div>
            </div>

            <div className="compliance-check">
              <div className="check-icon">✓</div>

              <div>
                <strong>No superseding rule detected</strong>

                <span>
                  No newer rule has been identified as
                  superseding this requirement.
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* SIDE PANEL */}
        <aside className="rule-detail-sidebar">
          <div className="rule-detail-card">
            <span className="card-label">
              RULE INFORMATION
            </span>

            <h3>Reference</h3>

            <div className="reference-row">
              <span>Rule ID</span>
              <strong>
                RG-{String(rule.id).padStart(4, "0")}
              </strong>
            </div>

            <div className="reference-row">
              <span>Status</span>

              <strong className="reference-active">
                Active
              </strong>
            </div>

            <div className="reference-row">
              <span>Risk Level</span>

              <span
                className={`rule-risk ${rule.risk.toLowerCase()}`}
              >
                {rule.risk}
              </span>
            </div>
          </div>

          <div className="rule-detail-card">
            <span className="card-label">
              SOURCE DOCUMENT
            </span>

            <h3>{rule.source}</h3>

            <p className="source-description">
              Official regulatory source associated with this
              governing rule.
            </p>

            <button className="secondary-button full-width">
              View Source Document
            </button>

            <button
              className="primary-button full-width"
              onClick={() => navigate("/compare")}
            >
              Compare Rule
            </button>
          </div>
        </aside>
      </section>
    </div>
  );
}

export default RuleDetails;