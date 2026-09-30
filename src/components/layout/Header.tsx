const Header = () => {
  return (
    <header className="header">
      <div className="header-search">
        <span className="search-icon">⌕</span>

        <input
          type="text"
          placeholder="Search statutory rules, FINCEN circulars, OCC bulletins..."
        />
      </div>

      <div className="header-actions">
        <div className="system-status">
          <span className="status-dot"></span>
          <span>FinCEN/Basel III Sync</span>
          <strong>LIVE</strong>
        </div>

        <button className="header-button">
          Export Audit
        </button>

        <div className="header-avatar">
          MV
        </div>
      </div>
    </header>
  );
};

export default Header;