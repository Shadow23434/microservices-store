import React from 'react';

export default function Logo({ className = "w-8 h-8" }: { className?: string }) {
  return (
    <svg viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
      <path d="M 40 70 Q 70 50 95 75 L 95 150 Q 70 130 40 150 Z" fill="#D96B27"/>
      <path d="M 160 70 Q 130 50 105 75 L 105 150 Q 130 130 160 150 Z" fill="#D96B27"/>
      <path d="M 105 75 L 140 35 L 140 105 L 105 145 Z" fill="#D96B27"/>
    </svg>
  );
}
