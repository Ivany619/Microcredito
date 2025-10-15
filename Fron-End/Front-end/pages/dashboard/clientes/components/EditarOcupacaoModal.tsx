import React, { useState, useEffect } from 'react';
import { XMarkIcon, BriefcaseIcon } from '@heroicons/react/24/solid';
import { Ocupacao } from '../types';
import { ocupacoesAPI } from '../services/api.service';

interface Props {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
    ocupacao: Ocupacao | null;
    clienteId: number;
}

const EditarOcupacaoModal: React.FC<Props> = ({ isOpen, onClose, onSuccess, ocupacao, clienteId }) => {
    const [loading, setLoading] = useState(false);
    const [erro, setErro] = useState<string | null>(null);
    const [formData, setFormData] = useState({
        codigo: '',
        nome: '',
        descricao: '',
        setor_economico: '',
        categoria_risco: '',
        renda_minima: 0,
        estabilidade_emprego: ''
    });

    useEffect(() => {
        if (ocupacao) {
            setFormData({
                codigo: ocupacao.codigo || '',
                nome: ocupacao.nome || '',
                descricao: ocupacao.descricao || '',
                setor_economico: ocupacao.setor_economico || '',
                categoria_risco: ocupacao.categoria_risco || '',
                renda_minima: ocupacao.renda_minima || 0,
                estabilidade_emprego: ocupacao.estabilidade_emprego || ''
            });
        } else {
            setFormData({
                codigo: '',
                nome: '',
                descricao: '',
                setor_economico: '',
                categoria_risco: '',
                renda_minima: 0,
                estabilidade_emprego: ''
            });
        }
    }, [ocupacao]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setErro(null);

        try {
            if (!formData.nome || !formData.setor_economico || !formData.categoria_risco) {
                throw new Error('Campos obrigatórios não preenchidos');
            }

            if (ocupacao) {
                // Atualizar ocupação existente
                await ocupacoesAPI.atualizar(ocupacao.ocupacao_id, formData);
            } else {
                // Criar nova ocupação
                await ocupacoesAPI.criar({
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
                <div className="bg-gradient-to-r from-green-500 to-green-600 text-white p-6 flex justify-between items-center rounded-t-2xl">
                    <div className="flex items-center gap-3">
                        <BriefcaseIcon className="w-8 h-8" />
                        <h2 className="text-2xl font-bold">{ocupacao ? 'Editar' : 'Adicionar'} Ocupação</h2>
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
                            <label className="block text-sm font-semibold text-gray-700 mb-2">
                                Código Ocupacional
                            </label>
                            <input
                                type="text"
                                value={formData.codigo}
                                onChange={(e) => setFormData({ ...formData, codigo: e.target.value })}
                                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-green-500 focus:ring-2 focus:ring-green-500/20"
                                placeholder="Código ISCO"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">
                                Nome da Ocupação *
                            </label>
                            <input
                                type="text"
                                required
                                value={formData.nome}
                                onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-green-500 focus:ring-2 focus:ring-green-500/20"
                                placeholder="Nome da profissão"
                            />
                        </div>
                        <div className="md:col-span-2">
                            <label className="block text-sm font-semibold text-gray-700 mb-2">
                                Descrição
                            </label>
                            <textarea
                                value={formData.descricao}
                                onChange={(e) => setFormData({ ...formData, descricao: e.target.value })}
                                rows={3}
                                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-green-500 focus:ring-2 focus:ring-green-500/20"
                                placeholder="Descreva as atividades realizadas"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">
                                Setor Econômico *
                            </label>
                            <select
                                required
                                value={formData.setor_economico}
                                onChange={(e) => setFormData({ ...formData, setor_economico: e.target.value })}
                                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-green-500 focus:ring-2 focus:ring-green-500/20"
                            >
                                <option value="">Selecione o setor</option>
                                <option value="AGRICULTURA">Agricultura</option>
                                <option value="INDUSTRIA">Indústria</option>
                                <option value="SERVICOS">Serviços</option>
                                <option value="COMERCIO">Comércio</option>
                                <option value="CONSTRUCAO">Construção</option>
                                <option value="TRANSPORTES">Transportes</option>
                                <option value="FINANCEIRO">Serviços Financeiros</option>
                                <option value="SAUDE">Saúde</option>
                                <option value="EDUCACAO">Educação</option>
                                <option value="INFORMACAO">Informação/Tecnologia</option>
                                <option value="OUTROS">Outros</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">
                                Categoria de Risco *
                            </label>
                            <select
                                required
                                value={formData.categoria_risco}
                                onChange={(e) => setFormData({ ...formData, categoria_risco: e.target.value })}
                                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-green-500 focus:ring-2 focus:ring-green-500/20"
                            >
                                <option value="">Selecione o risco</option>
                                <option value="BAIXO">Baixo</option>
                                <option value="MEDIO">Médio</option>
                                <option value="ALTO">Alto</option>
                                <option value="MUITO_ALTO">Muito Alto</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">
                                Renda Mínima (MT)
                            </label>
                            <input
                                type="number"
                                value={formData.renda_minima || ''}
                                onChange={(e) => setFormData({ ...formData, renda_minima: parseFloat(e.target.value) || 0 })}
                                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-green-500 focus:ring-2 focus:ring-green-500/20"
                                placeholder="Renda mínima mensal"
                                min="0"
                                step="0.01"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">
                                Estabilidade do Emprego
                            </label>
                            <select
                                value={formData.estabilidade_emprego}
                                onChange={(e) => setFormData({ ...formData, estabilidade_emprego: e.target.value })}
                                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-green-500 focus:ring-2 focus:ring-green-500/20"
                            >
                                <option value="">Selecione a estabilidade</option>
                                <option value="TEMPORARIO">Temporário</option>
                                <option value="CONTRATADO">Contratado</option>
                                <option value="ESTAVEL">Estável</option>
                                <option value="AUTONOMO">Autônomo</option>
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
                            className="px-6 py-2 bg-green-500 text-white font-bold rounded-lg hover:bg-green-600 transition-colors disabled:opacity-50"
                        >
                            {loading ? 'Salvando...' : 'Salvar'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default EditarOcupacaoModal;
