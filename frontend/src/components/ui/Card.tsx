import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
  onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({ children, className = '', style, onClick }) => {
  return (
    <div
      onClick={onClick}
      style={style}
      className={`bg-[#111827] border border-slate-800 rounded-lg p-5 shadow-sm transition-all duration-150 ${onClick ? 'cursor-pointer hover:border-slate-700 hover:bg-[#161F32]' : ''} ${className}`}
    >
      {children}
    </div>
  );
};
