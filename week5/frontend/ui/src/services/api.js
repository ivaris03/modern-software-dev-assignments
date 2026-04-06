const API_BASE = '';

async function fetchJSON(url, options = {}) {
  const res = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export const notesApi = {
  list: () => fetchJSON('/notes/'),
  create: (data) => fetchJSON('/notes/', { method: 'POST', body: JSON.stringify(data) }),
  get: (id) => fetchJSON(`/notes/${id}`),
  search: (q) => fetchJSON(`/notes/search/${q ? `?q=${encodeURIComponent(q)}` : ''}`),
  update: (id, data) => fetchJSON(`/notes/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id) => fetchJSON(`/notes/${id}`, { method: 'DELETE' }),
};

export const actionItemsApi = {
  list: () => fetchJSON('/action-items/'),
  create: (data) => fetchJSON('/action-items/', { method: 'POST', body: JSON.stringify(data) }),
  complete: (id) => fetchJSON(`/action-items/${id}/complete`, { method: 'PUT' }),
};