import React from 'react';
import { Badge } from './Badge';

interface StatusPillProps {
  status: string;
}

export const StatusPill: React.FC<StatusPillProps> = ({ status }) => {
  const normalized = (status || '').toUpperCase();

  switch (normalized) {
    case 'FULLY_RECONCILED':
    case 'MATCHED':
    case 'RESOLVED':
    case 'SETTLED':
    case 'VALID':
    case 'EXACT_MATCH':
      return <Badge variant="emerald">{normalized}</Badge>;

    case 'PARTIAL_MATCH':
    case 'PARTIAL_PAYMENT':
    case 'UNDER_REVIEW':
    case 'DELAYED':
    case 'MEDIUM':
      return <Badge variant="amber">{normalized}</Badge>;

    case 'AMBIGUOUS':
    case 'DISCREPANCY':
    case 'TAX_MISMATCH':
    case 'REJECTED':
    case 'CRITICAL':
    case 'HIGH':
      return <Badge variant="rose">{normalized}</Badge>;

    case 'OPEN':
    case 'PENDING':
    case 'ESCALATED':
      return <Badge variant="blue">{normalized}</Badge>;

    case 'AI_INVESTIGATED':
      return <Badge variant="purple">{normalized}</Badge>;

    default:
      return <Badge variant="slate">{normalized || 'UNKNOWN'}</Badge>;
  }
};
