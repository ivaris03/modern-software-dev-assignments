import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import App from './App';

// Mock the API module
vi.mock('./services/api', () => ({
  notesApi: {
    list: vi.fn(),
    create: vi.fn(),
    get: vi.fn(),
    search: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    attachTag: vi.fn(),
    detachTag: vi.fn(),
  },
  tagsApi: {
    list: vi.fn(),
    create: vi.fn(),
    delete: vi.fn(),
  },
  actionItemsApi: {
    list: vi.fn(),
    create: vi.fn(),
    complete: vi.fn(),
    bulkComplete: vi.fn(),
  },
}));

import { notesApi, actionItemsApi, tagsApi } from './services/api';

beforeEach(() => {
  cleanup();
  vi.clearAllMocks();
  // Default mock implementations
  notesApi.search.mockResolvedValue({ items: [], total: 0, page: 1, page_size: 10 });
  notesApi.delete.mockResolvedValue(undefined);
  notesApi.update.mockResolvedValue({ id: 1, title: 'Updated', content: 'Updated content' });
  notesApi.attachTag.mockResolvedValue({ id: 1, title: 'Note', content: 'Content', tags: [] });
  notesApi.detachTag.mockResolvedValue(undefined);
  notesApi.create.mockResolvedValue({ id: 1, title: 'Test', content: 'Test content' });
  actionItemsApi.list.mockResolvedValue({ items: [], total: 0, page: 1, page_size: 10 });
  actionItemsApi.create.mockResolvedValue({ id: 1, description: 'Test', completed: false });
  actionItemsApi.complete.mockResolvedValue({ id: 1, description: 'Test', completed: true });
  actionItemsApi.bulkComplete.mockResolvedValue([]);
  tagsApi.list.mockResolvedValue([]);
  tagsApi.create.mockResolvedValue({ id: 1, name: 'test' });
  tagsApi.delete.mockResolvedValue(undefined);
});

describe('App - Search Integration', () => {
  it('renders search bar and triggers search on button click', async () => {
    notesApi.search.mockResolvedValueOnce({
      items: [{ id: 1, title: 'Test Note', content: 'Content', tags: [] }],
      total: 1,
      page: 1,
      page_size: 10,
    });

    render(<App />);

    const searchInput = screen.getByPlaceholderText('Search notes...');
    const searchButton = screen.getByRole('button', { name: 'Search' });

    fireEvent.change(searchInput, { target: { value: 'Test' } });
    fireEvent.click(searchButton);

    expect(notesApi.search).toHaveBeenCalledWith({
      q: 'Test',
      page: 1,
      page_size: 10,
      sort: 'created_desc',
      tag_id: null,
    });
  });

  it('renders search bar and triggers search on Enter key', async () => {
    notesApi.search.mockResolvedValueOnce({
      items: [],
      total: 0,
      page: 1,
      page_size: 10,
    });

    render(<App />);

    const searchInput = screen.getByPlaceholderText('Search notes...');

    fireEvent.change(searchInput, { target: { value: 'Test' } });
    fireEvent.keyDown(searchInput, { key: 'Enter' });

    expect(notesApi.search).toHaveBeenCalledWith(
      expect.objectContaining({ q: 'Test' })
    );
  });

  it('renders search results with note count', async () => {
    notesApi.search.mockResolvedValueOnce({
      items: [{ id: 1, title: 'Note 1', content: 'Content 1', tags: [] }],
      total: 1,
      page: 1,
      page_size: 10,
    });

    render(<App />);

    // Wait for the component to render
    await screen.findByText('Showing 1 of 1 notes');

    expect(screen.getByText('Showing 1 of 1 notes')).toBeInTheDocument();
  });

  it('renders empty state when search has no results', async () => {
    notesApi.search.mockResolvedValueOnce({
      items: [],
      total: 0,
      page: 1,
      page_size: 10,
    });

    render(<App />);

    await screen.findByText('No notes found');

    expect(screen.getByText('No notes found')).toBeInTheDocument();
  });
});

describe('App - Pagination Integration', () => {
  it('renders pagination controls when there are multiple pages', async () => {
    notesApi.search.mockResolvedValueOnce({
      items: [{ id: 1, title: 'Note 1', content: 'Content', tags: [] }],
      total: 15,
      page: 1,
      page_size: 10,
    });

    render(<App />);

    await screen.findByText('Page 1 of 2');

    expect(screen.getByText('Page 1 of 2')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Previous' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Next' })).toBeInTheDocument();
  });

  it('does not render pagination when there is only one page', async () => {
    notesApi.search.mockResolvedValueOnce({
      items: [{ id: 1, title: 'Note 1', content: 'Content', tags: [] }],
      total: 5,
      page: 1,
      page_size: 10,
    });

    render(<App />);

    await screen.findByText('Showing 1 of 5 notes');

    expect(screen.queryByText('Page 1 of 1')).not.toBeInTheDocument();
  });

  it('disables Previous button on first page', async () => {
    notesApi.search.mockResolvedValueOnce({
      items: [{ id: 1, title: 'Note 1', content: 'Content', tags: [] }],
      total: 15,
      page: 1,
      page_size: 10,
    });

    render(<App />);

    await screen.findByText('Page 1 of 2');

    const prevButton = screen.getByRole('button', { name: 'Previous' });
    expect(prevButton).toBeDisabled();
  });

  it('disables Next button on last page', async () => {
    notesApi.search.mockResolvedValueOnce({
      items: [{ id: 1, title: 'Note 1', content: 'Content', tags: [] }],
      total: 15,
      page: 2,
      page_size: 10,
    });

    render(<App />);

    await screen.findByText('Page 2 of 2');

    const nextButton = screen.getByRole('button', { name: 'Next' });
    expect(nextButton).toBeDisabled();
  });

  it('calls API with new page number when Next is clicked', async () => {
    notesApi.search.mockResolvedValueOnce({
      items: [{ id: 1, title: 'Note 1', content: 'Content', tags: [] }],
      total: 15,
      page: 1,
      page_size: 10,
    });

    render(<App />);

    await screen.findByText('Page 1 of 2');

    const nextButton = screen.getByRole('button', { name: 'Next' });
    fireEvent.click(nextButton);

    expect(notesApi.search).toHaveBeenLastCalledWith(
      expect.objectContaining({ page: 2 })
    );
  });

  it('calls API with new page number when Previous is clicked', async () => {
    notesApi.search.mockResolvedValue({
      items: [{ id: 1, title: 'Note 1', content: 'Content', tags: [] }],
      total: 15,
      page: 2,
      page_size: 10,
    });

    render(<App />);

    await screen.findByText('Page 2 of 2');

    const prevButton = screen.getByRole('button', { name: 'Previous' });
    fireEvent.click(prevButton);

    expect(notesApi.search).toHaveBeenLastCalledWith(
      expect.objectContaining({ page: 1 })
    );
  });
});

describe('App - Optimistic Updates', () => {
  it('optimistically removes note from UI before API call completes', async () => {
    const note = { id: 1, title: 'Note to Delete', content: 'Content', tags: [] };
    notesApi.search.mockResolvedValueOnce({
      items: [note],
      total: 1,
      page: 1,
      page_size: 10,
    });
    notesApi.delete.mockResolvedValueOnce(undefined);

    render(<App />);

    await screen.findByText('Note to Delete');

    const deleteButton = screen.getByRole('button', { name: 'Delete' });
    fireEvent.click(deleteButton);

    // Note should be removed from UI immediately (optimistically)
    expect(screen.queryByText('Note to Delete')).not.toBeInTheDocument();
  });

  it('restores note to UI when delete API call fails', async () => {
    const note = { id: 1, title: 'Note to Fail', content: 'Content', tags: [] };
    notesApi.search.mockResolvedValueOnce({
      items: [note],
      total: 1,
      page: 1,
      page_size: 10,
    });
    notesApi.delete.mockRejectedValueOnce(new Error('Delete failed'));

    render(<App />);

    await screen.findByText('Note to Fail');

    const deleteButton = screen.getByRole('button', { name: 'Delete' });
    fireEvent.click(deleteButton);

    // Note should be restored after error
    await screen.findByText('Note to Fail');
    expect(screen.getByText('Note to Fail')).toBeInTheDocument();
    // Error message should be shown
    expect(screen.getByText('Failed to delete note')).toBeInTheDocument();
  });

  it('optimistically updates note in UI before API call completes', async () => {
    const note = { id: 1, title: 'Original Title', content: 'Original Content', tags: [] };
    notesApi.search.mockResolvedValueOnce({
      items: [note],
      total: 1,
      page: 1,
      page_size: 10,
    });
    notesApi.update.mockResolvedValueOnce({
      id: 1,
      title: 'New Title',
      content: 'New Content',
      tags: [],
    });

    render(<App />);

    await screen.findByText('Original Title');

    // Start editing
    const editButton = screen.getByRole('button', { name: 'Edit' });
    fireEvent.click(editButton);

    // Change the title
    const titleInput = screen.getByDisplayValue('Original Title');
    fireEvent.change(titleInput, { target: { value: 'New Title' } });

    // Save
    const saveButton = screen.getByRole('button', { name: 'Save' });
    fireEvent.click(saveButton);

    // Note should show updated title immediately (optimistically)
    expect(screen.queryByText('Original Title')).not.toBeInTheDocument();
  });

  it('restores original note when update API call fails', async () => {
    const note = { id: 1, title: 'Original Title', content: 'Original Content', tags: [] };
    notesApi.search.mockResolvedValueOnce({
      items: [note],
      total: 1,
      page: 1,
      page_size: 10,
    });
    notesApi.update.mockRejectedValueOnce(new Error('Update failed'));

    render(<App />);

    await screen.findByText('Original Title');

    // Start editing
    const editButton = screen.getByRole('button', { name: 'Edit' });
    fireEvent.click(editButton);

    // Change the title
    const titleInput = screen.getByDisplayValue('Original Title');
    fireEvent.change(titleInput, { target: { value: 'New Title' } });

    // Save
    const saveButton = screen.getByRole('button', { name: 'Save' });
    fireEvent.click(saveButton);

    // Original title should be restored after error
    await screen.findByText('Original Title');
    expect(screen.getByText('Original Title')).toBeInTheDocument();
  });
});
