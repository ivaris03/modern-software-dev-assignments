import { useState } from 'react';

export function ActionItemForm({ onSubmit }) {
  const [description, setDescription] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ description });
    setDescription('');
  };

  return (
    <form onSubmit={handleSubmit} className="action-item-form">
      <input
        type="text"
        placeholder="Description"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        required
      />
      <button type="submit">Add</button>
    </form>
  );
}