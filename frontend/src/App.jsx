import { NavLink, Route, Routes } from 'react-router-dom';
import Dashboard from './pages/Dashboard.jsx';
import Books from './pages/Books.jsx';
import Borrowers from './pages/Borrowers.jsx';
import BorrowReturn from './pages/BorrowReturn.jsx';
import SearchPage from './pages/SearchPage.jsx';
import Analytics from './pages/Analytics.jsx';

export default function App() {
  const links = [
    { to: '/', label: 'Dashboard', end: true },
    { to: '/books', label: 'Books' },
    { to: '/borrowers', label: 'Borrowers' },
    { to: '/transactions', label: 'Borrow / Return' },
    { to: '/search', label: 'Search' },
    { to: '/analytics', label: 'Analytics' },
  ];

  return (
    <div className="app">
      <header className="app-header">
        <h1>Library Management System</h1>
        <nav>
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.end}
              className={({ isActive }) =>
                'nav-link' + (isActive ? ' nav-link-active' : '')
              }
            >
              {l.label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main className="app-main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/books" element={<Books />} />
          <Route path="/borrowers" element={<Borrowers />} />
          <Route path="/transactions" element={<BorrowReturn />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/analytics" element={<Analytics />} />
        </Routes>
      </main>
      <footer className="app-footer">
        Phase 2 Capstone &middot; AFDE Jan26 &middot; Sharath
      </footer>
    </div>
  );
}
