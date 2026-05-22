import { useEffect, useState } from 'react';
import Alert from '../components/Alert.jsx';
import AvailabilityBadge from '../components/AvailabilityBadge.jsx';
import BookForm from '../components/BookForm.jsx';
import {
  createBook,
  deleteBook,
  listBooks,
  updateBook,
} from '../services/books.js';

export default function Books() {
  const [books, setBooks] = useState([]);
  const [editing, setEditing] = useState(null); // book or null
  const [showAdd, setShowAdd] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const refresh = async () => {
    try {
      const data = await listBooks();
      setBooks(data);
    } catch (err) {
      setError(err.friendlyMessage || 'Failed to load books');
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const handleCreate = async (values) => {
    setSubmitting(true);
    setError('');
    try {
      await createBook(values);
      setSuccess('Book added successfully');
      setShowAdd(false);
      await refresh();
    } catch (err) {
      setError(err.friendlyMessage || 'Failed to add book');
    } finally {
      setSubmitting(false);
    }
  };

  const handleUpdate = async (values) => {
    setSubmitting(true);
    setError('');
    try {
      await updateBook(editing.book_id, values);
      setSuccess('Book updated');
      setEditing(null);
      await refresh();
    } catch (err) {
      setError(err.friendlyMessage || 'Failed to update book');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (book) => {
    if (!confirm(`Delete "${book.title}"?`)) return;
    setError('');
    try {
      await deleteBook(book.book_id);
      setSuccess('Book deleted');
      await refresh();
    } catch (err) {
      setError(err.friendlyMessage || 'Failed to delete book');
    }
  };

  return (
    <div>
      <Alert message={error} onDismiss={() => setError('')} />
      <Alert kind="success" message={success} onDismiss={() => setSuccess('')} />

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ margin: 0 }}>Books ({books.length})</h2>
          {!showAdd && !editing && (
            <button className="btn-primary" onClick={() => setShowAdd(true)}>
              + Add Book
            </button>
          )}
        </div>
      </div>

      {showAdd && (
        <div className="card">
          <h2>Add New Book</h2>
          <BookForm
            onSubmit={handleCreate}
            onCancel={() => setShowAdd(false)}
            submitting={submitting}
          />
        </div>
      )}

      {editing && (
        <div className="card">
          <h2>Edit Book #{editing.book_id}</h2>
          <BookForm
            initial={editing}
            onSubmit={handleUpdate}
            onCancel={() => setEditing(null)}
            submitting={submitting}
          />
        </div>
      )}

      <div className="card">
        {books.length === 0 ? (
          <p className="muted">No books yet. Click "Add Book" to create one.</p>
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
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {books.map((b) => (
                <tr key={b.book_id}>
                  <td>{b.book_id}</td>
                  <td>{b.title}</td>
                  <td>{b.author}</td>
                  <td>{b.category}</td>
                  <td>{b.isbn}</td>
                  <td><AvailabilityBadge status={b.availability_status} /></td>
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
