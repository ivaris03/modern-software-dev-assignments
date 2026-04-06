import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import { ActionItemForm } from './ActionItemForm';

beforeEach(() => {
  cleanup();
});

describe('ActionItemForm', () => {
  it('renders form with description input', () => {
    render(<ActionItemForm onSubmit={vi.fn()} />);

    const descInput = screen.getByPlaceholderText('Description');
    const button = screen.getByRole('button', { name: 'Add' });

    expect(descInput).toBeInTheDocument();
    expect(button).toBeInTheDocument();
  });

  it('calls onSubmit with form data when submitted', () => {
    const onSubmit = vi.fn();
    render(<ActionItemForm onSubmit={onSubmit} />);

    fireEvent.change(screen.getByPlaceholderText('Description'), {
      target: { value: 'Test Action Item' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Add' }));

    expect(onSubmit).toHaveBeenCalledWith({
      description: 'Test Action Item',
    });
  });

  it('resets form after submission', () => {
    const onSubmit = vi.fn();
    render(<ActionItemForm onSubmit={onSubmit} />);

    const descInput = screen.getByPlaceholderText('Description');
    fireEvent.change(descInput, { target: { value: 'Test Action Item' } });
    fireEvent.click(screen.getByRole('button', { name: 'Add' }));

    expect(descInput.value).toBe('');
  });
});