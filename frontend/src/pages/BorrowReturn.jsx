import { useEffect, useState } from 'react';
import Alert from '../components/Alert.jsx';
import { listBooks } from '../services/books.js';
import { listBorrowers } from '../services/borrowers.js';
import {
  borrowBook,
  listTransactions,
  returnBook,
} from '../services/transactions.js';

export default function BorrowReturn() {
  const [books, setBooks] = useState([]);
  const [borrowers, setBorrowers] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [bookId, setBookId] = useState('');
  const [borrowerId, setBorrowerId] = useState('');
  const [activeOnly, setActiveOnly] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const refreshAll = async () => {
    try {
      const [b, br, tx] = await Promise.all([
        listBooks(),
        listBorrowers(),
        listTransactions({ active_only: activeOnly, limit: 100 }),
      ]);
      setBooks(b);
      setBorrowers(br);
      setTransactions(tx);
    } catch (err) {
      setError(err.friendlyMessage || 'Failed to load data');
    }
  };

  useEffect(() => {
    refreshAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeOnly]);

  const handleBorrow = async (e) => {
    e.preventDefault();
    if (!bookId || !borrowerId) {
      setError('Pick both a book and a borrower');
      return;
    }
    setSubmitting(true);
    setError('');
    try {
      await borrowBook(Number(bookId), Number(borrowerId));
      setSuccess('Book borrowed');
      setBookId('');
      setBorrowerId('');
      await refreshAll();
    } catch (err) {
      setError(err.friendlyMessage || 'Failed to borrow');
    } finally {
      setSubmitting(false);
    }
  };

  const handleReturn = async (txn) => {
    if (!confirm(`Return "${txn.book_title}"?`)) return;
    setError('');
    try {
      await returnBook(txn.transaction_id);
      setSuccess('Book returned');
      await refreshAll();
    } catch (err) {
      setError(err.friendlyMessage || 'Failed to return book');
    }
  };

  const availableBooks = books.filter(
    (b) => b.availability_status === 'Available'
  );

  return (
    <div>
      <Alert message={error} onDismiss={() => setError('')} />
      <Alert kind="success" message={success} onDismiss={() => setSuccess('')} />

      <div className="card">
        <h2>Borrow a Book</h2>
        <form onSubmit={handleBorrow}>
          <div className="form-row">
            <div className="form-group">
              <label>Book (only available shown)</label>
              <select value={bookId} onChange={(e) => setBookId(e.target.value)}>
                <option value="">— select —</option>
                {availableBooks.map((b) => (
                  <option key={b.book_id} value={b.book_id}>
                    #{b.book_id} · {b.title} — {b.author}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Borrower</label>
              <select
                value={borrowerId}
                onChange={(e) => setBorrowerId(e.target.value)}
              >
                <option value="">— select —</option>
                {borrowers.map((br) => (
                  <option key={br.borrower_id} value={br.borrower_id}>
                    #{br.borrower_id} · {br.borrower_name}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn-primary" disabled={submitting}>
              {submitting ? 'Working…' : 'Borrow'}
            </button>
          </div>
        </form>
      </div>

      <div className="card">
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: 12,
          }}
        >
          <h2 style={{ margin: 0 }}>Transactions</h2>
          <label className="muted">
            <input
              type="checkbox"
              checked={activeOnly}
              onChange={(e) => setActiveOnly(e.target.checked)}
            />{' '}
            Show only active loans
          </label>
        </div>
        {transactions.length === 0 ? (
          <p className="muted">No transactions to show.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Book</th>
                <th>Borrower</th>
                <th>Borrowed</th>
                <th>Returned</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((t) => (
                <tr key={t.transaction_id}>
                  <td>{t.transaction_id}</td>
                  <td>{t.book_title}</td>
                  <td>{t.borrower_name}</td>
                  <td>{new Date(t.borrow_date).toLocaleString()}</td>
                  <td>
                    {t.return_date ? (
                      new Date(t.return_date).toLocaleString()
                    ) : (
                      <span className="badge badge-borrowed">Open</span>
                    )}
                  </td>
                  <td>
                    {!t.return_date && (
                      <button
                        className="btn-primary"
                        onClick={() => handleReturn(t)}
                      >
                        Return
                      </button>
                    )}
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
