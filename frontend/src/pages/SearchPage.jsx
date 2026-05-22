import { useState } from 'react';
import Alert from '../components/Alert.jsx';
import AvailabilityBadge from '../components/AvailabilityBadge.jsx';
import { CATEGORIES } from '../services/books.js';
import { searchBooks } from '../services/search.js';

export default function SearchPage() {
  const [filters, setFilters] = useState({
    q: '',
    title: '',
    author: '',
    category: '',
    available: '',
  });
  const [results, setResults] = useState([]);
  const [searched, setSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) =>
    setFilters((f) => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const params = {};
      for (const [k, v] of Object.entries(filters)) {
        if (v === '' || v === null) continue;
        if (k === 'available') params.available = v === 'true';
        else params[k] = v;
      }
      const data = await searchBooks(params);
      setResults(data);
      setSearched(true);
    } catch (err) {
      setError(err.friendlyMessage || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFilters({ q: '', title: '', author: '', category: '', available: '' });
    setResults([]);
    setSearched(false);
  };

  return (
    <div>
      <Alert message={error} onDismiss={() => setError('')} />

      <div className="card">
        <h2>Search Books</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label>Keyword (any field)</label>
              <input
                name="q"
                value={filters.q}
                onChange={handleChange}
                placeholder="e.g. orwell"
              />
            </div>
            <div className="form-group">
              <label>Title</label>
              <input name="title" value={filters.title} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Author</label>
              <input name="author" value={filters.author} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Category</label>
              <select
                name="category"
                value={filters.category}
                onChange={handleChange}
              >
                <option value="">Any</option>
                {CATEGORIES.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Availability</label>
              <select
                name="available"
                value={filters.available}
                onChange={handleChange}
              >
                <option value="">Any</option>
                <option value="true">Available</option>
                <option value="false">Borrowed</option>
              </select>
            </div>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Searching…' : 'Search'}
            </button>
            <button type="button" className="btn-secondary" onClick={handleReset}>
              Reset
            </button>
          </div>
        </form>
      </div>

      {searched && (
        <div className="card">
          <h2>Results ({results.length})</h2>
          {results.length === 0 ? (
            <p className="muted">No books matched the filters.</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Title</th>
                  <th>Author</th>
                  <th>Category</th>
                  <th>ISBN</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {results.map((b) => (
                  <tr key={b.book_id}>
                    <td>{b.book_id}</td>
                    <td>{b.title}</td>
                    <td>{b.author}</td>
                    <td>{b.category}</td>
                    <td>{b.isbn}</td>
                    <td><AvailabilityBadge status={b.availability_status} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}
