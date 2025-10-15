import React, { useState, useEffect } from 'react';
import { XMarkIcon, CheckIcon, UserIcon, MapPinIcon, BriefcaseIcon, DocumentIcon, CurrencyDollarIcon } from '@heroicons/react/24/solid';

import { clientesAPI, localizacoesAPI, ocupacoesAPI, documentosAPI, outrosGanhosAPI } from '../services/api.service';
import { ClienteCompleto, Cliente } from '../types';

interface Props {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
}

const STEPS = [
    { id: 1, title: 'Cliente', icon: UserIcon, description: 'Dados pessoais' },
    { id: 2, title: 'Localização', icon: MapPinIcon, description: 'Morada' },
    { id: 3, title: 'Ocupação', icon: BriefcaseIcon, description: 'Profissão' },
    { id: 4, title: 'Documentos', icon: DocumentIcon, description: 'Identificação' },
    { id: 5, title: 'Renda', icon: CurrencyDollarIcon, description: 'Ganhos' },
];

const AdicionarClienteModal: React.FC<Props> = ({ isOpen, onClose, onSuccess }) => {
    const [currentStep, setCurrentStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [erro, setErro] = useState<string | null>(null);
    const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set());

    const [clienteData, setClienteData] = useState<ClienteCompleto>({
        cliente: {
            nome: '',
            data_nascimento: '',
            telefone: '',
            email: ''
        } as Partial<Cliente>,
        localizacao: {
            provincia: '',
            cidade: '',
            bairro: '',
            distrito: '',
            quarteirao: '',
            numero_da_casa: ''
        },
        ocupacao: {
            codigo: '',
            nome: '',
            descricao: '',
            renda_minima: 0
        },
        documentos: [],
        outros_ganhos: []
    });

    useEffect(() => {
        if (isOpen) {
            resetModal();
        }
    }, [isOpen]);

    const resetModal = () => {
        setCurrentStep(1);
        setCompletedSteps(new Set());
        setErro(null);
        setClienteData({
            cliente: {
                nome: '',
                data_nascimento: '',
                telefone: '',
                email: ''
            } as Partial<Cliente>,
            localizacao: {
                provincia: '',
                cidade: '',
                bairro: '',
                distrito: '',
                quarteirao: '',
                numero_da_casa: ''
            },
            ocupacao: {
                codigo: '',
                nome: '',
                descricao: '',
                renda_minima: 0
            },
            documentos: [],
            outros_ganhos: []
        });
    };

    const handleInputChange = (section: keyof ClienteCompleto, field: string, value: any) => {
        setClienteData(prev => ({
            ...prev,
            [section]: {
                ...prev[section],
                [field]: value
            }
        }));
    };

    const validateCurrentStep = async () => {
        switch (currentStep) {
            case 1:
                const { nome, data_nascimento, sexo, nacionalidade, telefone } = clienteData.cliente;
                if (!nome || !data_nascimento || !sexo || !nacionalidade || !telefone) {
                    setErro('Por favor, preencha todos os campos obrigatórios.');
                    return false;
                }

                // Verificar se telefone já existe
                try {
                    setLoading(true);
                    const existingClients = await clientesAPI.listar();
                    const telefoneExists = existingClients.some(cliente => cliente.telefone === telefone);
                    if (telefoneExists) {
                        setErro('Este número de telefone já está cadastrado.');
                        return false;
                    }
                } catch (error) {
                    console.error('Erro ao verificar telefone:', error);
                    // Não bloquear se houver erro na verificação - permitir continuar
                } finally {
                    setLoading(false);
                }
                break;
            case 2:
                const { provincia, cidade, bairro, distrito, quarteirao, numero_da_casa } = clienteData.localizacao!;
                if (!provincia || !cidade || !bairro || !distrito || !quarteirao || !numero_da_casa) {
                    setErro('Por favor, preencha todos os campos de localização.');
                    return false;
                }
                break;
            case 3:
                const { nome: ocupacaoNome, descricao, setor_economico, categoria_risco } = clienteData.ocupacao!;
                if (!ocupacaoNome || !setor_economico || !categoria_risco) {
                    setErro('Por favor, preencha os campos obrigatórios da ocupação.');
                    return false;
                }
                break;
        }
        setErro(null);
        return true;
    };

    const handleNext = () => {
        if (validateCurrentStep()) {
            setCompletedSteps(prev => new Set([...prev, currentStep]));
            if (currentStep === STEPS.length) {
                handleSave();
            } else {
                setCurrentStep(prev => prev + 1);
            }
        }
    };

    const handleBack = () => {
        if (currentStep > 1) {
            setCurrentStep(prev => prev - 1);
        }
    };

    const handleSave = async () => {
        setLoading(true);
        setErro(null);

        try {
            // Criar cliente básico
            const clienteResponse = await clientesAPI.criar(clienteData.cliente);
            const cliente_id = clienteResponse.cliente_id;

            // Criar localização
            if (clienteData.localizacao) {
                await localizacoesAPI.criar({
                    cliente_id,
                    ...clienteData.localizacao
                });
            }

            // Criar ocupação
            if (clienteData.ocupacao && clienteData.ocupacao.nome) {
                await ocupacoesAPI.criar({
                    cliente_id,
                    ...clienteData.ocupacao
                });
            }

            // Criar documentos (apenas se tem tipo E número E arquivo)
            if (clienteData.documentos && clienteData.documentos.length > 0) {
                for (const documento of clienteData.documentos) {
                    if (documento.tipo_documento && documento.numero_documento && documento.arquivo) {
                        const formData = new FormData();
                        formData.append('cliente_id', cliente_id.toString());
                        formData.append('tipo_documento', documento.tipo_documento);
                        formData.append('numero_documento', documento.numero_documento);
                        formData.append('arquivo', documento.arquivo);

                        await documentosAPI.criar(formData);
                    }
                }
            }

            // Criar outros ganhos
            if (clienteData.outros_ganhos && clienteData.outros_ganhos.length > 0) {
                for (const ganho of clienteData.outros_ganhos) {
                    await outrosGanhosAPI.criar({
                        cliente_id,
                        ...ganho
                    });
                }
            }

            onSuccess();
            onClose();

        } catch (error: any) {
            console.error('Erro ao salvar cliente:', error);
            setErro(error.message || 'Erro ao salvar cliente. Tente novamente.');
        } finally {
            setLoading(false);
        }
    };

    const addDocumento = () => {
        const newDoc = {
            tipo_documento: '',
            numero_documento: '',
            data_emissao: '',
            data_validade: '',
            arquivo: null as File | null
        };
        setClienteData(prev => ({
            ...prev,
            documentos: [...(prev.documentos || []), newDoc]
        }));
    };

    const updateDocumento = (index: number, field: string, value: any) => {
        setClienteData(prev => ({
            ...prev,
            documentos: prev.documentos?.map((doc, i) =>
                i === index ? { ...doc, [field]: value } : doc
            ) || []
        }));
    };

    const removeDocumento = (index: number) => {
        setClienteData(prev => ({
            ...prev,
            documentos: prev.documentos?.filter((_, i) => i !== index) || []
        }));
    };

    const addGanho = () => {
        const newGanho = {
            descricao: '',
            valor: 0,
            frequencia: ''
        };
        setClienteData(prev => ({
            ...prev,
            outros_ganhos: [...(prev.outros_ganhos || []), newGanho]
        }));
    };

    const updateGanho = (index: number, field: string, value: any) => {
        setClienteData(prev => ({
            ...prev,
            outros_ganhos: prev.outros_ganhos?.map((ganho, i) =>
                i === index ? { ...ganho, [field]: value } : ganho
            ) || []
        }));
    };

    const removeGanho = (index: number) => {
        setClienteData(prev => ({
            ...prev,
            outros_ganhos: prev.outros_ganhos?.filter((_, i) => i !== index) || []
        }));
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col">
                {/* Header */}
                <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6 rounded-t-2xl flex justify-between items-center">
                    <h2 className="text-2xl font-bold">Adicionar Novo Cliente</h2>
                    <button onClick={onClose} className="p-1 hover:bg-white/20 rounded-full transition-colors">
                        <XMarkIcon className="w-6 h-6" />
                    </button>
                </div>

                {/* Progress Steps */}
                <div className="px-6 pt-4">
                    <div className="flex items-center justify-between mb-4">
                        {STEPS.map((step, index) => (
                            <React.Fragment key={step.id}>
                                <div className={`flex flex-col items-center text-center ${currentStep >= step.id ? 'text-blue-600' : 'text-gray-400'}`}>
                                    <div className={`w-12 h-12 rounded-full flex items-center justify-center mb-2 transition-colors ${
                                        completedSteps.has(step.id) ? 'bg-green-500 text-white' :
                                        currentStep > step.id ? 'bg-blue-500 text-white' :
                                        currentStep === step.id ? 'bg-blue-600 text-white border-2 border-blue-300' :
                                        'bg-gray-200 text-gray-400'
                                    }`}>
                                        {completedSteps.has(step.id) ? (
                                            <CheckIcon className="w-6 h-6" />
                                        ) : (
                                            <step.icon className="w-6 h-6" />
                                        )}
                                    </div>
                                    <p className="font-medium text-sm">{step.title}</p>
                                    <p className="text-xs">{step.description}</p>
                                </div>
                                {index < STEPS.length - 1 && (
                                    <div className={`flex-1 h-0.5 mx-4 rounded-full ${
                                        completedSteps.has(index + 1) ? 'bg-green-400' :
                                        currentStep > index ? 'bg-blue-400' : 'bg-gray-200'
                                    }`}></div>
                                )}
                            </React.Fragment>
                        ))}
                    </div>
                </div>

                {/* Content */}
                <div className="flex-1 p-6 overflow-y-auto">
                    {erro && (
                        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                            {erro}
                        </div>
                    )}

                    {/* Step 1: Cliente */}
                    {currentStep === 1 && (
                        <div className="space-y-6">
                            <h3 className="text-xl font-semibold text-gray-800">Dados Pessoais</h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Nome Completo *
                                    </label>
                                    <input
                                        type="text"
                                        required
                                        value={clienteData.cliente.nome}
                                        onChange={(e) => handleInputChange('cliente', 'nome', e.target.value)}
                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                        placeholder="Digite o nome completo"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Data de Nascimento *
                                    </label>
                                    <input
                                        type="date"
                                        required
                                        value={clienteData.cliente.data_nascimento}
                                        onChange={(e) => handleInputChange('cliente', 'data_nascimento', e.target.value)}
                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Sexo *
                                    </label>
                                    <select
                                        required
                                        value={clienteData.cliente.sexo}
                                        onChange={(e) => handleInputChange('cliente', 'sexo', e.target.value)}
                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    >
                                        <option value="">Selecione o sexo</option>
                                        <option value="Masculino">Masculino</option>
                                        <option value="Feminino">Feminino</option>
                                        <option value="Outro">Outro</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Nacionalidade *
                                    </label>
                                    <select
                                        required
                                        value={clienteData.cliente.nacionalidade}
                                        onChange={(e) => handleInputChange('cliente', 'nacionalidade', e.target.value)}
                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    >
                                        <option value="">Selecione a nacionalidade</option>
                                        <option value="Moçambicana">Moçambicana</option>
                                        <option value="Estrangeira">Estrangeira</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Telefone *
                                    </label>
                                    <input
                                        type="tel"
                                        required
                                        value={clienteData.cliente.telefone}
                                        onChange={(e) => handleInputChange('cliente', 'telefone', e.target.value)}
                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                        placeholder="+258 XX XXX XXXX"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Email
                                    </label>
                                    <input
                                        type="email"
                                        value={clienteData.cliente.email}
                                        onChange={(e) => handleInputChange('cliente', 'email', e.target.value)}
                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                        placeholder="cliente@example.com"
                                    />
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Step 2: Localização */}
                    {currentStep === 2 && clienteData.localizacao && (
                        <div className="space-y-6">
                            <h3 className="text-xl font-semibold text-gray-800">Informações de Localização</h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Província *
                                    </label>
                                    <select
                                        required
                                        value={clienteData.localizacao.provincia}
                                        onChange={(e) => handleInputChange('localizacao', 'provincia', e.target.value)}
                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    >
                                        <option value="">Selecione a província</option>
                                        <option value="MAPUTO_CIDADE">Maputo Cidade</option>
                                        <option value="MAPUTO_PROVINCIA">Maputo Província</option>
                                        <option value="GAZA">Gaza</option>
                                        <option value="INHAMBANE">Inhambane</option>
                                        <option value="SOFALA">Sofala</option>
                                        <option value="MANICA">Manica</option>
                                        <option value="TETE">Tete</option>
                                        <option value="ZAMBEZIA">Zambézia</option>
                                        <option value="NAMPULA">Nampula</option>
                                        <option value="CABO_DELGADO">Cabo Delgado</option>
                                        <option value="NIASSA">Niassa</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Distrito *
                                    </label>
                                    <input
                                        type="text"
                                        required
                                        value={clienteData.localizacao.distrito}
                                        onChange={(e) => handleInputChange('localizacao', 'distrito', e.target.value)}
                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                        placeholder="Nome do distrito"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Cidade *
                                    </label>
                                    <input
                                        type="text"
                                        required
                                        value={clienteData.localizacao.cidade}
                                        onChange={(e) => handleInputChange('localizacao', 'cidade', e.target.value)}
                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                        placeholder="Nome da cidade"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Bairro *
                                    </label>
                                    <input
                                        type="text"
                                        required
                                        value={clienteData.localizacao.bairro}
                                        onChange={(e) => handleInputChange('localizacao', 'bairro', e.target.value)}
                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                        placeholder="Nome do bairro"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Quarteirão *
                                    </label>
                                    <input
                                        type="text"
                                        required
                                        value={clienteData.localizacao.quarteirao}
                                        onChange={(e) => handleInputChange('localizacao', 'quarteirao', e.target.value)}
                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                        placeholder="Número do quarteirão"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Número da Casa *
                                    </label>
                                    <input
                                        type="text"
                                        required
                                        value={clienteData.localizacao.numero_da_casa}
                                        onChange={(e) => handleInputChange('localizacao', 'numero_da_casa', e.target.value)}
                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                        placeholder="Número da casa"
                                    />
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Step 3: Ocupação */}
                    {currentStep === 3 && clienteData.ocupacao && (
                        <div className="space-y-6">
                            <h3 className="text-xl font-semibold text-gray-800">Informações de Ocupação</h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Código Ocupacional
                                    </label>
                                    <input
                                        type="text"
                                        value={clienteData.ocupacao.codigo}
                                        onChange={(e) => handleInputChange('ocupacao', 'codigo', e.target.value)}
                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                        placeholder="Código ISCO"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Nome da Ocupação *
                                    </label>
                                    <input
                                        type="text"
                                        required
                                        value={clienteData.ocupacao.nome}
                                        onChange={(e) => handleInputChange('ocupacao', 'nome', e.target.value)}
                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                        placeholder="Nome da profissão"
                                    />
                                </div>
                                <div className="md:col-span-2">
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Descrição
                                    </label>
                                    <textarea
                                        value={clienteData.ocupacao.descricao}
                                        onChange={(e) => handleInputChange('ocupacao', 'descricao', e.target.value)}
                                        rows={3}
                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                        placeholder="Descrição das atividades realizadas"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Setor Econômico *
                                    </label>
                                    <select
                                        required
                                        value={clienteData.ocupacao.setor_economico}
                                        onChange={(e) => handleInputChange('ocupacao', 'setor_economico', e.target.value)}
                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    >
                                        <option value="">Selecione o setor</option>
                                        <option value="Primario">Primário</option>
                                        <option value="Secundario">Secundário</option>
                                        <option value="Terciario">Terciário</option>
                                        <option value="Quaternario">Quaternário</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Categoria de Risco *
                                    </label>
                                    <select
                                        required
                                        value={clienteData.ocupacao.categoria_risco}
                                        onChange={(e) => handleInputChange('ocupacao', 'categoria_risco', e.target.value)}
                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    >
                                        <option value="">Selecione o risco</option>
                                        <option value="Muito Baixo">Muito Baixo</option>
                                        <option value="Baixo">Baixo</option>
                                        <option value="Medio">Médio</option>
                                        <option value="Alto">Alto</option>
                                        <option value="Muito Alto">Muito Alto</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Renda Mínima (MT)
                                    </label>
                                    <input
                                        type="number"
                                        value={clienteData.ocupacao.renda_minima || ''}
                                        onChange={(e) => handleInputChange('ocupacao', 'renda_minima', parseFloat(e.target.value))}
                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                        placeholder="Renda mínima mensal"
                                        min="0"
                                        step="0.01"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Estabilidade do Emprego
                                    </label>
                                    <select
                                        value={clienteData.ocupacao.estabilidade_emprego}
                                        onChange={(e) => handleInputChange('ocupacao', 'estabilidade_emprego', e.target.value)}
                                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    >
                                        <option value="">Selecione a estabilidade</option>
                                        <option value="Alta">Alta</option>
                                        <option value="Media">Média</option>
                                        <option value="Baixa">Baixa</option>
                                        <option value="Sazonal">Sazonal</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Step 4: Documentos */}
                    {currentStep === 4 && (
                        <div className="space-y-6">
                            <div className="flex justify-between items-center">
                                <h3 className="text-xl font-semibold text-gray-800">Documentos de Identificação</h3>
                                <button
                                    type="button"
                                    onClick={addDocumento}
                                    className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                                >
                                    + Adicionar Documento
                                </button>
                            </div>

                            {clienteData.documentos?.length === 0 ? (
                                <div className="text-center py-8 text-gray-500">
                                    <DocumentIcon className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                                    <p>Nenhum documento adicionado</p>
                                    <p className="text-sm">Clique em "Adicionar Documento" para incluir</p>
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    {clienteData.documentos?.map((doc, index) => (
                                        <div key={index} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                                            <div className="flex justify-between items-start mb-3">
                                                <span className="font-medium text-gray-800">Documento #{index + 1}</span>
                                                <button
                                                    type="button"
                                                    onClick={() => removeDocumento(index)}
                                                    className="text-red-500 hover:text-red-700"
                                                >
                                                    <XMarkIcon className="w-5 h-5" />
                                                </button>
                                            </div>
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                                <select
                                                    value={doc.tipo_documento}
                                                    onChange={(e) => updateDocumento(index, 'tipo_documento', e.target.value)}
                                                    className="p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                                    required
                                                >
                                                    <option value="">Tipo *</option>
                                                    <option value="BI">BI</option>
                                                    <option value="Passaporte">Passaporte</option>
                                                    <option value="Carta de Conducao">Carta de Condução</option>
                                                    <option value="NUIT">NUIT</option>
                                                    <option value="Contrato Microcredito">Contrato Microcredito</option>
                                                    <option value="Livrete">Livrete</option>
                                                    <option value="DIRE">DIRE</option>
                                                    <option value="Certidao de Nascimento">Certidão de Nascimento</option>
                                                    <option value="Certificado de Habilitacoes">Certificado de Habilitações</option>
                                                    <option value="Comprovativo de Residencia">Comprovativo de Residência</option>
                                                    <option value="Talao de Deposito">Talão de Depósito</option>
                                                    <option value="Outro">Outro</option>
                                                </select>
                                                <input
                                                    type="text"
                                                    placeholder="Número do Documento *"
                                                    value={doc.numero_documento}
                                                    onChange={(e) => updateDocumento(index, 'numero_documento', e.target.value)}
                                                    className="p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                                    required
                                                />
                                                <div className="md:col-span-2">
                                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                                        Arquivo do Documento *
                                                    </label>
                                                    <input
                                                        type="file"
                                                        accept=".pdf,.jpg,.jpeg,.png"
                                                        onChange={(e) => updateDocumento(index, 'arquivo', e.target.files?.[0] || null)}
                                                        className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                                        required
                                                    />
                                                    {doc.arquivo && (
                                                        <p className="text-sm text-blue-600 mt-1">
                                                            📄 {doc.arquivo.name}
                                                        </p>
                                                    )}
                                                </div>
                                                <div className="md:col-span-2">
                                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                                        Data de Emissão
                                                    </label>
                                                    <input
                                                        type="date"
                                                        value={doc.data_emissao}
                                                        onChange={(e) => updateDocumento(index, 'data_emissao', e.target.value)}
                                                        className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                                    />
                                                </div>
                                                <div className="md:col-span-2">
                                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                                        Data de Validade
                                                    </label>
                                                    <input
                                                        type="date"
                                                        value={doc.data_validade}
                                                        onChange={(e) => updateDocumento(index, 'data_validade', e.target.value)}
                                                        className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                                    />
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}

                    {/* Step 5: Outros Ganhos */}
                    {currentStep === 5 && (
                        <div className="space-y-6">
                            <div className="flex justify-between items-center">
                                <h3 className="text-xl font-semibold text-gray-800">Outros Ganhos/Rendas</h3>
                                <button
                                    type="button"
                                    onClick={addGanho}
                                    className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                                >
                                    + Adicionar Ganho
                                </button>
                            </div>

                            {clienteData.outros_ganhos?.length === 0 ? (
                                <div className="text-center py-8 text-gray-500">
                                    <CurrencyDollarIcon className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                                    <p>Nenhum ganho adicional adicionado</p>
                                    <p className="text-sm">Clique em "Adicionar Ganho" para incluir</p>
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    {clienteData.outros_ganhos?.map((ganho, index) => (
                                        <div key={index} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                                            <div className="flex justify-between items-start mb-3">
                                                <span className="font-medium text-gray-800">Ganho #{index + 1}</span>
                                                <button
                                                    type="button"
                                                    onClick={() => removeGanho(index)}
                                                    className="text-red-500 hover:text-red-700"
                                                >
                                                    <XMarkIcon className="w-5 h-5" />
                                                </button>
                                            </div>
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                                <input
                                                    type="text"
                                                    placeholder="Descrição (ex: Aluguel, Vendas, etc)"
                                                    value={ganho.descricao}
                                                    onChange={(e) => updateGanho(index, 'descricao', e.target.value)}
                                                    className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                                />
                                                <input
                                                    type="number"
                                                    placeholder="Valor (MT)"
                                                    value={ganho.valor || ''}
                                                    onChange={(e) => updateGanho(index, 'valor', parseFloat(e.target.value))}
                                                    className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                                    min="0"
                                                    step="0.01"
                                                />
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="border-t border-gray-200 p-6 flex justify-between items-center bg-gray-50 rounded-b-2xl">
                    <button
                        type="button"
                        onClick={handleBack}
                        disabled={currentStep === 1}
                        className="px-6 py-2 text-gray-600 font-medium hover:text-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Anterior
                    </button>

                    <span className="text-sm text-gray-500">
                        Passo {currentStep} de {STEPS.length}
                    </span>

                    <button
                        type="button"
                        onClick={handleNext}
                        disabled={loading}
                        className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        {loading ? 'Salvando...' :
                         currentStep === STEPS.length ? 'Finalizar' : 'Próximo'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default AdicionarClienteModal;
