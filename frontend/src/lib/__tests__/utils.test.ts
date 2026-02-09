import { describe, it, expect } from 'vitest';
import {
  cn,
  truncate,
  pluralize,
  formatNumber,
  isValidEmail,
  isValidHandle,
  getInitials,
  getEvidenceTypeIcon,
  skipToCursor,
  cursorToSkip,
} from '../utils';

describe('cn', () => {
  it('merges class names', () => {
    expect(cn('foo', 'bar')).toBe('foo bar');
  });

  it('handles conditional classes', () => {
    expect(cn('base', false && 'hidden', 'visible')).toBe('base visible');
  });
});

describe('truncate', () => {
  it('returns text unchanged if shorter than max', () => {
    expect(truncate('hello', 10)).toBe('hello');
  });

  it('truncates and adds ellipsis', () => {
    expect(truncate('hello world this is long', 10)).toBe('hello w...');
  });
});

describe('pluralize', () => {
  it('returns singular for count 1', () => {
    expect(pluralize(1, 'receipt')).toBe('receipt');
  });

  it('returns default plural for count > 1', () => {
    expect(pluralize(5, 'receipt')).toBe('receipts');
  });

  it('uses custom plural', () => {
    expect(pluralize(0, 'person', 'people')).toBe('people');
  });
});

describe('formatNumber', () => {
  it('formats small numbers as-is', () => {
    expect(formatNumber(42)).toBe('42');
  });

  it('formats thousands with K', () => {
    expect(formatNumber(1500)).toBe('1.5K');
  });

  it('formats millions with M', () => {
    expect(formatNumber(2000000)).toBe('2M');
  });

  it('removes trailing .0', () => {
    expect(formatNumber(1000)).toBe('1K');
  });
});

describe('isValidEmail', () => {
  it('accepts valid email', () => {
    expect(isValidEmail('test@example.com')).toBe(true);
  });

  it('rejects invalid email', () => {
    expect(isValidEmail('not-an-email')).toBe(false);
  });
});

describe('isValidHandle', () => {
  it('accepts valid handle', () => {
    expect(isValidHandle('user_123')).toBe(true);
  });

  it('rejects too short handle', () => {
    expect(isValidHandle('ab')).toBe(false);
  });

  it('rejects handle with special chars', () => {
    expect(isValidHandle('user@name')).toBe(false);
  });
});

describe('getInitials', () => {
  it('gets two-letter initials', () => {
    expect(getInitials('John Doe')).toBe('JD');
  });

  it('handles single name', () => {
    expect(getInitials('Alice')).toBe('A');
  });
});

describe('getEvidenceTypeIcon', () => {
  it('returns correct icon for known types', () => {
    expect(getEvidenceTypeIcon('image')).toBe('image');
    expect(getEvidenceTypeIcon('link')).toBe('link');
    expect(getEvidenceTypeIcon('video')).toBe('video');
    expect(getEvidenceTypeIcon('quote')).toBe('quote');
  });

  it('returns file for unknown type', () => {
    expect(getEvidenceTypeIcon('unknown')).toBe('file');
  });
});

describe('cursor helpers', () => {
  it('skipToCursor converts number to string', () => {
    expect(skipToCursor(20)).toBe('20');
  });

  it('cursorToSkip parses string to number', () => {
    expect(cursorToSkip('40')).toBe(40);
  });

  it('cursorToSkip returns 0 for null/undefined', () => {
    expect(cursorToSkip(null)).toBe(0);
    expect(cursorToSkip(undefined)).toBe(0);
  });

  it('cursorToSkip returns 0 for invalid string', () => {
    expect(cursorToSkip('not-a-number')).toBe(0);
  });
});
