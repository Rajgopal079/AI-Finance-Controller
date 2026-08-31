import React from 'react';

interface PageHeaderProps {
  title: string;
  subtitle: string;
  action?: React.ReactNode;
}

export const PageHeader: React.FC<PageHeaderProps> = ({ title, subtitle, action }) => {
  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-slate-800 gap-4 mb-6">
      <div>
        <h1 className="text-xl font-bold text-slate-100 tracking-tight">{title}</h1>
        <p className="text-xs text-slate-400 mt-1">{subtitle}</p>
      </div>
      {action && <div>{action}</div>}
    </div>
  );
};
