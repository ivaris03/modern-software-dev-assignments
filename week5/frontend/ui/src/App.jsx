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

  const loadNotes = async () => {
    try {
      const data = await notesApi.list();
      setNotes(data);
      setError(null);
    } catch (err) {
      setError('Failed to load notes');
      console.error(err);
    }
  };

  const loadActionItems = async () => {
    try {
      const data = await actionItemsApi.list();
      setActionItems(data);
      setError(null);
    } catch (err) {
      setError('Failed to load action items');
      console.error(err);
    }
  };

  useEffect(() => {
    loadNotes();
    loadActionItems();
  }, []);

  const handleAddNote = async ({ title, content }) => {
    try {
      await notesApi.create({ title, content });
      await loadNotes();
    } catch (err) {
      setError('Failed to create note');
      console.error(err);
    }
  };

  const handleDeleteNote = async (id) => {
    try {
      await notesApi.delete(id);
      await loadNotes();
    } catch (err) {
      setError('Failed to delete note');
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
      await loadActionItems();
    } catch (err) {
      setError('Failed to complete action item');
      console.error(err);
    }
  };

  return (
    <main>
      <h1>Modern Software Dev Starter</h1>

      {error && <div className="error">{error}</div>}

      <section>
        <h2>Notes</h2>
        <NoteForm onSubmit={handleAddNote} />
        <NoteList notes={notes} onDelete={handleDeleteNote} />
      </section>

      <section>
        <h2>Action Items</h2>
        <ActionItemForm onSubmit={handleAddActionItem} />
        <ActionItemList items={actionItems} onComplete={handleCompleteActionItem} />
      </section>
    </main>
  );
}

export default App;