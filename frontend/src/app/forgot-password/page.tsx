'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useMutation } from '@tanstack/react-query';
import { apiClient, getErrorMessage } from '@/lib/api-client';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: async () => {
      await apiClient.post('/auth/forgot-password', { email });
    },
    onSuccess: () => {
      setSubmitted(true);
    },
    onError: (err) => {
      setError(getErrorMessage(err));
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    mutation.mutate();
  };

  if (submitted) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">Check your email</CardTitle>
            <CardDescription>
              If an account exists with that email, we sent a password reset link.
            </CardDescription>
          </CardHeader>
          <CardFooter className="justify-center">
            <Link href="/login" className="text-primary hover:underline text-sm">
              Back to sign in
            </Link>
          </CardFooter>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Reset your password</CardTitle>
          <CardDescription>
            Enter your email and we'll send you a reset link.
          </CardDescription>
        </CardHeader>

        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            {error && (
              <div className="p-3 bg-destructive/10 text-destructive rounded-md text-sm">
                {error}
              </div>
            )}

            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-2">
                Email
              </label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
              />
            </div>
          </CardContent>

          <CardFooter className="flex flex-col space-y-4">
            <Button
              type="submit"
              className="w-full"
              isLoading={mutation.isPending}
            >
              Send Reset Link
            </Button>

            <Link href="/login" className="text-sm text-muted-foreground hover:underline text-center">
              Back to sign in
            </Link>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
