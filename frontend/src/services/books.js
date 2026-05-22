import api from '../api.js';

export const listBooks = () => api.get('/books').then((r) => r.data);
export const getBook = (id) => api.get(`/books/${id}`).then((r) => r.data);
export const createBook = (payload) => api.post('/books', payload).then((r) => r.data);
export const updateBook = (id, payload) =>
  api.put(`/books/${id}`, payload).then((r) => r.data);
export const deleteBook = (id) => api.delete(`/books/${id}`);
export const bookStats = () => api.get('/books/stats').then((r) => r.data);

export const CATEGORIES = [
  'Fiction',
  'Non-Fiction',
  'Science',
  'History',
  'Technology',
  'Biography',
  'Children',
];
