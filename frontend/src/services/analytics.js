import api from '../api.js';

export const summary = () =>
  api.get('/analytics/summary').then((r) => r.data);

export const popularBooks = (limit = 10) =>
  api.get('/analytics/popular-books', { params: { limit } }).then((r) => r.data);

export const categoryBorrowing = () =>
  api.get('/analytics/category-borrowing').then((r) => r.data);

export const monthlyTrends = () =>
  api.get('/analytics/monthly-trends').then((r) => r.data);

export const overdue = (status) =>
  api
    .get('/analytics/overdue', { params: status ? { status } : {} })
    .then((r) => r.data);

export const etlRuns = (limit = 5) =>
  api.get('/analytics/runs', { params: { limit } }).then((r) => r.data);

export const refresh = () =>
  api.post('/analytics/refresh').then((r) => r.data);
