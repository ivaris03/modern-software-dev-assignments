export function NoteList({ notes, onDelete }) {
  if (!notes.length) {
    return <p className="empty-state">No notes yet</p>;
  }

  return (
    <ul className="note-list">
      {notes.map((note) => (
        <li key={note.id} className="note-item">
          <span className="note-title">{note.title}</span>
          <span className="note-content">{note.content}</span>
          <button
            type="button"
            className="delete-btn"
            onClick={() => onDelete(note.id)}
          >
            Delete
          </button>
        </li>
      ))}
    </ul>
  );
}