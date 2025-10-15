import React, { useState, useEffect } from 'react';
import { XMarkIcon, CurrencyDollarIcon } from '@heroicons/react/24/solid';
import { OutroGanho } from '../types';
import { outrosGanhosAPI } from '../services/api.service';

interface Props {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
    ganho: OutroGanho | null;
    clienteId: number;
}

const EditarOutrosGanhosModal: React.FC<Props> = ({ isOpen, onClose, onSuccess, ganho, clienteId }) => {
    const [loading, setLoading] = useState(false);
    const [erro, setErro] = useState<string | null>(null);
    const [formData, setFormData] = useState({
        descricao: '',
        valor: 0,
        frequencia: ''
    });

    useEffect(() => {
        if (ganho) {
            setFormData({
                descricao: ganho.descricao || '',
                valor: ganho.valor || 0,
                frequencia: ganho.frequencia || ''
            });
        } else {
            setFormData({
                descricao: '',
                valor: 0,
                frequencia: ''
            });
        }
    }, [ganho]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setErro(null);

        try {
            if (!formData.descricao || !formData.valor) {
                throw new Error('Campos obrigatórios não preenchidos');
            }

            if (ganho) {
                // Atualizar ganho existente
                await outrosGanhosAPI.atualizar(ganho.ganho_id, formData);
            } else {
                // Criar novo ganho
                await outrosGanhosAPI.criar({
                    cliente_id: clienteId,
                    ...formData
                });
            }
            onSuccess();
            onClose();
        } catch (error: any) {
            setErro(error.message);
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full">
                <div className="bg-gradient-to-r from-purple-500 to-purple-600 text-white p-6 flex justify-between items-center rounded-t-2xl">
                    <div className="flex items-center gap-3">
                        <CurrencyDollarIcon className="w-8 h-8" />
                        <h2 className="text-2xl font-bold">{ganho ? 'Editar' : 'Adicionar'} Outro Ganho</h2>
                    </div>
                    <button onClick={onClose} className="text-white hover:bg-white/20 p-2 rounded-full">
                        <XMarkIcon className="w-6 h-6" />
                    </button>
                </div>

                {erro && (
                    <div className="mx-6 mt-4 p-4 bg-red-50 border-l-4 border-red-500 text-red-700 rounded">
                        {erro}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="p-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="md:col-span-2">
                            <label className="block text-sm font-semibold text-gray-700 mb-2">
                                Descrição *
                            </label>
                            <input
                                type="text"
                                required
                                value={formData.descricao}
                                onChange={(e) => setFormData({ ...formData, descricao: e.target.value })}
                                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
                                placeholder="Ex: Aluguel, Vendas, Rendimentos, etc."
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">
                                Valor em MT *
                            </label>
                            <input
                                type="number"
                                required
                                value={formData.valor || ''}
                                onChange={(e) => setFormData({ ...formData, valor: parseFloat(e.target.value) || 0 })}
                                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
                                placeholder="0.00"
                                min="0"
                                step="0.01"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">
                                Frequência
                            </label>
                            <select
                                value={formData.frequencia}
                                onChange={(e) => setFormData({ ...formData, frequencia: e.target.value })}
                                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
                            >
                                <option value="">Selecione a frequência</option>
                                <option value="DIARIO">Diário</option>
                                <option value="SEMANAL">Semanal</option>
                                <option value="MENSAL">Mensal</option>
                                <option value="TRIMESTRAL">Trimestral</option>
                                <option value="SEMESTRAL">Semestral</option>
                                <option value="ANUAL">Anual</option>
                                <option value="UNICO">Único</option>
                            </select>
                        </div>
                    </div>

                    <div className="flex justify-end gap-4 mt-6">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-6 py-2 text-gray-600 hover:text-gray-800 font-semibold"
                        >
                            Cancelar
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="px-6 py-2 bg-purple-500 text-white font-bold rounded-lg hover:bg-purple-600 transition-colors disabled:opacity-50"
                        >
                            {loading ? 'Salvando...' : 'Salvar'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default EditarOutrosGanhosModal;
