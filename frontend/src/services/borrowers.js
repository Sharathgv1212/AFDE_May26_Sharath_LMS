import api from '../api.js';

export const listBorrowers = () => api.get('/borrowers').then((r) => r.data);
export const getBorrower = (id) => api.get(`/borrowers/${id}`).then((r) => r.data);
export const createBorrower = (p) => api.post('/borrowers', p).then((r) => r.data);
export const updateBorrower = (id, p) =>
  api.put(`/borrowers/${id}`, p).then((r) => r.data);
export const deleteBorrower = (id) => api.delete(`/borrowers/${id}`);
