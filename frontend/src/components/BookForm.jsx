import { useEffect, useState } from 'react';
import { CATEGORIES } from '../services/books.js';

const empty = { title: '', author: '', category: 'Fiction', isbn: '' };

export default function BookForm({ initial, onSubmit, onCancel, submitting }) {
  const [values, setValues] = useState(initial || empty);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    setValues(initial || empty);
    setErrors({});
  }, [initial]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setValues((v) => ({ ...v, [name]: value }));
  };

  const validate = () => {
    const e = {};
    if (!values.title.trim()) e.title = 'Title is required';
    if (!values.author.trim()) e.author = 'Author is required';
    if (!values.category) e.category = 'Category is required';
    const cleanedIsbn = values.isbn.replace(/[-\s]/g, '');
    if (!cleanedIsbn) e.isbn = 'ISBN is required';
    else if (!/^\d+$/.test(cleanedIsbn))
      e.isbn = 'ISBN may contain only digits, dashes, or spaces';
    else if (![10, 13].includes(cleanedIsbn.length))
      e.isbn = 'ISBN must be 10 or 13 digits';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validate()) return;
    onSubmit(values);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-row">
        <div className="form-group">
          <label>Title</label>
          <input name="title" value={values.title} onChange={handleChange} />
          {errors.title && <span className="muted">{errors.title}</span>}
        </div>
        <div className="form-group">
          <label>Author</label>
          <input name="author" value={values.author} onChange={handleChange} />
          {errors.author && <span className="muted">{errors.author}</span>}
        </div>
        <div className="form-group">
          <label>Category</label>
          <select name="category" value={values.category} onChange={handleChange}>
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label>ISBN</label>
          <input
            name="isbn"
            value={values.isbn}
            onChange={handleChange}
            placeholder="978-0-13-235088-4"
          />
          {errors.isbn && <span className="muted">{errors.isbn}</span>}
        </div>
      </div>
      <div className="form-actions">
        <button type="submit" className="btn-primary" disabled={submitting}>
          {submitting ? 'Saving…' : initial ? 'Update Book' : 'Add Book'}
        </button>
        {onCancel && (
          <button type="button" className="btn-secondary" onClick={onCancel}>
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
