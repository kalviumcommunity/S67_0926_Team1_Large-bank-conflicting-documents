import { NavLink } from "react-router-dom";
import { navigationItems } from "../../lib/navigation";

const Sidebar = () => {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon">B</div>

        <div>
          <h1>Bank Management</h1>
          <span>COMPLIANCE & RISK</span>
        </div>
      </div>

      <div className="sidebar-section">
        <span className="sidebar-section-title">
          GOVERNANCE NAVIGATION
        </span>

        <nav className="sidebar-nav">
          {navigationItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? "active" : ""}`
              }
            >
              <span className="sidebar-icon">{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </div>

      <div className="sidebar-user">
        <div className="user-avatar">MV</div>

        <div className="user-info">
          <strong>Marcus Vance</strong>
          <span>Senior Risk Officer</span>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;