import { useState, useEffect } from 'react';
import { NoteForm } from './components/NoteForm';
import { NoteList } from './components/NoteList';
import { ActionItemForm } from './components/ActionItemForm';
import { ActionItemList } from './components/ActionItemList';
import { notesApi, actionItemsApi } from './services/api';
import './App.css';

function App() {
  const [notes, setNotes] = useState([]);
  const [actionItems, setActionItems] = useState([]);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [total, setTotal] = useState(0);
  const [sort, setSort] = useState('created_desc');
  const [actionFilter, setActionFilter] = useState(null);
  const [selectedActionIds, setSelectedActionIds] = useState([]);

  const loadNotes = async (search = '', pageNum = 1, sortOrder = 'created_desc') => {
    try {
      const data = await notesApi.search({ q: search, page: pageNum, page_size: pageSize, sort: sortOrder });
      setNotes(data.items);
      setTotal(data.total);
      setPage(data.page);
      setError(null);
    } catch (err) {
      setError('Failed to load notes');
      console.error(err);
    }
  };

  const loadActionItems = async (filter = null) => {
    try {
      const data = await actionItemsApi.list(filter !== null ? { completed: filter } : {});
      setActionItems(data);
      setError(null);
    } catch (err) {
      setError('Failed to load action items');
      console.error(err);
    }
  };

  useEffect(() => {
    loadNotes();
    loadActionItems(actionFilter);
  }, []);

  const handleSearch = () => {
    setPage(1);
    loadNotes(searchQuery, 1, sort);
  };

  const handleSortChange = (newSort) => {
    setSort(newSort);
    loadNotes(searchQuery, page, newSort);
  };

  const handlePageChange = (newPage) => {
    loadNotes(searchQuery, newPage, sort);
  };

  const handleAddNote = async ({ title, content }) => {
    try {
      await notesApi.create({ title, content });
      loadNotes(searchQuery, page, sort);
    } catch (err) {
      setError('Failed to create note');
      console.error(err);
    }
  };

  const handleDeleteNote = async (id) => {
    // Optimistic delete: store backup before removing
    const backup = notes.find(n => n.id === id);
    if (!backup) return;

    // Immediately remove from UI
    setNotes(prev => prev.filter(n => n.id !== id));

    try {
      await notesApi.delete(id);
    } catch (err) {
      // Rollback on error: restore the note
      setNotes(prev => [backup, ...prev]);
      setError('Failed to delete note');
      console.error(err);
    }
  };

  const handleUpdateNote = async (id, { title, content }) => {
    // Optimistic update: store backup before changing
    const backup = notes.find(n => n.id === id);
    if (!backup) return;

    // Immediately update in UI
    setNotes(prev => prev.map(n =>
      n.id === id ? { ...n, title, content } : n
    ));

    try {
      await notesApi.update(id, { title, content });
    } catch (err) {
      // Rollback on error: restore original
      setNotes(prev => prev.map(n =>
        n.id === id ? backup : n
      ));
      setError('Failed to update note');
      console.error(err);
    }
  };

  const handleAddActionItem = async ({ description }) => {
    try {
      await actionItemsApi.create({ description });
      await loadActionItems();
    } catch (err) {
      setError('Failed to create action item');
      console.error(err);
    }
  };

  const handleCompleteActionItem = async (id) => {
    try {
      await actionItemsApi.complete(id);
      await loadActionItems(actionFilter);
    } catch (err) {
      setError('Failed to complete action item');
      console.error(err);
    }
  };

  const handleBulkCompleteActionItems = async (ids) => {
    try {
      await actionItemsApi.bulkComplete(ids);
      setSelectedActionIds([]);
      await loadActionItems(actionFilter);
    } catch (err) {
      setError('Failed to bulk complete action items');
      console.error(err);
    }
  };

  const handleActionFilterChange = (filter) => {
    setActionFilter(filter);
    setSelectedActionIds([]);
    loadActionItems(filter);
  };

  const handleToggleSelectActionItem = (id) => {
    setSelectedActionIds(prev =>
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <main>
      <h1>Modern Software Dev Starter</h1>

      {error && <div className="error">{error}</div>}

      <section>
        <h2>Notes</h2>
        <div className="search-bar">
          <input
            type="text"
            placeholder="Search notes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button type="button" onClick={handleSearch}>Search</button>
          <select value={sort} onChange={(e) => handleSortChange(e.target.value)}>
            <option value="created_desc">Newest First</option>
            <option value="created_asc">Oldest First</option>
            <option value="title_asc">Title A-Z</option>
            <option value="title_desc">Title Z-A</option>
          </select>
        </div>
        <NoteForm onSubmit={handleAddNote} />
        <div className="result-count">
          {total > 0 ? `Showing ${notes.length} of ${total} notes` : 'No notes found'}
        </div>
        <NoteList notes={notes} onDelete={handleDeleteNote} onUpdate={handleUpdateNote} />
        {totalPages > 1 && (
          <div className="pagination">
            <button
              type="button"
              onClick={() => handlePageChange(page - 1)}
              disabled={page <= 1}
            >
              Previous
            </button>
            <span>Page {page} of {totalPages}</span>
            <button
              type="button"
              onClick={() => handlePageChange(page + 1)}
              disabled={page >= totalPages}
            >
              Next
            </button>
          </div>
        )}
      </section>

      <section>
        <h2>Action Items</h2>
        <div className="filter-toggles">
          <button
            type="button"
            className={actionFilter === null ? 'active' : ''}
            onClick={() => handleActionFilterChange(null)}
          >
            All
          </button>
          <button
            type="button"
            className={actionFilter === false ? 'active' : ''}
            onClick={() => handleActionFilterChange(false)}
          >
            Open
          </button>
          <button
            type="button"
            className={actionFilter === true ? 'active' : ''}
            onClick={() => handleActionFilterChange(true)}
          >
            Completed
          </button>
        </div>
        <ActionItemForm onSubmit={handleAddActionItem} />
        <ActionItemList
          items={actionItems}
          onComplete={handleCompleteActionItem}
          onBulkComplete={handleBulkCompleteActionItems}
          selectedIds={selectedActionIds}
          onToggleSelect={handleToggleSelectActionItem}
        />
      </section>
    </main>
  );
}

export default App;
