import React, { useState, useEffect } from 'react';
import { XMarkIcon, DocumentIcon } from '@heroicons/react/24/solid';
import { Documento } from '../types';
import { documentosAPI } from '../services/api.service';

interface Props {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
    documento: Documento | null;
    clienteId: number;
}

const EditarDocumentoModal: React.FC<Props> = ({ isOpen, onClose, onSuccess, documento, clienteId }) => {
    const [loading, setLoading] = useState(false);
    const [erro, setErro] = useState<string | null>(null);
    const [formData, setFormData] = useState<{
        tipo_documento: string;
        numero_documento: string;
        data_emissao: string;
        data_validade: string;
        arquivo?: File;
    }>({
        tipo_documento: documento?.tipo_documento || '',
        numero_documento: documento?.numero_documento || '',
        data_emissao: documento?.data_emissao || '',
        data_validade: documento?.data_validade || ''
    });

    useEffect(() => {
        if (documento) {
            setFormData({
                tipo_documento: documento.tipo_documento,
                numero_documento: documento.numero_documento,
                data_emissao: documento.data_emissao,
                data_validade: documento.data_validade || ''
            });
        } else {
            setFormData({
                tipo_documento: '',
                numero_documento: '',
                data_emissao: '',
                data_validade: ''
            });
        }
    }, [documento]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setErro(null);

        try {
            if (documento) {
                // Apenas atualizar informações básicas
                const { arquivo, ...updateData } = formData;
                await documentosAPI.atualizar(documento.documento_id, updateData);
            } else {
                // Criar novo documento
                const form = new FormData();
                form.append('cliente_id', clienteId.toString());
                form.append('tipo_documento', formData.tipo_documento);
                form.append('numero_documento', formData.numero_documento);
                if (formData.arquivo) {
                    form.append('arquivo', formData.arquivo);
                } else {
                    throw new Error('Arquivo do documento é obrigatório');
                }
                await documentosAPI.criar(form);
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
                <div className="bg-gradient-to-r from-orange-500 to-orange-600 text-white p-6 flex justify-between items-center rounded-t-2xl">
                    <div className="flex items-center gap-3">
                        <DocumentIcon className="w-8 h-8" />
                        <h2 className="text-2xl font-bold">{documento ? 'Editar' : 'Adicionar'} Documento</h2>
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
                            <label className="block text-sm font-semibold text-gray-700 mb-2">Tipo de Documento *</label>
                            <input
                                type="text"
                                required
                                value={formData.tipo_documento}
                                onChange={(e) => setFormData({ ...formData, tipo_documento: e.target.value })}
                                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20"
                                placeholder="BI, NUIT, etc."
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">Número do Documento *</label>
                            <input
                                type="text"
                                required
                                value={formData.numero_documento}
                                onChange={(e) => setFormData({ ...formData, numero_documento: e.target.value })}
                                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">Data de Emissão *</label>
                            <input
                                type="date"
                                required
                                value={formData.data_emissao}
                                onChange={(e) => setFormData({ ...formData, data_emissao: e.target.value })}
                                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">Data de Validade</label>
                            <input
                                type="date"
                                value={formData.data_validade}
                                onChange={(e) => setFormData({ ...formData, data_validade: e.target.value })}
                                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20"
                            />
                        </div>
                        {!documento && (
                            <div className="md:col-span-2">
                                <label className="block text-sm font-semibold text-gray-700 mb-2">Arquivo do Documento *</label>
                                <input
                                    type="file"
                                    required
                                    accept=".pdf,.jpg,.jpeg,.png"
                                    onChange={(e) => {
                                        const file = e.target.files?.[0];
                                        if (file) {
                                            setFormData({ ...formData, arquivo: file });
                                        }
                                    }}
                                    className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20"
                                />
                                {formData.arquivo && (
                                    <p className="text-sm text-gray-600 mt-1">Arquivo selecionado: {formData.arquivo.name}</p>
                                )}
                            </div>
                        )}
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
                            className="px-6 py-2 bg-orange-500 text-white font-bold rounded-lg hover:bg-orange-600 transition-colors disabled:opacity-50"
                        >
                            {loading ? 'Salvando...' : 'Salvar'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default EditarDocumentoModal;
