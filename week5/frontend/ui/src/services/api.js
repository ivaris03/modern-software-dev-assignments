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
  search: (params = {}) => {
    const searchParams = new URLSearchParams();
    if (params.q) searchParams.set('q', params.q);
    if (params.tag_id) searchParams.set('tag_id', params.tag_id);
    if (params.page) searchParams.set('page', params.page);
    if (params.page_size) searchParams.set('page_size', params.page_size);
    if (params.sort) searchParams.set('sort', params.sort);
    const query = searchParams.toString();
    return fetchJSON(`/notes/search/${query ? `?${query}` : ''}`);
  },
  update: (id, data) => fetchJSON(`/notes/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id) => fetchJSON(`/notes/${id}`, { method: 'DELETE' }),
  attachTag: (noteId, tagName) => fetchJSON(`/notes/${noteId}/tags`, {
    method: 'POST',
    body: JSON.stringify({ name: tagName }),
  }),
  detachTag: (noteId, tagId) => fetchJSON(`/notes/${noteId}/tags/${tagId}`, { method: 'DELETE' }),
};

export const tagsApi = {
  list: () => fetchJSON('/tags/'),
  create: (data) => fetchJSON('/tags/', { method: 'POST', body: JSON.stringify(data) }),
  delete: (id) => fetchJSON(`/tags/${id}`, { method: 'DELETE' }),
};

export const actionItemsApi = {
  list: (params = {}) => {
    const searchParams = new URLSearchParams();
    if (params.completed !== undefined && params.completed !== null) {
      searchParams.set('completed', String(params.completed));
    }
    if (params.page !== undefined && params.page !== null) {
      searchParams.set('page', String(params.page));
    }
    if (params.page_size !== undefined && params.page_size !== null) {
      searchParams.set('page_size', String(params.page_size));
    }
    const query = searchParams.toString();
    return fetchJSON(`/action-items/${query ? `?${query}` : ''}`);
  },
  create: (data) => fetchJSON('/action-items/', { method: 'POST', body: JSON.stringify(data) }),
  complete: (id) => fetchJSON(`/action-items/${id}/complete`, { method: 'PUT' }),
  bulkComplete: (ids) => fetchJSON('/action-items/bulk-complete', {
    method: 'POST',
    body: JSON.stringify({ ids }),
  }),
};