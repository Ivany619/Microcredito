import React, { useState } from 'react';
import { PlusIcon, CurrencyDollarIcon, ShieldCheckIcon, UserGroupIcon } from '@heroicons/react/24/solid';
import EmprestimoForm from './components/EmprestimoForm';
import PenhorForm from './components/PenhorForm';
import TestemunhaForm from './components/TestemunhaForm';

// Mock data for clients
const mockClients = [
    { cliente_id: 1, nome: 'Mariana Santos' },
    { cliente_id: 2, nome: 'João Silva' },
];

const GestaoEmprestimos: React.FC = () => {
    const [selectedClient, setSelectedClient] = useState<number | null>(null);

    return (
        <div className="p-8 bg-gray-50 min-h-screen">
            {/* Header */}
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-4xl font-bold text-brand-blue-dark">Gestão de Empréstimos</h1>
                    <p className="text-lg text-gray-600 mt-1">Crie e gira empréstimos para clientes registrados.</p>
                </div>
            </div>

            {/* Client Selection */}
            <div className="mb-8">
                <label htmlFor="cliente_id" className="block text-base font-semibold text-gray-800 mb-1">Selecione um Cliente</label>
                <select
                    id="cliente_id"
                    className="w-full md:w-1/2 px-4 py-3 bg-white border-2 border-gray-200 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent transition-all"
                    onChange={(e) => setSelectedClient(e.target.value ? parseInt(e.target.value) : null)}
                    value={selectedClient || ''}
                >
                    <option value="">Selecione...</option>
                    {mockClients.map(client => (
                        <option key={client.cliente_id} value={client.cliente_id}>{client.nome}</option>
                    ))}
                </select>
            </div>

            {selectedClient ? (
                <div className="space-y-8 animate-fade-in">
                    <EmprestimoForm />
                    <PenhorForm />
                    <TestemunhaForm />
                    <div className="flex justify-end pt-4">
                        <button className="flex items-center gap-2 bg-brand-gold text-brand-blue-dark font-bold py-3 px-6 rounded-lg shadow-lg hover:bg-yellow-400 transition-all duration-300 transform hover:scale-105">
                            <PlusIcon className="w-6 h-6" />
                            Criar Empréstimo
                        </button>
                    </div>
                </div>
            ) : (
                <div className="text-center py-10 animate-fade-in">
                    <div className="inline-block bg-white p-8 rounded-full shadow-xl transform hover:rotate-6 transition-transform duration-500">
                         <CurrencyDollarIcon className="w-24 h-24 text-brand-gold" />
                    </div>
                    <h2 className="mt-8 text-3xl font-bold text-brand-blue-dark">Selecione um Cliente para Começar</h2>
                    <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
                        Para criar um novo empréstimo, penhor ou adicionar testemunhas, por favor, selecione um cliente da lista acima. O nosso sistema foi desenhado para ser seguro, rápido e eficiente.
                    </p>
                    <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
                        {/* Card for Emprestimos */}
                        <div className="bg-white p-8 rounded-2xl shadow-lg transform hover:scale-105 hover:-translate-y-2 transition-transform duration-300 ease-in-out">
                            <div className="flex justify-center items-center h-20 w-20 rounded-full bg-green-100 mx-auto mb-6">
                                <ShieldCheckIcon className="w-12 h-12 text-green-500" />
                            </div>
                            <h3 className="text-xl font-semibold text-brand-blue-dark mt-4">Empréstimos Seguros</h3>
                            <p className="text-gray-600 mt-2 text-sm">Oferecemos empréstimos com as melhores taxas e condições do mercado, garantindo a sua segurança financeira.</p>
                        </div>
                        {/* Card for Penhor */}
                        <div className="bg-white p-8 rounded-2xl shadow-lg transform hover:scale-105 hover:-translate-y-2 transition-transform duration-300 ease-in-out">
                             <div className="flex justify-center items-center h-20 w-20 rounded-full bg-yellow-100 mx-auto mb-6">
                                <CurrencyDollarIcon className="w-12 h-12 text-brand-gold" />
                             </div>
                            <h3 className="text-xl font-semibold text-brand-blue-dark mt-4">Avaliação Justa de Penhor</h3>
                            <p className="text-gray-600 mt-2 text-sm">Os seus bens são avaliados de forma justa e transparente para que obtenha o melhor valor no seu penhor.</p>
                        </div>
                        {/* Card for Testemunhas */}
                        <div className="bg-white p-8 rounded-2xl shadow-lg transform hover:scale-105 hover:-translate-y-2 transition-transform duration-300 ease-in-out">
                            <div className="flex justify-center items-center h-20 w-20 rounded-full bg-blue-100 mx-auto mb-6">
                                <UserGroupIcon className="w-12 h-12 text-blue-500" />
                            </div>
                            <h3 className="text-xl font-semibold text-brand-blue-dark mt-4">Processo com Testemunhas</h3>
                            <p className="text-gray-600 mt-2 text-sm">Adicione testemunhas ao processo para maior segurança e conformidade, tornando tudo mais credível.</p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default GestaoEmprestimos;
