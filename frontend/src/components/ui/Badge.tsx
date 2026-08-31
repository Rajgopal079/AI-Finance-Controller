import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'emerald' | 'amber' | 'rose' | 'blue' | 'purple' | 'slate';
  size?: 'sm' | 'md';
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'slate',
  size = 'sm'
}) => {
  const variantStyles = {
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/25',
    amber: 'bg-amber-500/10 text-amber-400 border-amber-500/25',
    rose: 'bg-rose-500/10 text-rose-400 border-rose-500/25',
    blue: 'bg-blue-500/10 text-blue-400 border-blue-500/25',
    purple: 'bg-purple-500/10 text-purple-300 border-purple-500/25',
    slate: 'bg-slate-800/80 text-slate-300 border-slate-700/80'
  };

  const sizeStyles = {
    sm: 'px-2 py-0.5 text-[10px] font-mono font-semibold tracking-wider',
    md: 'px-2.5 py-1 text-xs font-mono font-semibold tracking-wider'
  };

  return (
    <span className={`inline-flex items-center rounded border uppercase ${variantStyles[variant]} ${sizeStyles[size]}`}>
      {children}
    </span>
  );
};
