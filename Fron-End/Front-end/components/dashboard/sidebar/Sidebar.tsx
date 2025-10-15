
import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  UsersIcon,
  CurrencyDollarIcon,
  BellIcon,
  ChartBarIcon,
  CreditCardIcon,
  ExclamationTriangleIcon,
  DocumentChartBarIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline';

const Sidebar: React.FC = () => {
    const navigate = useNavigate();

    const navLinkClasses = ({ isActive }: { isActive: boolean }) =>
      `flex items-center px-4 py-3 text-lg font-semibold rounded-lg transition-all duration-300 ease-in-out transform hover:scale-105 ${
        isActive
          ? 'bg-brand-gold text-brand-blue-dark shadow-md'
          : 'text-brand-gray hover:bg-brand-blue-light hover:text-brand-blue-dark hover:shadow-sm'
      }`;

    const handleLogout = () => {
        localStorage.removeItem('authToken');
        sessionStorage.removeItem('isAdmin');
        navigate('/');
    };

    return (
        <aside className="w-64 h-screen bg-gradient-to-b from-brand-blue-light to-brand-blue text-white p-6 flex flex-col shadow-2xl border-r border-brand-blue-light/20">
            {/* Logo Section - remains at the top */}
            <div className="flex-shrink-0">
                <div className="mb-10">
                     <h1 className="text-3xl font-bold text-brand-gold text-center">Laços</h1>
                     <h2 className="text-md font-light text-white text-center">Microcrédito</h2>
                 </div>
            </div>

            {/* Navigation Section - becomes scrollable */}
            <nav className="flex-grow space-y-4 overflow-y-auto pr-2">
                <NavLink to="/admin/dashboard/analise-credito" className={navLinkClasses}>
                     <ChartBarIcon className="w-6 h-6 mr-3" />
                     Análise de Crédito
                 </NavLink>
                <NavLink to="/admin/dashboard/clientes" className={navLinkClasses}>
                    <UsersIcon className="w-6 h-6 mr-3" />
                    Gestão de Clientes
                </NavLink>
                <NavLink to="/admin/dashboard/emprestimos" className={navLinkClasses}>
                    <CurrencyDollarIcon className="w-6 h-6 mr-3" />
                    Gestão de Empréstimos
                </NavLink>
                <NavLink to="/admin/dashboard/pagamentos" className={navLinkClasses}>
                    <CreditCardIcon className="w-6 h-6 mr-3" />
                    Gestão de Pagamentos
                </NavLink>
                <NavLink to="/admin/dashboard/cobrancas" className={navLinkClasses}>
                    <ExclamationTriangleIcon className="w-6 h-6 mr-3" />
                    Cobranças
                </NavLink>
                <NavLink to="/admin/dashboard/relatorios" className={navLinkClasses}>
                    <DocumentChartBarIcon className="w-6 h-6 mr-3" />
                    Relatórios
                </NavLink>
                <NavLink to="/admin/dashboard/notificacoes" className={navLinkClasses}>
                    <BellIcon className="w-6 h-6 mr-3" />
                    Notificações
                </NavLink>
                <NavLink to="/admin/dashboard/configuracoes" className={navLinkClasses}>
                    <Cog6ToothIcon className="w-6 h-6 mr-3" />
                    Configurações
                </NavLink>
            </nav>

            {/* Logout Button - pushed to the bottom */}
            <div className="mt-auto pt-6 flex-shrink-0">
                <button
                    onClick={handleLogout}
                    className="w-full bg-brand-gold hover:bg-yellow-400 text-brand-blue-dark font-bold py-3 px-4 rounded-lg transition-all duration-300 ease-in-out transform hover:scale-105 shadow-md"
                >
                    Terminar Sessão
                </button>
            </div>
        </aside>
    );
};

export default Sidebar;
