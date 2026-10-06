import { useMemo, useState } from "react";

type Rule = {
  id: number;
  name: string;
  regulator: string;
  effectiveDate: string;
  jurisdiction: string;
  category: string;
  threshold: string;
  requirement: string;
  reporting: string;
};

const rules: Rule[] = [
  {
    id: 1,
    name: "FinCEN Circular 2024-04",
    regulator: "FinCEN",
    effectiveDate: "Jan 15, 2024",
    jurisdiction: "United States",
    category: "Cross-border Transactions",
    threshold: "$250,000",
    requirement: "Enhanced review required for qualifying cross-border transactions.",
    reporting: "CTR filing required within the regulatory reporting window.",
  },
  {
    id: 2,
    name: "OCC Bulletin 2024-17",
    regulator: "OCC",
    effectiveDate: "Feb 02, 2024",
    jurisdiction: "United States",
    category: "Customer Verification",
    threshold: "$100,000",
    requirement: "Additional customer verification is required for elevated-risk transactions.",
    reporting: "Suspicious activity must be escalated to the compliance team.",
  },
  {
    id: 3,
    name: "AML Regulatory Update",
    regulator: "RBI",
    effectiveDate: "Mar 11, 2024",
    jurisdiction: "India",
    category: "AML Monitoring",
    threshold: "₹10,00,000",
    requirement: "Enhanced monitoring applies to transactions exceeding the prescribed threshold.",
    reporting: "Suspicious transactions must be reported through the appropriate AML channel.",
  },
  {
    id: 4,
    name: "KYC Requirements 2024",
    regulator: "RBI",
    effectiveDate: "Apr 01, 2024",
    jurisdiction: "India",
    category: "KYC Compliance",
    threshold: "₹5,00,000",
    requirement: "Additional identity verification is required for higher-risk customers.",
    reporting: "Customer verification records must be retained for audit purposes.",
  },
];

function CompareRules() {
  const [leftRuleId, setLeftRuleId] = useState(1);
  const [rightRuleId, setRightRuleId] = useState(2);

  const leftRule = useMemo(
    () => rules.find((rule) => rule.id === leftRuleId) ?? rules[0],
    [leftRuleId]
  );

  const rightRule = useMemo(
    () => rules.find((rule) => rule.id === rightRuleId) ?? rules[1],
    [rightRuleId]
  );

  const sameJurisdiction =
    leftRule.jurisdiction === rightRule.jurisdiction;

  const sameCategory = leftRule.category === rightRule.category;

  return (
    <div className="compare-page">
      {/* PAGE HEADER */}
      <div className="compare-page-heading">
        <div>
          <span className="eyebrow">REGULATORY ANALYSIS</span>

          <h2>Compare Rules</h2>

          <p>
            Compare regulatory requirements and identify conflicts
            between governing rules.
          </p>
        </div>

        <div className="comparison-status">
          <span className="status-dot"></span>
          Comparison ready
        </div>
      </div>

      {/* RULE SELECTORS */}
      <section className="compare-selector-card">
        <div className="compare-selector">
          <span className="compare-label">RULE A</span>

          <select
            value={leftRuleId}
            onChange={(event) =>
              setLeftRuleId(Number(event.target.value))
            }
          >
            {rules.map((rule) => (
              <option key={rule.id} value={rule.id}>
                {rule.name}
              </option>
            ))}
          </select>

          <span className="selector-hint">
            Primary regulatory rule
          </span>
        </div>

        <div className="compare-vs">VS</div>

        <div className="compare-selector">
          <span className="compare-label">RULE B</span>

          <select
            value={rightRuleId}
            onChange={(event) =>
              setRightRuleId(Number(event.target.value))
            }
          >
            {rules.map((rule) => (
              <option key={rule.id} value={rule.id}>
                {rule.name}
              </option>
            ))}
          </select>

          <span className="selector-hint">
            Rule being compared
          </span>
        </div>
      </section>

      {/* RULE OVERVIEW */}
      <section className="comparison-grid">
        <div className="comparison-rule-card">
          <div className="comparison-card-header">
            <div>
              <span className="card-label">RULE A</span>
              <h3>{leftRule.name}</h3>
            </div>

            <span className="regulator-badge">
              {leftRule.regulator}
            </span>
          </div>

          <div className="rule-meta-grid">
            <div>
              <span>Effective Date</span>
              <strong>{leftRule.effectiveDate}</strong>
            </div>

            <div>
              <span>Jurisdiction</span>
              <strong>{leftRule.jurisdiction}</strong>
            </div>

            <div>
              <span>Category</span>
              <strong>{leftRule.category}</strong>
            </div>
          </div>
        </div>

        <div className="comparison-rule-card">
          <div className="comparison-card-header">
            <div>
              <span className="card-label">RULE B</span>
              <h3>{rightRule.name}</h3>
            </div>

            <span className="regulator-badge">
              {rightRule.regulator}
            </span>
          </div>

          <div className="rule-meta-grid">
            <div>
              <span>Effective Date</span>
              <strong>{rightRule.effectiveDate}</strong>
            </div>

            <div>
              <span>Jurisdiction</span>
              <strong>{rightRule.jurisdiction}</strong>
            </div>

            <div>
              <span>Category</span>
              <strong>{rightRule.category}</strong>
            </div>
          </div>
        </div>
      </section>

      {/* COMPARISON SUMMARY */}
      <section className="comparison-summary">
        <div className="summary-item conflict-summary">
          <strong>2</strong>
          <span>Potential Conflicts</span>
        </div>

        <div className="summary-item match-summary">
          <strong>{sameJurisdiction ? "✓" : "—"}</strong>
          <span>
            {sameJurisdiction
              ? "Same Jurisdiction"
              : "Different Jurisdiction"}
          </span>
        </div>

        <div className="summary-item match-summary">
          <strong>{sameCategory ? "✓" : "—"}</strong>
          <span>
            {sameCategory
              ? "Same Category"
              : "Different Categories"}
          </span>
        </div>

        <div className="summary-item">
          <strong>1</strong>
          <span>Requires Review</span>
        </div>
      </section>

      {/* REQUIREMENT COMPARISON */}
      <section className="comparison-detail-card">
        <div className="comparison-detail-header">
          <div>
            <span className="card-label">REQUIREMENT ANALYSIS</span>
            <h3>Regulatory Differences</h3>
          </div>

          <span className="conflict-badge">
            CONFLICT DETECTED
          </span>
        </div>

        {/* THRESHOLD */}
        <div className="comparison-row">
          <div className="comparison-field">
            <span>TRANSACTION THRESHOLD</span>
            <strong>{leftRule.threshold}</strong>
          </div>

          <div className="comparison-middle">
            <span>VS</span>
          </div>

          <div className="comparison-field">
            <span>TRANSACTION THRESHOLD</span>
            <strong>{rightRule.threshold}</strong>
          </div>
        </div>

        {/* REQUIREMENT */}
        <div className="comparison-row">
          <div className="comparison-field">
            <span>REQUIREMENT</span>
            <p>{leftRule.requirement}</p>
          </div>

          <div className="comparison-middle">
            <span>VS</span>
          </div>

          <div className="comparison-field">
            <span>REQUIREMENT</span>
            <p>{rightRule.requirement}</p>
          </div>
        </div>

        {/* REPORTING */}
        <div className="comparison-row">
          <div className="comparison-field">
            <span>REPORTING</span>
            <p>{leftRule.reporting}</p>
          </div>

          <div className="comparison-middle">
            <span>VS</span>
          </div>

          <div className="comparison-field">
            <span>REPORTING</span>
            <p>{rightRule.reporting}</p>
          </div>
        </div>
      </section>

      {/* CONFLICT SUMMARY */}
      <section className="conflict-analysis-card">
        <div className="analysis-icon">!</div>

        <div>
          <span className="card-label">ANALYSIS SUMMARY</span>

          <h3>Potential regulatory conflict identified</h3>

          <p>
            The selected rules contain different transaction
            thresholds and compliance requirements. A risk officer
            should review the governing jurisdiction and transaction
            context before determining which requirement takes
            precedence.
          </p>
        </div>

        <button className="primary-button">
          Review Conflict
        </button>
      </section>
    </div>
  );
}

export default CompareRules;