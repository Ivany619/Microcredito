
import React from 'react';

export const GrowthIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg 
    xmlns="http://www.w3.org/2000/svg" 
    width="24" 
    height="24" 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    strokeWidth="2" 
    strokeLinecap="round" 
    strokeLinejoin="round"
    {...props}
  >
    <path d="M2 22h20"></path>
    <path d="M12 2c-2.8 0-5 2.2-5 5s2.2 5 5 5 5-2.2 5-5-2.2-5-5-5z"></path>
    <path d="M12 12v10"></path>
    <path d="M12 12c-4 0-8 2-8 5"></path>
    <path d="M12 12c4 0 8 2 8 5"></path>
  </svg>
);
