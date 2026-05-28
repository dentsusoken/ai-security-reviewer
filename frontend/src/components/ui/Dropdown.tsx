import { useEffect, useRef, useState } from 'react';
import { ChevronDown } from 'lucide-react';

interface DropdownOption {
  value: string;
  label: string;
}

interface DropdownProps {
  label: string;
  icon?: React.ReactNode;
  options: DropdownOption[];
  value: string;
  onChange: (value: string) => void;
}

export function Dropdown({ label, icon, options, value, onChange }: DropdownProps) {
  const [open, setOpen] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClick = (event: MouseEvent) => {
      if (!wrapperRef.current) return;
      if (wrapperRef.current.contains(event.target as Node)) return;
      setOpen(false);
    };

    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const selected = options.find((option) => option.value === value) ?? options[0];

  return (
    <div className="relative" ref={wrapperRef}>
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className="px-3 py-1.5 rounded-lg border transition hover:opacity-80 inline-flex items-center gap-1.5"
        style={{ borderColor: 'var(--border)' }}
      >
        {icon}
        <span>{selected?.label ?? label}</span>
        <ChevronDown className="w-3 h-3" />
      </button>

      {open ? (
        <div
          className="absolute top-full left-0 mt-1 z-20 glass-strong rounded-xl py-2 min-w-[180px] shadow-lg"
          style={{ border: '1px solid var(--border-strong)' }}
        >
          {options.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => {
                onChange(option.value);
                setOpen(false);
              }}
              className="block px-4 py-2 text-sm cursor-pointer transition hover-row text-left w-full"
            >
              {option.label}
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}
