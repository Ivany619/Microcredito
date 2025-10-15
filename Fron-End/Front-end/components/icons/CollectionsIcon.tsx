
import React from 'react';

const CollectionsIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg
    {...props}
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M20.3 18.9c.4.4.4 1 0 1.4l-1.8 1.8c-.4.4-1 .4-1.4 0l-15-15c-.4-.4-.4-1 0-1.4l1.8-1.8c.4-.4 1-.4 1.4 0l15 15z" />
    <path d="M8 16h8" />
    <path d="m12 12 4 4" />
  </svg>
);

export default CollectionsIcon;
