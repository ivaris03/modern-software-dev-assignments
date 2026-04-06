import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import { NoteForm } from './NoteForm';

beforeEach(() => {
  cleanup();
});

describe('NoteForm', () => {
  it('renders form with title and content inputs', () => {
    render(<NoteForm onSubmit={vi.fn()} />);

    const titleInput = screen.getByPlaceholderText('Title');
    const contentInput = screen.getByPlaceholderText('Content');
    const button = screen.getByRole('button', { name: 'Add' });

    expect(titleInput).toBeTruthy();
    expect(contentInput).toBeTruthy();
    expect(button).toBeTruthy();
  });

  it('calls onSubmit with form data when submitted', () => {
    const onSubmit = vi.fn();
    render(<NoteForm onSubmit={onSubmit} />);

    fireEvent.change(screen.getByPlaceholderText('Title'), {
      target: { value: 'Test Title' },
    });
    fireEvent.change(screen.getByPlaceholderText('Content'), {
      target: { value: 'Test Content' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Add' }));

    expect(onSubmit).toHaveBeenCalledWith({
      title: 'Test Title',
      content: 'Test Content',
    });
  });

  it('resets form after submission', () => {
    const onSubmit = vi.fn();
    render(<NoteForm onSubmit={onSubmit} />);

    const titleInput = screen.getByPlaceholderText('Title');
    const contentInput = screen.getByPlaceholderText('Content');

    fireEvent.change(titleInput, { target: { value: 'Test Title' } });
    fireEvent.change(contentInput, { target: { value: 'Test Content' } });
    fireEvent.click(screen.getByRole('button', { name: 'Add' }));

    expect(titleInput.value).toBe('');
    expect(contentInput.value).toBe('');
  });
});