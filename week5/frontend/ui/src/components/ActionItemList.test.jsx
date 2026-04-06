import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import { ActionItemList } from './ActionItemList';

beforeEach(() => {
  cleanup();
});

describe('ActionItemList', () => {
  it('renders empty state when no items', () => {
    render(<ActionItemList items={[]} onComplete={vi.fn()} />);

    expect(screen.getByText('No action items yet')).toBeTruthy();
  });

  it('renders list of action items', () => {
    const items = [
      { id: 1, description: 'Item 1', completed: false },
      { id: 2, description: 'Item 2', completed: true },
    ];
    render(<ActionItemList items={items} onComplete={vi.fn()} />);

    expect(screen.getByText('Item 1')).toBeTruthy();
    expect(screen.getByText('Item 2')).toBeTruthy();
    expect(screen.getByText('[open]')).toBeTruthy();
    expect(screen.getByText('[done]')).toBeTruthy();
  });

  it('shows complete button only for incomplete items', () => {
    const items = [
      { id: 1, description: 'Incomplete Item', completed: false },
      { id: 2, description: 'Completed Item', completed: true },
    ];
    render(<ActionItemList items={items} onComplete={vi.fn()} />);

    const completeButtons = screen.getAllByRole('button', { name: 'Complete' });
    expect(completeButtons.length).toBe(1);
  });

  it('calls onComplete when complete button is clicked', () => {
    const onComplete = vi.fn();
    const items = [{ id: 1, description: 'Test Item', completed: false }];
    render(<ActionItemList items={items} onComplete={onComplete} />);

    fireEvent.click(screen.getByRole('button', { name: 'Complete' }));
    expect(onComplete).toHaveBeenCalledWith(1);
  });
});