
import React from 'react';

export const SpeedIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
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
    <path d="M4.5 16.5c-1.5 1.2-1.5 3.3 0 4.5 1.5 1.2 3.8 1.2 5.2 0l3.3-2.6c.2-.2.5-.2.7 0l2.6 2.6c1.2 1.5 3.3 1.5 4.5 0s1.2-3.8 0-5.2l-2.6-3.3c-.2-.2-.2-.5 0-.7l2.6-2.6c1.5-1.2 1.5-3.3 0-4.5s-3.8-1.2-5.2 0l-3.3 2.6c-.2.2-.5.2-.7 0l-2.6-2.6C6.3 2.2 4.2 2.2 3 3.5c-1.2 1.5-1.2 3.8 0 5.2l2.6 3.3c.2.2.2.5 0 .7L3 15.2c-1.2 1.5-1.2 3.8 0 5.2z"></path>
  </svg>
);
