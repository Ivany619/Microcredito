import React from 'react';

const PenhorForm: React.FC = () => {
    return (
        <div className="space-y-8 animate-fade-in">
            <h3 className="text-2xl font-bold text-brand-blue-dark border-b-2 border-brand-gold pb-2">Detalhes do Penhor</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">

                {/* Descrição do Item */}
                <div className="md:col-span-2">
                    <label htmlFor="descricao_item" className="block text-base font-semibold text-gray-800 mb-1">Descrição do Item</label>
                    <textarea id="descricao_item" placeholder="Ex: Joia de ouro" rows={3} className="w-full px-4 py-3 bg-gray-50 border-2 border-gray-200 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent transition-all"></textarea>
                </div>

                {/* Valor Estimado */}
                <div>
                    <label htmlFor="valor_estimado" className="block text-base font-semibold text-gray-800 mb-1">Valor Estimado</label>
                    <input type="number" id="valor_estimado" placeholder="Ex: 2500" className="w-full px-4 py-3 bg-gray-50 border-2 border-gray-200 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent transition-all"/>
                </div>

                {/* Data da Penhora */}
                <div>
                    <label htmlFor="data_penhora" className="block text-base font-semibold text-gray-800 mb-1">Data da Penhora</label>
                    <input type="date" id="data_penhora" className="w-full px-4 py-3 bg-gray-50 border-2 border-gray-200 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent transition-all"/>
                </div>

            </div>
        </div>
    );
};

export default PenhorForm;