import { useEffect, useState } from 'react';
import { bookStats } from '../services/books.js';
import {
  recentTransactions,
  transactionStats,
} from '../services/transactions.js';
import Alert from '../components/Alert.jsx';

function StatCard({ label, value }) {
  return (
    <div className="stat">
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
    </div>
  );
}

export default function Dashboard() {
  const [books, setBooks] = useState(null);
  const [txn, setTxn] = useState(null);
  const [recent, setRecent] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const [b, t, r] = await Promise.all([
          bookStats(),
          transactionStats(),
          recentTransactions(5),
        ]);
        setBooks(b);
        setTxn(t);
        setRecent(r);
      } catch (err) {
        setError(err.friendlyMessage || 'Failed to load dashboard');
      }
    })();
  }, []);

  return (
    <div>
      <Alert message={error} onDismiss={() => setError('')} />

      <div className="stat-grid">
        <StatCard label="Total Books" value={books?.total_books ?? '—'} />
        <StatCard label="Available" value={books?.available_books ?? '—'} />
        <StatCard label="Borrowed" value={books?.borrowed_books ?? '—'} />
        <StatCard label="Active Loans" value={txn?.active_loans ?? '—'} />
        <StatCard label="Total Transactions" value={txn?.total_transactions ?? '—'} />
      </div>

      <div className="card" style={{ marginTop: 18 }}>
        <h2>Books by Category</h2>
        {books?.categories && Object.keys(books.categories).length > 0 ? (
          <table>
            <thead>
              <tr>
                <th>Category</th>
                <th>Books</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(books.categories).map(([cat, count]) => (
                <tr key={cat}>
                  <td>{cat}</td>
                  <td>{count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="muted">No books yet.</p>
        )}
      </div>

      <div className="card">
        <h2>Recent Transactions</h2>
        {recent.length === 0 ? (
          <p className="muted">No recent transactions.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Book</th>
                <th>Borrower</th>
                <th>Borrowed</th>
                <th>Returned</th>
              </tr>
            </thead>
            <tbody>
              {recent.map((t) => (
                <tr key={t.transaction_id}>
                  <td>{t.transaction_id}</td>
                  <td>{t.book_title}</td>
                  <td>{t.borrower_name}</td>
                  <td>{new Date(t.borrow_date).toLocaleString()}</td>
                  <td>
                    {t.return_date
                      ? new Date(t.return_date).toLocaleString()
                      : <span className="badge badge-borrowed">Open</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
