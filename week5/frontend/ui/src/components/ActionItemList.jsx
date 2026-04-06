export function ActionItemList({ items, onComplete }) {
  if (!items.length) {
    return <p className="empty-state">No action items yet</p>;
  }

  return (
    <ul className="action-item-list">
      {items.map((item) => (
        <li key={item.id} className={`action-item ${item.completed ? 'completed' : ''}`}>
          <span className="action-description">{item.description}</span>
          <span className="action-status">[{item.completed ? 'done' : 'open'}]</span>
          {!item.completed && (
            <button
              type="button"
              className="complete-btn"
              onClick={() => onComplete(item.id)}
            >
              Complete
            </button>
          )}
        </li>
      ))}
    </ul>
  );
}