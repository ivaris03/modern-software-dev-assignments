async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function loadNotes(q) {
  const list = document.getElementById('notes');
  list.innerHTML = '';
  const url = q ? `/notes/search/?q=${encodeURIComponent(q)}` : '/notes/';
  const notes = await fetchJSON(url);
  for (const n of notes) {
    const li = document.createElement('li');
    li.textContent = `${n.title}: ${n.content}`;
    list.appendChild(li);
  }
}

async function loadActions() {
  const list = document.getElementById('actions');
  list.innerHTML = '';
  const items = await fetchJSON('/action-items/');
  for (const a of items) {
    const li = document.createElement('li');

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.id = `action-${a.id}`;
    checkbox.checked = a.completed;
    checkbox.onchange = async () => {
      if (checkbox.checked) {
        await fetchJSON(`/action-items/${a.id}/complete`, { method: 'PUT' });
      }
      loadActions();
    };

    const label = document.createElement('label');
    label.htmlFor = `action-${a.id}`;
    label.textContent = a.description;
    if (a.completed) {
      label.style.textDecoration = 'line-through';
      label.style.color = '#888';
    }

    li.appendChild(checkbox);
    li.appendChild(label);
    list.appendChild(li);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('note-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('note-title').value;
    const content = document.getElementById('note-content').value;
    await fetchJSON('/notes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content }),
    });
    e.target.reset();
    loadNotes();
  });

  document.getElementById('action-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const description = document.getElementById('action-desc').value;
    await fetchJSON('/action-items/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description }),
    });
    e.target.reset();
    loadActions();
  });

  document.getElementById('note-search-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const q = document.getElementById('note-search').value;
    loadNotes(q);
  });

  loadNotes();
  loadActions();
});
