import api from '../api.js';

export const searchBooks = (params) =>
  api.get('/search', { params }).then((r) => r.data);
