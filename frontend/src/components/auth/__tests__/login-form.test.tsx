import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { LoginForm } from '../login-form';

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
  );
}

describe('LoginForm', () => {
  it('renders email and password fields', () => {
    renderWithProviders(<LoginForm />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });

  it('renders sign in button', () => {
    renderWithProviders(<LoginForm />);
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('renders sign up link', () => {
    renderWithProviders(<LoginForm />);
    expect(screen.getByText(/sign up/i)).toBeInTheDocument();
  });

  it('email field has correct type attribute', () => {
    renderWithProviders(<LoginForm />);
    const emailInput = screen.getByLabelText(/email/i);
    expect(emailInput).toHaveAttribute('type', 'email');
  });
});
