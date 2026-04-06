export function ActionItemList({ items, onComplete, onBulkComplete, selectedIds, onToggleSelect }) {
  const completedItems = items.filter(i => i.completed);
  const openItems = items.filter(i => !i.completed);

  const handleBulkComplete = () => {
    onBulkComplete(selectedIds);
  };

  const isAllSelected = openItems.length > 0 && openItems.every(i => selectedIds.includes(i.id));
  const isSomeSelected = openItems.some(i => selectedIds.includes(i.id));

  const toggleAll = () => {
    if (isAllSelected) {
      openItems.forEach(i => onToggleSelect(i.id));
    } else {
      openItems.forEach(i => {
        if (!selectedIds.includes(i.id)) onToggleSelect(i.id);
      });
    }
  };

  const renderItem = (item) => (
    <li key={item.id} className={`action-item ${item.completed ? 'completed' : ''}`}>
      {!item.completed && (
        <input
          type="checkbox"
          checked={selectedIds.includes(item.id)}
          onChange={() => onToggleSelect(item.id)}
        />
      )}
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
  );

  return (
    <div>
      <div className="bulk-actions">
        <label>
          <input type="checkbox" checked={isAllSelected} ref={el => { if (el) el.indeterminate = isSomeSelected && !isAllSelected; }} onChange={toggleAll} />
          Select all open
        </label>
        {selectedIds.length > 0 && (
          <button type="button" className="bulk-complete-btn" onClick={handleBulkComplete}>
            Complete selected ({selectedIds.length})
          </button>
        )}
      </div>
      {items.length === 0 ? (
        <p className="empty-state">No action items yet</p>
      ) : (
        <>
          {openItems.length > 0 && (
            <>
              <h3>Open ({openItems.length})</h3>
              <ul className="action-item-list">
                {openItems.map(renderItem)}
              </ul>
            </>
          )}
          {completedItems.length > 0 && (
            <>
              <h3>Completed ({completedItems.length})</h3>
              <ul className="action-item-list">
                {completedItems.map(renderItem)}
              </ul>
            </>
          )}
        </>
      )}
    </div>
  );
}