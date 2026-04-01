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
    li.dataset.noteId = n.id;

    const titleSpan = document.createElement('span');
    titleSpan.className = 'note-title';
    titleSpan.textContent = n.title;

    const contentSpan = document.createElement('span');
    contentSpan.className = 'note-content';
    contentSpan.textContent = `: ${n.content}`;

    const editBtn = document.createElement('button');
    editBtn.textContent = 'Edit';
    editBtn.className = 'note-edit-btn';
    editBtn.onclick = () => startEditNote(n.id, titleSpan, contentSpan, editBtn, deleteBtn);

    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = 'Delete';
    deleteBtn.className = 'note-delete-btn';
    deleteBtn.onclick = async () => {
      if (confirm('Delete this note?')) {
        const res = await fetch(`/notes/${n.id}`, { method: 'DELETE' });
        if (!res.ok) throw new Error(await res.text());
        loadNotes();
      }
    };

    li.appendChild(titleSpan);
    li.appendChild(contentSpan);
    li.appendChild(editBtn);
    li.appendChild(deleteBtn);
    list.appendChild(li);
  }
}

let editNoteId = null;

async function startEditNote(noteId, titleSpan, contentSpan, editBtn, deleteBtn) {
  if (editNoteId === noteId) {
    const titleInput = document.getElementById('edit-title');
    const contentInput = document.getElementById('edit-content');
    const title = titleInput.value;
    const content = contentInput.value;
    await fetchJSON(`/notes/${noteId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content }),
    });
    editNoteId = null;
    const q = document.getElementById('note-search').value;
    loadNotes(q || undefined);
  } else {
    editNoteId = noteId;
    titleSpan.innerHTML = `<input id="edit-title" value="${escapeHtml(titleSpan.textContent)}" />`;
    contentSpan.innerHTML = `<input id="edit-content" value="${escapeHtml(contentSpan.textContent.replace(': ', ''))}" />`;
    editBtn.textContent = 'Save';
    deleteBtn.textContent = 'Cancel';
    deleteBtn.onclick = () => {
      editNoteId = null;
      loadNotes();
    };
    editBtn.onclick = () => startEditNote(noteId, titleSpan, contentSpan, editBtn, deleteBtn);
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
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
