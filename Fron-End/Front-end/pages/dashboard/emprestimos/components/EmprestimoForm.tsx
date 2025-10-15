import React from 'react';

const EmprestimoForm: React.FC = () => {
    return (
        <div className="space-y-8 animate-fade-in">
            <h3 className="text-2xl font-bold text-brand-blue-dark border-b-2 border-brand-gold pb-2">Detalhes do Empréstimo</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">

                {/* Valor do Empréstimo */}
                <div>
                    <label htmlFor="valor" className="block text-base font-semibold text-gray-800 mb-1">Valor do Empréstimo</label>
                    <input type="number" id="valor" placeholder="Ex: 5000" className="w-full px-4 py-3 bg-gray-50 border-2 border-gray-200 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent transition-all"/>
                </div>

                {/* Status */}
                <div>
                    <label htmlFor="status" className="block text-base font-semibold text-gray-800 mb-1">Status</label>
                    <select id="status" className="w-full px-4 py-3 bg-gray-50 border-2 border-gray-200 rounded-lg shadow-sm appearance-none focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent transition-all">
                        <option value="Ativo">Ativo</option>
                        <option value="Pago">Pago</option>
                        <option value="Inadimplente">Inadimplente</option>
                    </select>
                </div>

                {/* Data do Empréstimo */}
                <div>
                    <label htmlFor="data_emprestimo" className="block text-base font-semibold text-gray-800 mb-1">Data do Empréstimo</label>
                    <input type="date" id="data_emprestimo" className="w-full px-4 py-3 bg-gray-50 border-2 border-gray-200 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent transition-all"/>
                </div>

                {/* Data de Vencimento */}
                <div>
                    <label htmlFor="data_vencimento" className="block text-base font-semibold text-gray-800 mb-1">Data de Vencimento</label>
                    <input type="date" id="data_vencimento" className="w-full px-4 py-3 bg-gray-50 border-2 border-gray-200 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent transition-all"/>
                </div>
            </div>
        </div>
    );
};

export default EmprestimoForm;