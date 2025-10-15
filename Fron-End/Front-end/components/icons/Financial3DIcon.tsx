import React from 'react';

export const Financial3DIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg
    viewBox="0 0 64 64"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
    role="img"
    {...props}
  >
    <defs>
      <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur in="SourceAlpha" stdDeviation="2" />
        <feOffset dx="2" dy="2" result="offsetblur" />
        <feComponentTransfer>
          <feFuncA type="linear" slope="0.5" />
        </feComponentTransfer>
        <feMerge>
          <feMergeNode />
          <feMergeNode in="SourceGraphic" />
        </feMerge>
      </filter>
    </defs>
    <g filter="url(#shadow)">
      {/* Bottom Coin */}
      <ellipse cx="32" cy="48" rx="26" ry="10" fill="#D97706" />
      <rect x="6" y="38" width="52" height="10" fill="#F59E0B" />
      <ellipse cx="32" cy="38" rx="26" ry="10" fill="#FBBF24" />
      
      {/* Middle Coin */}
      <ellipse cx="32" cy="32" rx="26" ry="10" fill="#D97706" />
      <rect x="6" y="22" width="52" height="10" fill="#F59E0B" />
      <ellipse cx="32" cy="22" rx="26" ry="10" fill="#FBBF24" />
      
      {/* Top Coin */}
      <ellipse cx="32" cy="16" rx="26" ry="10" fill="#D97706" />
      <rect x="6" y="6" width="52" height="10" fill="#F59E0B" />
      <ellipse cx="32" cy="6" rx="26" ry="10" fill="#FBBF24" />

      {/* Symbol on top coin */}
      <text 
        x="32" y="10" 
        fontFamily="sans-serif" 
        fontSize="12" 
        fill="#B45309"
        fontWeight="bold" 
        textAnchor="middle"
        dominantBaseline="middle"
      >
        MT
      </text>
    </g>
  </svg>
);
