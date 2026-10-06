import { useMemo, useState } from "react";

type Document = {
  id: number;
  title: string;
  type: "Circular" | "Bulletin" | "Regulatory Update" | "Audit Report";
  regulator: string;
  published: string;
  effectiveDate: string;
  status: "Current" | "Under Review" | "Archived";
  conflicts: number;
};

const documents: Document[] = [
  {
    id: 1,
    title: "FinCEN Circular 2024-04",
    type: "Circular",
    regulator: "FinCEN",
    published: "Jan 10, 2024",
    effectiveDate: "Jan 15, 2024",
    status: "Current",
    conflicts: 2,
  },
  {
    id: 2,
    title: "OCC Bulletin 2024-17",
    type: "Bulletin",
    regulator: "OCC",
    published: "Jan 28, 2024",
    effectiveDate: "Feb 02, 2024",
    status: "Current",
    conflicts: 1,
  },
  {
    id: 3,
    title: "AML Regulatory Update",
    type: "Regulatory Update",
    regulator: "RBI",
    published: "Mar 05, 2024",
    effectiveDate: "Mar 11, 2024",
    status: "Current",
    conflicts: 0,
  },
  {
    id: 4,
    title: "Internal AML Audit Report Q1",
    type: "Audit Report",
    regulator: "Internal Audit",
    published: "Apr 12, 2024",
    effectiveDate: "Apr 12, 2024",
    status: "Under Review",
    conflicts: 3,
  },
  {
    id: 5,
    title: "KYC Requirements 2024",
    type: "Circular",
    regulator: "RBI",
    published: "Mar 25, 2024",
    effectiveDate: "Apr 01, 2024",
    status: "Current",
    conflicts: 1,
  },
  {
    id: 6,
    title: "Transaction Monitoring Framework",
    type: "Bulletin",
    regulator: "FinCEN",
    published: "May 10, 2024",
    effectiveDate: "May 18, 2024",
    status: "Current",
    conflicts: 2,
  },
  {
    id: 7,
    title: "Customer Due Diligence Notice",
    type: "Regulatory Update",
    regulator: "OCC",
    published: "Jun 01, 2024",
    effectiveDate: "Jun 05, 2024",
    status: "Current",
    conflicts: 0,
  },
  {
    id: 8,
    title: "Legacy Customer Verification Report",
    type: "Audit Report",
    regulator: "Internal Audit",
    published: "Dec 18, 2023",
    effectiveDate: "Dec 18, 2023",
    status: "Archived",
    conflicts: 4,
  },
];

function Documents() {
  const [searchTerm, setSearchTerm] = useState("");
  const [regulatorFilter, setRegulatorFilter] = useState("All");
  const [typeFilter, setTypeFilter] = useState("All");

  const filteredDocuments = useMemo(() => {
    return documents.filter((document) => {
      const matchesSearch =
        document.title
          .toLowerCase()
          .includes(searchTerm.toLowerCase()) ||
        document.regulator
          .toLowerCase()
          .includes(searchTerm.toLowerCase()) ||
        document.type
          .toLowerCase()
          .includes(searchTerm.toLowerCase());

      const matchesRegulator =
        regulatorFilter === "All" ||
        document.regulator === regulatorFilter;

      const matchesType =
        typeFilter === "All" ||
        document.type === typeFilter;

      return matchesSearch && matchesRegulator && matchesType;
    });
  }, [searchTerm, regulatorFilter, typeFilter]);

  const currentDocuments = documents.filter(
    (document) => document.status === "Current"
  ).length;

  const conflictDocuments = documents.filter(
    (document) => document.conflicts > 0
  ).length;

  const circularDocuments = documents.filter(
    (document) => document.type === "Circular"
  ).length;

  return (
    <div className="documents-page">
      {/* PAGE HEADER */}
      <div className="documents-page-heading">
        <div>
          <span className="eyebrow">
            REGULATORY DOCUMENT MANAGEMENT
          </span>

          <h2>Documents</h2>

          <p>
            Manage regulatory circulars, bulletins, updates, and
            internal compliance reports.
          </p>
        </div>

        <button className="primary-button">
          + Add Document
        </button>
      </div>

      {/* SUMMARY CARDS */}
      <section className="document-stats">
        <div className="document-stat-card">
          <span>TOTAL DOCUMENTS</span>
          <strong>{documents.length}</strong>
          <small>Across all sources</small>
        </div>

        <div className="document-stat-card">
          <span>CURRENT DOCUMENTS</span>
          <strong>{currentDocuments}</strong>
          <small className="positive">Currently governing</small>
        </div>

        <div className="document-stat-card">
          <span>REGULATORY CIRCULARS</span>
          <strong>{circularDocuments}</strong>
          <small>Active circular sources</small>
        </div>

        <div className="document-stat-card warning">
          <span>CONFLICTING DOCUMENTS</span>
          <strong>{conflictDocuments}</strong>
          <small className="negative">
            Require attention
          </small>
        </div>
      </section>

      {/* FILTER BAR */}
      <section className="documents-filter-card">
        <div className="documents-search">
          <span>⌕</span>

          <input
            type="text"
            placeholder="Search documents, regulators, or document types..."
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
          />
        </div>

        <select
          value={regulatorFilter}
          onChange={(event) =>
            setRegulatorFilter(event.target.value)
          }
        >
          <option value="All">All Regulators</option>
          <option value="FinCEN">FinCEN</option>
          <option value="OCC">OCC</option>
          <option value="RBI">RBI</option>
          <option value="Internal Audit">Internal Audit</option>
        </select>

        <select
          value={typeFilter}
          onChange={(event) => setTypeFilter(event.target.value)}
        >
          <option value="All">All Document Types</option>
          <option value="Circular">Circular</option>
          <option value="Bulletin">Bulletin</option>
          <option value="Regulatory Update">
            Regulatory Update
          </option>
          <option value="Audit Report">Audit Report</option>
        </select>
      </section>

      {/* DOCUMENT TABLE */}
      <section className="documents-table-card">
        <div className="documents-table-header">
          <div>
            <span className="card-label">
              REGULATORY DOCUMENT REPOSITORY
            </span>

            <h3>Document Library</h3>
          </div>

          <span className="results-count">
            {filteredDocuments.length} results
          </span>
        </div>

        <div className="documents-table-wrapper">
          <table className="documents-table">
            <thead>
              <tr>
                <th>DOCUMENT</th>
                <th>TYPE</th>
                <th>REGULATOR</th>
                <th>PUBLISHED</th>
                <th>EFFECTIVE</th>
                <th>CONFLICTS</th>
                <th>STATUS</th>
                <th></th>
              </tr>
            </thead>

            <tbody>
              {filteredDocuments.map((document) => (
                <tr key={document.id}>
                  <td>
                    <div className="document-name">
                      <strong>{document.title}</strong>

                      <span>
                        Document ID: DOC-
                        {String(document.id).padStart(4, "0")}
                      </span>
                    </div>
                  </td>

                  <td>
                    <span className="document-type-badge">
                      {document.type}
                    </span>
                  </td>

                  <td>{document.regulator}</td>

                  <td>{document.published}</td>

                  <td>{document.effectiveDate}</td>

                  <td>
                    {document.conflicts > 0 ? (
                      <span className="document-conflict">
                        {document.conflicts}{" "}
                        {document.conflicts === 1
                          ? "Conflict"
                          : "Conflicts"}
                      </span>
                    ) : (
                      <span className="no-conflict">
                        No conflicts
                      </span>
                    )}
                  </td>

                  <td>
                    <span
                      className={`document-status ${document.status
                        .toLowerCase()
                        .replace(" ", "-")}`}
                    >
                      <span className="status-dot"></span>
                      {document.status}
                    </span>
                  </td>

                  <td>
                    <button className="view-document-button">
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {filteredDocuments.length === 0 && (
            <div className="empty-documents">
              <strong>No documents found</strong>

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

export default Documents;