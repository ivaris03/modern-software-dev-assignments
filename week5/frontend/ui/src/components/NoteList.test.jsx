import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import { NoteList } from './NoteList';

beforeEach(() => {
  cleanup();
});

describe('NoteList', () => {
  it('renders empty state when no notes', () => {
    render(<NoteList notes={[]} onDelete={vi.fn()} />);

    expect(screen.getByText('No notes yet')).toBeInTheDocument();
  });

  it('renders list of notes', () => {
    const notes = [
      { id: 1, title: 'Note 1', content: 'Content 1' },
      { id: 2, title: 'Note 2', content: 'Content 2' },
    ];
    render(<NoteList notes={notes} onDelete={vi.fn()} />);

    expect(screen.getByText('Note 1')).toBeInTheDocument();
    expect(screen.getByText('Note 2')).toBeInTheDocument();
    expect(screen.getByText('Content 1')).toBeInTheDocument();
    expect(screen.getByText('Content 2')).toBeInTheDocument();
  });

  it('renders delete button for each note', () => {
    const notes = [{ id: 1, title: 'Test Note', content: 'Test Content' }];
    render(<NoteList notes={notes} onDelete={vi.fn()} />);

    const deleteButtons = screen.getAllByRole('button', { name: 'Delete' });
    expect(deleteButtons.length).toBe(1);
  });

  it('calls onDelete with note id when delete button is clicked', () => {
    const onDelete = vi.fn();
    const notes = [{ id: 42, title: 'Test Note', content: 'Test Content' }];
    render(<NoteList notes={notes} onDelete={onDelete} />);

    fireEvent.click(screen.getByRole('button', { name: 'Delete' }));
    expect(onDelete).toHaveBeenCalledWith(42);
  });
});
