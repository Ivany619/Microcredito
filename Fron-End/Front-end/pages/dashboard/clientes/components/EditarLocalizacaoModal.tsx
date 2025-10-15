import React, { useState, useEffect } from 'react';
import { XMarkIcon, MapPinIcon } from '@heroicons/react/24/solid';
import { Localizacao } from '../types';
import { localizacoesAPI } from '../services/api.service';

interface Props {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
    localizacao: Localizacao | null;
    clienteId: number;
}

const EditarLocalizacaoModal: React.FC<Props> = ({ isOpen, onClose, onSuccess, localizacao, clienteId }) => {
    const [loading, setLoading] = useState(false);
    const [erro, setErro] = useState<string | null>(null);
    const [formData, setFormData] = useState<Partial<Localizacao>>({
        provincia: '',
        cidade: '',
        distrito: '',
        bairro: '',
        quarteirao: '',
        numero_da_casa: ''
    });

    useEffect(() => {
        if (localizacao) {
            setFormData(localizacao);
        } else {
            setFormData({
                cliente_id: clienteId,
                provincia: '',
                cidade: '',
                distrito: '',
                bairro: '',
                quarteirao: '',
                numero_da_casa: ''
            });
        }
    }, [localizacao, clienteId]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setErro(null);

        try {
            if (localizacao) {
                await localizacoesAPI.atualizar(localizacao.localizacao_id, formData);
            } else {
                await localizacoesAPI.criar({ ...formData, cliente_id: clienteId });
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
                <div className="bg-gradient-to-r from-red-500 to-red-600 text-white p-6 flex justify-between items-center rounded-t-2xl">
                    <div className="flex items-center gap-3">
                        <MapPinIcon className="w-8 h-8" />
                        <h2 className="text-2xl font-bold">{localizacao ? 'Editar' : 'Adicionar'} Localização</h2>
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
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">Província *</label>
                            <input
                                type="text"
                                required
                                value={formData.provincia}
                                onChange={(e) => setFormData({ ...formData, provincia: e.target.value })}
                                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-red-500 focus:ring-2 focus:ring-red-500/20"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">Cidade *</label>
                            <input
                                type="text"
                                required
                                value={formData.cidade}
                                onChange={(e) => setFormData({ ...formData, cidade: e.target.value })}
                                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-red-500 focus:ring-2 focus:ring-red-500/20"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">Distrito *</label>
                            <input
                                type="text"
                                required
                                value={formData.distrito}
                                onChange={(e) => setFormData({ ...formData, distrito: e.target.value })}
                                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-red-500 focus:ring-2 focus:ring-red-500/20"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">Bairro *</label>
                            <input
                                type="text"
                                required
                                value={formData.bairro}
                                onChange={(e) => setFormData({ ...formData, bairro: e.target.value })}
                                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-red-500 focus:ring-2 focus:ring-red-500/20"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">Quarteirão *</label>
                            <input
                                type="text"
                                required
                                value={formData.quarteirao}
                                onChange={(e) => setFormData({ ...formData, quarteirao: e.target.value })}
                                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-red-500 focus:ring-2 focus:ring-red-500/20"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">Número da Casa *</label>
                            <input
                                type="text"
                                required
                                value={formData.numero_da_casa}
                                onChange={(e) => setFormData({ ...formData, numero_da_casa: e.target.value })}
                                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-red-500 focus:ring-2 focus:ring-red-500/20"
                            />
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
                            className="px-6 py-2 bg-red-500 text-white font-bold rounded-lg hover:bg-red-600 transition-colors disabled:opacity-50"
                        >
                            {loading ? 'Salvando...' : 'Salvar'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default EditarLocalizacaoModal;
