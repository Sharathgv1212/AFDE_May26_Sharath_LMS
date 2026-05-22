import api from '../api.js';

export const listTransactions = (params = {}) =>
  api.get('/transactions', { params }).then((r) => r.data);
export const recentTransactions = (limit = 5) =>
  api.get('/transactions/recent', { params: { limit } }).then((r) => r.data);
export const transactionStats = () =>
  api.get('/transactions/stats').then((r) => r.data);
export const borrowBook = (book_id, borrower_id) =>
  api.post('/borrow', { book_id, borrower_id }).then((r) => r.data);
export const returnBook = (transaction_id) =>
  api.post('/return', { transaction_id }).then((r) => r.data);
