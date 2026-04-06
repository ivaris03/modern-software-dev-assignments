import { useState } from 'react';

export function NoteList({ notes, onDelete, onUpdate, onAttachTag, onDetachTag }) {
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [editContent, setEditContent] = useState('');
  const [newTagNoteId, setNewTagNoteId] = useState(null);
  const [newTagName, setNewTagName] = useState('');

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

  const handleStartAddTag = (noteId) => {
    setNewTagNoteId(noteId);
    setNewTagName('');
  };

  const handleCancelAddTag = () => {
    setNewTagNoteId(null);
    setNewTagName('');
  };

  const handleSubmitTag = (noteId) => {
    if (newTagName.trim()) {
      onAttachTag(noteId, newTagName.trim());
    }
    setNewTagNoteId(null);
    setNewTagName('');
  };

  const handleDetachTag = (noteId, tagId) => {
    onDetachTag(noteId, tagId);
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
              {note.tags && note.tags.length > 0 && (
                <div className="note-tags">
                  {note.tags.map((tag) => (
                    <span key={tag.id} className="tag-chip">
                      {tag.name}
                      <button
                        type="button"
                        className="tag-remove-btn"
                        onClick={() => handleDetachTag(note.id, tag.id)}
                      >
                        x
                      </button>
                    </span>
                  ))}
                </div>
              )}
              {newTagNoteId === note.id ? (
                <div className="tag-input-form">
                  <input
                    type="text"
                    className="tag-name-input"
                    value={newTagName}
                    onChange={(e) => setNewTagName(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSubmitTag(note.id)}
                    placeholder="Tag name"
                    autoFocus
                  />
                  <button type="button" onClick={() => handleSubmitTag(note.id)}>Add</button>
                  <button type="button" onClick={handleCancelAddTag}>Cancel</button>
                </div>
              ) : (
                <button
                  type="button"
                  className="add-tag-btn"
                  onClick={() => handleStartAddTag(note.id)}
                >
                  + Tag
                </button>
              )}
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
