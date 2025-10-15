import React from 'react';

const TestemunhaForm: React.FC = () => {
    return (
        <div className="space-y-8 animate-fade-in">
            <h3 className="text-2xl font-bold text-brand-blue-dark border-b-2 border-brand-gold pb-2">Informações da Testemunha</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">

                {/* Nome da Testemunha */}
                <div>
                    <label htmlFor="nome" className="block text-base font-semibold text-gray-800 mb-1">Nome</label>
                    <input type="text" id="nome" placeholder="Ex: João Silva" className="w-full px-4 py-3 bg-gray-50 border-2 border-gray-200 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent transition-all"/>
                </div>

                {/* Telefone */}
                <div>
                    <label htmlFor="telefone" className="block text-base font-semibold text-gray-800 mb-1">Telefone</label>
                    <input type="text" id="telefone" placeholder="Ex: 841234567" className="w-full px-4 py-3 bg-gray-50 border-2 border-gray-200 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent transition-all"/>
                </div>

                {/* Tipo de Relação */}
                <div className="md:col-span-2">
                    <label htmlFor="tipo_relacao" className="block text-base font-semibold text-gray-800 mb-1">Tipo de Relação</label>
                    <select id="tipo_relacao" className="w-full px-4 py-3 bg-gray-50 border-2 border-gray-200 rounded-lg shadow-sm appearance-none focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent transition-all">
                        <option value="Parente">Parente</option>
                        <option value="Amigo">Amigo</option>
                        <option value="Colega">Colega</option>
                        <option value="Outro">Outro</option>
                    </select>
                </div>
            </div>
        </div>
    );
};

export default TestemunhaForm;