import { useEffect, useState } from 'react';

const empty = { borrower_name: '', email: '', phone: '' };

export default function BorrowerForm({ initial, onSubmit, onCancel, submitting }) {
  const [values, setValues] = useState(initial || empty);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    setValues(initial || empty);
    setErrors({});
  }, [initial]);

  const handleChange = (e) =>
    setValues((v) => ({ ...v, [e.target.name]: e.target.value }));

  const validate = () => {
    const e = {};
    if (!values.borrower_name.trim()) e.borrower_name = 'Name is required';
    if (!values.email.trim()) e.email = 'Email is required';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email))
      e.email = 'Email format looks invalid';
    const cleanedPhone = values.phone.replace(/[\s+-]/g, '');
    if (!cleanedPhone) e.phone = 'Phone is required';
    else if (!/^\d{7,15}$/.test(cleanedPhone))
      e.phone = 'Phone must be 7–15 digits';
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
          <label>Borrower Name</label>
          <input
            name="borrower_name"
            value={values.borrower_name}
            onChange={handleChange}
          />
          {errors.borrower_name && <span className="muted">{errors.borrower_name}</span>}
        </div>
        <div className="form-group">
          <label>Email</label>
          <input name="email" value={values.email} onChange={handleChange} />
          {errors.email && <span className="muted">{errors.email}</span>}
        </div>
        <div className="form-group">
          <label>Phone</label>
          <input
            name="phone"
            value={values.phone}
            onChange={handleChange}
            placeholder="+91 9876543210"
          />
          {errors.phone && <span className="muted">{errors.phone}</span>}
        </div>
      </div>
      <div className="form-actions">
        <button type="submit" className="btn-primary" disabled={submitting}>
          {submitting ? 'Saving…' : initial ? 'Update Borrower' : 'Add Borrower'}
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
