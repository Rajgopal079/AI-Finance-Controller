import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'warning' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  icon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'secondary',
  size = 'md',
  isLoading = false,
  icon,
  className = '',
  disabled,
  ...props
}) => {
  const variantStyles = {
    primary: 'bg-blue-600 hover:bg-blue-500 text-white border-blue-500/80 active:bg-blue-700 shadow-sm shadow-blue-900/20',
    secondary: 'bg-slate-800/90 hover:bg-slate-700/90 text-slate-200 border-slate-700 active:bg-slate-800',
    danger: 'bg-rose-600/90 hover:bg-rose-600 text-white border-rose-500 active:bg-rose-700',
    warning: 'bg-amber-600/90 hover:bg-amber-600 text-white border-amber-500 active:bg-amber-700',
    ghost: 'bg-transparent hover:bg-slate-800/60 text-slate-400 hover:text-slate-200 border-transparent'
  };

  const sizeStyles = {
    sm: 'px-2.5 py-1 text-xs font-medium',
    md: 'px-3.5 py-1.5 text-xs font-medium',
    lg: 'px-4 py-2 text-sm font-medium'
  };

  return (
    <button
      disabled={disabled || isLoading}
      className={`inline-flex items-center justify-center gap-1.5 rounded border font-sans transition-all duration-150 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
      {...props}
    >
      {isLoading ? (
        <span className="w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin shrink-0" />
      ) : (
        icon
      )}
      {children}
    </button>
  );
};
