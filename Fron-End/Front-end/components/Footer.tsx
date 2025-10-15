
import React from 'react';
import { NAV_LINKS } from '../constants';
import { BaobabIcon } from './icons/BaobabIcon';
import { FacebookIcon, LinkedinIcon, TwitterIcon } from './icons/SocialIcons';

const Footer: React.FC = () => {
    const handleLinkClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
        e.preventDefault();
        document.querySelector(href)?.scrollIntoView({ behavior: 'smooth' });
    };

  return (
    <footer className="bg-brand-blue-dark text-white pt-12 pb-8">
      <div className="container mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="col-span-1 md:col-span-2">
             <a href="#inicio" onClick={(e) => handleLinkClick(e, '#inicio')} className="flex items-center gap-2 text-white text-2xl font-extrabold mb-4">
              <BaobabIcon className="w-8 h-8 text-brand-gold" />
              <h2>Lacos Microcrédito</h2>
            </a>
            <p className="text-gray-400 max-w-md">
              A impulsionar o crescimento de pequenas empresas e a realizar sonhos em todo Moçambique. Juntos, construímos um futuro mais próspero.
            </p>
          </div>
          
          <div>
            <h3 className="text-xl font-bold mb-4 text-brand-gold">Navegação</h3>
            <ul className="space-y-2">
              {NAV_LINKS.map(link => (
                <li key={link.href}>
                  <a href={link.href} onClick={(e) => handleLinkClick(e, link.href)} className="hover:text-brand-gold transition-colors duration-300 text-gray-300">{link.label}</a>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-xl font-bold mb-4 text-brand-gold">Contacto</h3>
            <ul className="space-y-2 text-gray-300">
              <li>Av. 25 de Setembro, Maputo</li>
              <li>Moçambique</li>
              <li>Email: LacosMicrocredito@gmail.co.mz</li>
              <li>Telefone: +258 87 510 4607</li>
            </ul>
            <div className="flex space-x-4 mt-6">
                <a href="#" className="text-gray-400 hover:text-brand-gold" aria-label="Facebook"><FacebookIcon /></a>
                <a href="#" className="text-gray-400 hover:text-brand-gold" aria-label="Twitter"><TwitterIcon /></a>
                <a href="#" className="text-gray-400 hover:text-brand-gold" aria-label="LinkedIn"><LinkedinIcon /></a>
            </div>
          </div>
        </div>
        
        <div className="mt-12 border-t border-gray-700 pt-6 text-center text-gray-500">
          <p>&copy; {new Date().getFullYear()} Lacos Microcrédito. Todos os direitos reservados.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;