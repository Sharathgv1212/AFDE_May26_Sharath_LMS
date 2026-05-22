import { useEffect, useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import Alert from '../components/Alert.jsx';
import {
  categoryBorrowing,
  etlRuns,
  monthlyTrends,
  overdue as fetchOverdue,
  popularBooks,
  refresh as refreshEtl,
  summary as fetchSummary,
} from '../services/analytics.js';

const CHART_COLORS = ['#2563eb', '#16a34a', '#dc2626', '#ca8a04', '#7c3aed', '#0891b2', '#db2777'];

function Stat({ label, value }) {
  return (
    <div className="stat">
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value ?? '—'}</div>
    </div>
  );
}

export default function Analytics() {
  const [sum, setSum] = useState(null);
  const [pop, setPop] = useState([]);
  const [cat, setCat] = useState([]);
  const [trend, setTrend] = useState([]);
  const [over, setOver] = useState([]);
  const [runs, setRuns] = useState([]);
  const [overdueFilter, setOverdueFilter] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const loadAll = async () => {
    try {
      const [s, p, c, m, o, r] = await Promise.all([
        fetchSummary(),
        popularBooks(10),
        categoryBorrowing(),
        monthlyTrends(),
        fetchOverdue(overdueFilter || undefined),
        etlRuns(5),
      ]);
      setSum(s);
      setPop(p);
      setCat(c);
      setTrend(m);
      setOver(o);
      setRuns(r);
    } catch (err) {
      setError(err.friendlyMessage || 'Failed to load analytics');
    }
  };

  useEffect(() => {
    loadAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [overdueFilter]);

  const handleRefresh = async () => {
    setRefreshing(true);
    setError('');
    setSuccess('');
    try {
      const res = await refreshEtl();
      setSuccess(
        `ETL ${res.status}: extracted ${res.rows_extracted}, loaded ${res.rows_loaded}`
      );
      await loadAll();
    } catch (err) {
      setError(err.friendlyMessage || 'Refresh failed');
    } finally {
      setRefreshing(false);
    }
  };

  const noEtlYet = sum && sum.last_etl_run === null;

  return (
    <div>
      <Alert message={error} onDismiss={() => setError('')} />
      <Alert kind="success" message={success} onDismiss={() => setSuccess('')} />

      <div className="card">
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: 12,
          }}
        >
          <div>
            <h2 style={{ margin: 0 }}>Analytics</h2>
            <div className="muted">
              {sum?.last_etl_run
                ? `Last ETL run: ${new Date(sum.last_etl_run).toLocaleString()} · ${sum.last_etl_status}`
                : 'ETL has not run yet — click "Refresh analytics" to populate the dashboard.'}
            </div>
          </div>
          <button
            className="btn-primary"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            {refreshing ? 'Refreshing…' : 'Refresh analytics'}
          </button>
        </div>
      </div>

      {noEtlYet && (
        <div className="card">
          <p className="muted">
            No analytics data yet. Run <code>py -m etl.run</code> from the
            project root, or hit the "Refresh analytics" button above.
          </p>
        </div>
      )}

      <div className="stat-grid">
        <Stat label="Total Books" value={sum?.total_books} />
        <Stat label="Total Borrowers" value={sum?.total_borrowers} />
        <Stat label="Total Transactions" value={sum?.total_transactions} />
        <Stat label="Active Loans" value={sum?.active_loans} />
        <Stat label="Overdue" value={sum?.overdue_count} />
        <Stat label="Top Category" value={sum?.top_category} />
        <Stat
          label="Most Borrowed"
          value={
            sum?.most_borrowed_title
              ? `${sum.most_borrowed_title} (${sum.most_borrowed_count})`
              : '—'
          }
        />
      </div>

      {/* Popular books — horizontal-ish bar chart */}
      <div className="card" style={{ marginTop: 18 }}>
        <h2>Most Borrowed Books (top 10)</h2>
        {pop.length === 0 ? (
          <p className="muted">No data yet.</p>
        ) : (
          <div style={{ width: '100%', height: 340 }}>
            <ResponsiveContainer>
              <BarChart data={pop} margin={{ top: 12, right: 24, left: 8, bottom: 60 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis
                  dataKey="title"
                  angle={-25}
                  textAnchor="end"
                  height={80}
                  interval={0}
                  style={{ fontSize: 11 }}
                />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="borrow_count" fill="#2563eb" name="Borrows" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Category breakdown */}
      <div
        className="card"
        style={{
          marginTop: 18,
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))',
          gap: 24,
        }}
      >
        <div>
          <h2>Category-wise Borrowing</h2>
          {cat.length === 0 ? (
            <p className="muted">No data yet.</p>
          ) : (
            <div style={{ width: '100%', height: 300 }}>
              <ResponsiveContainer>
                <PieChart>
                  <Pie
                    data={cat}
                    dataKey="borrow_count"
                    nameKey="category"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label={({ category, borrow_count }) =>
                      `${category}: ${borrow_count}`
                    }
                  >
                    {cat.map((_, idx) => (
                      <Cell key={idx} fill={CHART_COLORS[idx % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
        <div>
          <h2>By Category (table)</h2>
          {cat.length === 0 ? (
            <p className="muted">—</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Category</th>
                  <th>Borrows</th>
                  <th>Unique borrowers</th>
                </tr>
              </thead>
              <tbody>
                {cat.map((c) => (
                  <tr key={c.category}>
                    <td>{c.category}</td>
                    <td>{c.borrow_count}</td>
                    <td>{c.unique_borrowers}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Monthly trends */}
      <div className="card" style={{ marginTop: 18 }}>
        <h2>Monthly Borrowing Trends</h2>
        {trend.length === 0 ? (
          <p className="muted">No data yet.</p>
        ) : (
          <div style={{ width: '100%', height: 320 }}>
            <ResponsiveContainer>
              <LineChart data={trend} margin={{ top: 12, right: 24, left: 8, bottom: 30 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="year_month" angle={-30} textAnchor="end" height={60} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="borrow_count"
                  stroke="#2563eb"
                  name="Borrows"
                  strokeWidth={2}
                />
                <Line
                  type="monotone"
                  dataKey="return_count"
                  stroke="#16a34a"
                  name="Returns"
                  strokeWidth={2}
                />
                <Line
                  type="monotone"
                  dataKey="overdue_count"
                  stroke="#dc2626"
                  name="Overdue"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Overdue analytics */}
      <div className="card" style={{ marginTop: 18 }}>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: 12,
            flexWrap: 'wrap',
            gap: 8,
          }}
        >
          <h2 style={{ margin: 0 }}>Overdue Transactions</h2>
          <select
            value={overdueFilter}
            onChange={(e) => setOverdueFilter(e.target.value)}
            style={{
              padding: '6px 10px',
              border: '1px solid #d1d5db',
              borderRadius: 6,
            }}
          >
            <option value="">All overdue</option>
            <option value="Active Overdue">Active overdue</option>
            <option value="Returned Late">Returned late</option>
          </select>
        </div>
        {over.length === 0 ? (
          <p className="muted">No overdue transactions.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Book</th>
                <th>Borrower</th>
                <th>Borrowed</th>
                <th>Returned</th>
                <th>Days</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {over.slice(0, 50).map((t) => (
                <tr key={t.transaction_id}>
                  <td>{t.transaction_id}</td>
                  <td>{t.book_title}</td>
                  <td>{t.borrower_name}</td>
                  <td>{new Date(t.borrow_date).toLocaleDateString()}</td>
                  <td>
                    {t.return_date
                      ? new Date(t.return_date).toLocaleDateString()
                      : '—'}
                  </td>
                  <td>{t.loan_duration_days}</td>
                  <td>
                    <span
                      className={
                        t.overdue_label === 'Active Overdue'
                          ? 'badge badge-borrowed'
                          : 'badge badge-available'
                      }
                    >
                      {t.overdue_label}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {over.length > 50 && (
          <p className="muted">Showing first 50 of {over.length} rows.</p>
        )}
      </div>

      {/* ETL run log */}
      <div className="card">
        <h2>Recent ETL Runs</h2>
        {runs.length === 0 ? (
          <p className="muted">No ETL runs recorded yet.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>When</th>
                <th>Status</th>
                <th>Extracted</th>
                <th>Loaded</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((r) => (
                <tr key={r.run_id}>
                  <td>{r.run_id}</td>
                  <td>{new Date(r.ran_at).toLocaleString()}</td>
                  <td>
                    <span
                      className={
                        r.status === 'success'
                          ? 'badge badge-available'
                          : 'badge badge-borrowed'
                      }
                    >
                      {r.status}
                    </span>
                  </td>
                  <td>{r.rows_extracted}</td>
                  <td>{r.rows_loaded}</td>
                  <td className="muted" style={{ fontSize: 12 }}>
                    {r.error || r.cleaning_stats || '—'}
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
