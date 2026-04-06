import { useState } from 'react';

export function NoteList({ notes, onDelete, onUpdate }) {
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [editContent, setEditContent] = useState('');

  if (!notes.length) {
    return <p className="empty-state">No notes yet</p>;
  }

  const handleStartEdit = (note) => {
    setEditingId(note.id);
    setEditTitle(note.title);
    setEditContent(note.content);
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditTitle('');
    setEditContent('');
  };

  const handleSaveEdit = (note) => {
    onUpdate(note.id, { title: editTitle, content: editContent });
    setEditingId(null);
    setEditTitle('');
    setEditContent('');
  };

  const handleKeyDown = (e, note) => {
    if (e.key === 'Escape') {
      handleCancelEdit();
    }
  };

  return (
    <ul className="note-list">
      {notes.map((note) => (
        <li key={note.id} className="note-item">
          {editingId === note.id ? (
            <>
              <input
                type="text"
                className="edit-title-input"
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                onKeyDown={(e) => handleKeyDown(e, note)}
                autoFocus
              />
              <textarea
                className="edit-content-input"
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                onKeyDown={(e) => handleKeyDown(e, note)}
              />
              <button
                type="button"
                className="save-btn"
                onClick={() => handleSaveEdit(note)}
              >
                Save
              </button>
              <button
                type="button"
                className="cancel-btn"
                onClick={handleCancelEdit}
              >
                Cancel
              </button>
            </>
          ) : (
            <>
              <span className="note-title">{note.title}</span>
              <span className="note-content">{note.content}</span>
              <button
                type="button"
                className="edit-btn"
                onClick={() => handleStartEdit(note)}
              >
                Edit
              </button>
              <button
                type="button"
                className="delete-btn"
                onClick={() => onDelete(note.id)}
              >
                Delete
              </button>
            </>
          )}
        </li>
      ))}
    </ul>
  );
}
