import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

type Rule = {
  id: number;
  name: string;
  regulator: string;
  category: string;
  effectiveDate: string;
  jurisdiction: string;
  risk: "High" | "Medium" | "Low";
  status: "Active";
};

const rules: Rule[] = [
  {
    id: 1,
    name: "FinCEN Circular 2024-04",
    regulator: "FinCEN",
    category: "Cross-border Transactions",
    effectiveDate: "Jan 15, 2024",
    jurisdiction: "United States",
    risk: "High",
    status: "Active",
  },
  {
    id: 2,
    name: "OCC Bulletin 2024-17",
    regulator: "OCC",
    category: "Customer Verification",
    effectiveDate: "Feb 02, 2024",
    jurisdiction: "United States",
    risk: "Medium",
    status: "Active",
  },
  {
    id: 3,
    name: "AML Regulatory Update",
    regulator: "RBI",
    category: "AML Monitoring",
    effectiveDate: "Mar 11, 2024",
    jurisdiction: "India",
    risk: "Low",
    status: "Active",
  },
  {
    id: 4,
    name: "KYC Requirements 2024",
    regulator: "RBI",
    category: "KYC Compliance",
    effectiveDate: "Apr 01, 2024",
    jurisdiction: "India",
    risk: "Medium",
    status: "Active",
  },
  {
    id: 5,
    name: "Transaction Monitoring Framework",
    regulator: "FinCEN",
    category: "Transaction Monitoring",
    effectiveDate: "May 18, 2024",
    jurisdiction: "United States",
    risk: "High",
    status: "Active",
  },
  {
    id: 6,
    name: "Customer Due Diligence Notice",
    regulator: "OCC",
    category: "Due Diligence",
    effectiveDate: "Jun 05, 2024",
    jurisdiction: "United States",
    risk: "Low",
    status: "Active",
  },
];

function ActiveRules() {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState("");
  const [regulatorFilter, setRegulatorFilter] = useState("All");
  const [riskFilter, setRiskFilter] = useState("All");

  const filteredRules = useMemo(() => {
    return rules.filter((rule) => {
      const matchesSearch =
        rule.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        rule.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
        rule.regulator.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesRegulator =
        regulatorFilter === "All" ||
        rule.regulator === regulatorFilter;

      const matchesRisk =
        riskFilter === "All" ||
        rule.risk === riskFilter;

      return matchesSearch && matchesRegulator && matchesRisk;
    });
  }, [searchTerm, regulatorFilter, riskFilter]);

  return (
    <div className="rules-page">
      {/* PAGE HEADER */}
      <div className="rules-page-heading">
        <div>
          <span className="eyebrow">REGULATORY GOVERNANCE</span>

          <h2>Active Rules</h2>

          <p>
            View the current regulatory rules governing transactions
            across your organization.
          </p>
        </div>

        <div className="rules-summary">
          <strong>{rules.length}</strong>
          <span>Active Rules</span>
        </div>
      </div>

      {/* FILTER BAR */}
      <section className="rules-filter-card">
        <div className="rules-search">
          <span>⌕</span>

          <input
            type="text"
            placeholder="Search rules, regulators, or categories..."
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
          />
        </div>

        <select
          value={regulatorFilter}
          onChange={(event) => setRegulatorFilter(event.target.value)}
        >
          <option value="All">All Regulators</option>
          <option value="FinCEN">FinCEN</option>
          <option value="OCC">OCC</option>
          <option value="RBI">RBI</option>
        </select>

        <select
          value={riskFilter}
          onChange={(event) => setRiskFilter(event.target.value)}
        >
          <option value="All">All Risk Levels</option>
          <option value="High">High Risk</option>
          <option value="Medium">Medium Risk</option>
          <option value="Low">Low Risk</option>
        </select>
      </section>

      {/* RULE TABLE */}
      <section className="rules-table-card">
        <div className="rules-table-header">
          <div>
            <span className="card-label">CURRENT REGULATIONS</span>
            <h3>Governing Rules</h3>
          </div>

          <span className="results-count">
            {filteredRules.length} results
          </span>
        </div>

        <div className="rules-table-wrapper">
          <table className="rules-table">
            <thead>
              <tr>
                <th>RULE</th>
                <th>REGULATOR</th>
                <th>CATEGORY</th>
                <th>EFFECTIVE DATE</th>
                <th>JURISDICTION</th>
                <th>RISK</th>
                <th>STATUS</th>
                <th></th>
              </tr>
            </thead>

            <tbody>
              {filteredRules.map((rule) => (
                <tr key={rule.id}>
                  <td>
                    <div className="rule-name">
                      <strong>{rule.name}</strong>
                      <span>Rule ID: RG-{String(rule.id).padStart(4, "0")}</span>
                    </div>
                  </td>

                  <td>
                    <span className="regulator-badge">
                      {rule.regulator}
                    </span>
                  </td>

                  <td>{rule.category}</td>

                  <td>{rule.effectiveDate}</td>

                  <td>{rule.jurisdiction}</td>

                  <td>
                    <span
                      className={`rule-risk ${rule.risk.toLowerCase()}`}
                    >
                      {rule.risk}
                    </span>
                  </td>

                  <td>
                    <span className="active-status">
                      <span className="status-dot"></span>
                      {rule.status}
                    </span>
                  </td>

                  <td>
                    <button
                      className="view-rule-button"
                      onClick={() => navigate(`/rules/${rule.id}`)}
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {filteredRules.length === 0 && (
            <div className="empty-rules">
              <strong>No rules found</strong>
              <span>
                Try changing your search or filter criteria.
              </span>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

export default ActiveRules;