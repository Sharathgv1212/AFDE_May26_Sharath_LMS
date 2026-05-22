import { useEffect, useState } from 'react';
import Alert from '../components/Alert.jsx';
import BorrowerForm from '../components/BorrowerForm.jsx';
import {
  createBorrower,
  deleteBorrower,
  listBorrowers,
  updateBorrower,
} from '../services/borrowers.js';

export default function Borrowers() {
  const [items, setItems] = useState([]);
  const [editing, setEditing] = useState(null);
  const [showAdd, setShowAdd] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const refresh = async () => {
    try {
      setItems(await listBorrowers());
    } catch (err) {
      setError(err.friendlyMessage || 'Failed to load borrowers');
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const handleCreate = async (values) => {
    setSubmitting(true);
    setError('');
    try {
      await createBorrower(values);
      setSuccess('Borrower added');
      setShowAdd(false);
      await refresh();
    } catch (err) {
      setError(err.friendlyMessage || 'Failed to add borrower');
    } finally {
      setSubmitting(false);
    }
  };

  const handleUpdate = async (values) => {
    setSubmitting(true);
    setError('');
    try {
      await updateBorrower(editing.borrower_id, values);
      setSuccess('Borrower updated');
      setEditing(null);
      await refresh();
    } catch (err) {
      setError(err.friendlyMessage || 'Failed to update borrower');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (b) => {
    if (!confirm(`Delete borrower "${b.borrower_name}"?`)) return;
    setError('');
    try {
      await deleteBorrower(b.borrower_id);
      setSuccess('Borrower deleted');
      await refresh();
    } catch (err) {
      setError(err.friendlyMessage || 'Failed to delete borrower');
    }
  };

  return (
    <div>
      <Alert message={error} onDismiss={() => setError('')} />
      <Alert kind="success" message={success} onDismiss={() => setSuccess('')} />

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ margin: 0 }}>Borrowers ({items.length})</h2>
          {!showAdd && !editing && (
            <button className="btn-primary" onClick={() => setShowAdd(true)}>
              + Add Borrower
            </button>
          )}
        </div>
      </div>

      {showAdd && (
        <div className="card">
          <h2>Add Borrower</h2>
          <BorrowerForm
            onSubmit={handleCreate}
            onCancel={() => setShowAdd(false)}
            submitting={submitting}
          />
        </div>
      )}

      {editing && (
        <div className="card">
          <h2>Edit Borrower #{editing.borrower_id}</h2>
          <BorrowerForm
            initial={editing}
            onSubmit={handleUpdate}
            onCancel={() => setEditing(null)}
            submitting={submitting}
          />
        </div>
      )}

      <div className="card">
        {items.length === 0 ? (
          <p className="muted">No borrowers yet.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map((b) => (
                <tr key={b.borrower_id}>
                  <td>{b.borrower_id}</td>
                  <td>{b.borrower_name}</td>
                  <td>{b.email}</td>
                  <td>{b.phone}</td>
                  <td>
                    <div className="row-actions">
                      <button className="btn-secondary" onClick={() => setEditing(b)}>
                        Edit
                      </button>
                      <button className="btn-danger" onClick={() => handleDelete(b)}>
                        Delete
                      </button>
                    </div>
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
