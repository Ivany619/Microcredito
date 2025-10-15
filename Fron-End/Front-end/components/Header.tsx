import React, { useState, useEffect, useRef } from 'react';
import { NAV_LINKS } from '../constants';
import { BaobabIcon } from './icons/BaobabIcon';

const Header: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [activeLink, setActiveLink] = useState(NAV_LINKS[0].href);
  const observer = useRef<IntersectionObserver | null>(null);

  useEffect(() => {
    const options = {
      root: null,
      rootMargin: '0px',
      threshold: 0.4, // 40% of the section should be visible
    };

    observer.current = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          setActiveLink(`#${entry.target.id}`);
        }
      });
    }, options);

    const sections = document.querySelectorAll('section[id]');
    sections.forEach(section => {
      if(section.id) observer.current?.observe(section)
    });

    return () => {
      sections.forEach(section => {
        if(section.id) observer.current?.unobserve(section)
      });
    };
  }, []);

  const handleLinkClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    e.preventDefault();
    document.querySelector(href)?.scrollIntoView({ behavior: 'smooth' });
    setIsMenuOpen(false);
    setActiveLink(href);
  };

  return (
    <header className="bg-brand-blue-dark shadow-lg sticky top-0 z-50">
      <div className="container mx-auto px-6 py-4 flex justify-between items-center">
        <a href="#inicio" onClick={(e) => handleLinkClick(e, '#inicio')} className="flex items-center gap-2 text-white text-2xl font-extrabold">
          <BaobabIcon className="w-8 h-8 text-brand-gold" />
          <h1>Lacos Microcrédito</h1>
        </a>

        <nav className="hidden md:flex items-center space-x-8">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              onClick={(e) => handleLinkClick(e, link.href)}
              className={`${activeLink === link.href ? 'text-brand-gold' : 'text-white hover:text-brand-gold'} transition-colors duration-300 font-semibold text-lg`}
              aria-current={activeLink === link.href ? 'page' : undefined}
            >
              {link.label}
            </a>
          ))}
        </nav>

        <div className="md:hidden">
          <button onClick={() => setIsMenuOpen(!isMenuOpen)} className="text-white focus:outline-none" aria-label="Abrir menu">
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d={isMenuOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16m-7 6h7"}></path>
            </svg>
          </button>
        </div>
      </div>
      
      {isMenuOpen && (
        <div className="md:hidden bg-brand-blue-dark animate-fade-in">
          <nav className="flex flex-col items-center space-y-4 px-6 pt-2 pb-6">
            {NAV_LINKS.map((link) => (
              <a
                key={link.href}
                href={link.href}
                onClick={(e) => handleLinkClick(e, link.href)}
                className={`${activeLink === link.href ? 'text-brand-gold' : 'text-white hover:text-brand-gold'} transition-colors duration-300 font-semibold text-lg`}
              >
                {link.label}
              </a>
            ))}
          </nav>
        </div>
      )}
    </header>
  );
};

export default Header;
