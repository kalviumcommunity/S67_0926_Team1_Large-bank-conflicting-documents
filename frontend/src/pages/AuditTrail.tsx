import { useMemo, useState } from "react";

type AuditEvent = {
  id: number;
  action: string;
  description: string;
  user: string;
  role: string;
  resource: string;
  resourceType: string;
  timestamp: string;
  status: "Success" | "Review Required" | "Critical";
};

const auditEvents: AuditEvent[] = [
  {
    id: 1,
    action: "Rule Updated",
    description: "Governing rule configuration was updated",
    user: "Marcus Vance",
    role: "Senior Risk Officer",
    resource: "FinCEN Circular 2024-04",
    resourceType: "Rule",
    timestamp: "Oct 05, 2026 · 10:42 AM",
    status: "Success",
  },
  {
    id: 2,
    action: "Conflict Detected",
    description: "Conflicting regulatory requirements were identified",
    user: "Compliance Engine",
    role: "Automated System",
    resource: "OCC Bulletin 2024-17",
    resourceType: "Rule",
    timestamp: "Oct 05, 2026 · 10:18 AM",
    status: "Review Required",
  },
  {
    id: 3,
    action: "Document Added",
    description: "New regulatory document was added to the repository",
    user: "Sarah Mitchell",
    role: "Compliance Analyst",
    resource: "AML Regulatory Update",
    resourceType: "Document",
    timestamp: "Oct 05, 2026 · 09:54 AM",
    status: "Success",
  },
  {
    id: 4,
    action: "Rule Validation",
    description: "Transaction was validated against governing rules",
    user: "James Carter",
    role: "Risk Analyst",
    resource: "$450,000 Cross-Border Transfer",
    resourceType: "Transaction",
    timestamp: "Oct 05, 2026 · 09:31 AM",
    status: "Success",
  },
  {
    id: 5,
    action: "Conflict Escalated",
    description: "Unresolved regulatory conflict was escalated",
    user: "Marcus Vance",
    role: "Senior Risk Officer",
    resource: "KYC Requirements 2024",
    resourceType: "Rule",
    timestamp: "Oct 05, 2026 · 08:46 AM",
    status: "Critical",
  },
  {
    id: 6,
    action: "Document Reviewed",
    description: "Regulatory document review was completed",
    user: "Sarah Mitchell",
    role: "Compliance Analyst",
    resource: "Transaction Monitoring Framework",
    resourceType: "Document",
    timestamp: "Oct 04, 2026 · 05:22 PM",
    status: "Success",
  },
  {
    id: 7,
    action: "Rule Compared",
    description: "Two regulatory rules were compared",
    user: "James Carter",
    role: "Risk Analyst",
    resource: "FinCEN vs OCC Requirements",
    resourceType: "Comparison",
    timestamp: "Oct 04, 2026 · 04:17 PM",
    status: "Success",
  },
  {
    id: 8,
    action: "Access Attempt",
    description: "Restricted document access was attempted",
    user: "Unknown User",
    role: "External",
    resource: "Internal AML Audit Report Q1",
    resourceType: "Document",
    timestamp: "Oct 04, 2026 · 02:09 PM",
    status: "Critical",
  },
];

function AuditTrail() {
  const [searchTerm, setSearchTerm] = useState("");
  const [actionFilter, setActionFilter] = useState("All");
  const [statusFilter, setStatusFilter] = useState("All");

  const filteredEvents = useMemo(() => {
    return auditEvents.filter((event) => {
      const search = searchTerm.toLowerCase();

      const matchesSearch =
        event.action.toLowerCase().includes(search) ||
        event.description.toLowerCase().includes(search) ||
        event.user.toLowerCase().includes(search) ||
        event.resource.toLowerCase().includes(search);

      const matchesAction =
        actionFilter === "All" ||
        event.action === actionFilter;

      const matchesStatus =
        statusFilter === "All" ||
        event.status === statusFilter;

      return matchesSearch && matchesAction && matchesStatus;
    });
  }, [searchTerm, actionFilter, statusFilter]);

  const successfulEvents = auditEvents.filter(
    (event) => event.status === "Success"
  ).length;

  const reviewEvents = auditEvents.filter(
    (event) => event.status === "Review Required"
  ).length;

  const criticalEvents = auditEvents.filter(
    (event) => event.status === "Critical"
  ).length;

  return (
    <div className="audit-page">
      {/* PAGE HEADER */}
      <div className="audit-page-heading">
        <div>
          <span className="eyebrow">
            COMPLIANCE ACTIVITY MONITORING
          </span>

          <h2>Audit Trail</h2>

          <p>
            Track regulatory changes, compliance actions, and
            system activity across your organization.
          </p>
        </div>

        <button className="secondary-button">
          Export Audit Log
        </button>
      </div>

      {/* STATISTICS */}
      <section className="audit-stats">
        <div className="audit-stat-card">
          <span>TOTAL EVENTS</span>
          <strong>{auditEvents.length}</strong>
          <small>Recorded activity</small>
        </div>

        <div className="audit-stat-card">
          <span>SUCCESSFUL ACTIONS</span>
          <strong>{successfulEvents}</strong>
          <small className="audit-positive">
            Completed successfully
          </small>
        </div>

        <div className="audit-stat-card">
          <span>REVIEW REQUIRED</span>
          <strong>{reviewEvents}</strong>
          <small className="audit-warning">
            Require attention
          </small>
        </div>

        <div className="audit-stat-card">
          <span>CRITICAL EVENTS</span>
          <strong>{criticalEvents}</strong>
          <small className="audit-negative">
            Priority attention
          </small>
        </div>
      </section>

      {/* FILTERS */}
      <section className="audit-filter-card">
        <div className="audit-search">
          <span>⌕</span>

          <input
            type="text"
            placeholder="Search audit activity, users, rules..."
            value={searchTerm}
            onChange={(event) =>
              setSearchTerm(event.target.value)
            }
          />
        </div>

        <select
          value={actionFilter}
          onChange={(event) =>
            setActionFilter(event.target.value)
          }
        >
          <option value="All">All Actions</option>
          <option value="Rule Updated">Rule Updated</option>
          <option value="Conflict Detected">
            Conflict Detected
          </option>
          <option value="Document Added">
            Document Added
          </option>
          <option value="Rule Validation">
            Rule Validation
          </option>
          <option value="Conflict Escalated">
            Conflict Escalated
          </option>
          <option value="Document Reviewed">
            Document Reviewed
          </option>
          <option value="Rule Compared">Rule Compared</option>
          <option value="Access Attempt">
            Access Attempt
          </option>
        </select>

        <select
          value={statusFilter}
          onChange={(event) =>
            setStatusFilter(event.target.value)
          }
        >
          <option value="All">All Statuses</option>
          <option value="Success">Success</option>
          <option value="Review Required">
            Review Required
          </option>
          <option value="Critical">Critical</option>
        </select>
      </section>

      {/* AUDIT LOG */}
      <section className="audit-table-card">
        <div className="audit-table-header">
          <div>
            <span className="card-label">
              SYSTEM ACTIVITY LOG
            </span>

            <h3>Recent Compliance Activity</h3>
          </div>

          <span className="results-count">
            {filteredEvents.length} events
          </span>
        </div>

        <div className="audit-table-wrapper">
          <table className="audit-table">
            <thead>
              <tr>
                <th>ACTION</th>
                <th>USER</th>
                <th>RESOURCE</th>
                <th>DATE & TIME</th>
                <th>STATUS</th>
                <th></th>
              </tr>
            </thead>

            <tbody>
              {filteredEvents.map((event) => (
                <tr key={event.id}>
                  <td>
                    <div className="audit-action">
                      <div
                        className={`audit-action-icon ${event.status
                          .toLowerCase()
                          .replace(" ", "-")}`}
                      >
                        {event.status === "Success"
                          ? "✓"
                          : event.status === "Critical"
                            ? "!"
                            : "↗"}
                      </div>

                      <div>
                        <strong>{event.action}</strong>
                        <span>{event.description}</span>
                      </div>
                    </div>
                  </td>

                  <td>
                    <div className="audit-user">
                      <strong>{event.user}</strong>
                      <span>{event.role}</span>
                    </div>
                  </td>

                  <td>
                    <div className="audit-resource">
                      <strong>{event.resource}</strong>
                      <span>{event.resourceType}</span>
                    </div>
                  </td>

                  <td>
                    <span className="audit-time">
                      {event.timestamp}
                    </span>
                  </td>

                  <td>
                    <span
                      className={`audit-status ${event.status
                        .toLowerCase()
                        .replace(" ", "-")}`}
                    >
                      <span className="audit-status-dot"></span>
                      {event.status}
                    </span>
                  </td>

                  <td>
                    <button className="view-audit-button">
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {filteredEvents.length === 0 && (
            <div className="empty-audit">
              <strong>No audit events found</strong>

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

export default AuditTrail;