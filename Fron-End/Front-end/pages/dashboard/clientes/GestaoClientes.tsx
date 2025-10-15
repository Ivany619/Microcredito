import React, { useState, useEffect } from 'react';
import { PlusIcon, TrashIcon, UserCircleIcon, CheckCircleIcon, MapPinIcon, BriefcaseIcon, DocumentIcon, CurrencyDollarIcon, ChevronDownIcon, BuildingLibraryIcon, ArrowDownTrayIcon } from '@heroicons/react/24/solid';

import { clientesAPI, localizacoesAPI, ocupacoesAPI, documentosAPI, outrosGanhosAPI } from './services/api.service';
import { Cliente, Localizacao, Ocupacao, Documento, OutroGanho } from './types';

import AdicionarClienteModal from './components/AdicionarClienteModal';
import EditarLocalizacaoModal from './components/EditarLocalizacaoModal';
import EditarOcupacaoModal from './components/EditarOcupacaoModal';
import EditarDocumentoModal from './components/EditarDocumentoModal';
import EditarOutrosGanhosModal from './components/EditarOutrosGanhosModal';

const GestaoClientes: React.FC = () => {
    const [clients, setClients] = useState<Cliente[]>([]);
    const [selectedClient, setSelectedClient] = useState<Cliente | null>(null);
    const [activeTab, setActiveTab] = useState('info');
    const [loading, setLoading] = useState(false);
    const [successMessage, setSuccessMessage] = useState<string | null>(null);
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);

    // Dados do cliente selecionado
    const [localizacoes, setLocalizacoes] = useState<Localizacao[]>([]);
    const [ocupacoes, setOcupacoes] = useState<Ocupacao[]>([]);
    const [documentos, setDocumentos] = useState<Documento[]>([]);
    const [outrosGanhos, setOutrosGanhos] = useState<OutroGanho[]>([]);

    // Estados dos modais
    const [showAdicionarModal, setShowAdicionarModal] = useState(false);
    const [showEditarLocalizacao, setShowEditarLocalizacao] = useState(false);
    const [showEditarOcupacao, setShowEditarOcupacao] = useState(false);
    const [showEditarDocumento, setShowEditarDocumento] = useState(false);
    const [showEditarGanhos, setShowEditarGanhos] = useState(false);

    // Carregar clientes na inicialização
    useEffect(() => {
        loadClients();
    }, []);

    // Carregar dados do cliente selecionado
    useEffect(() => {
        if (selectedClient) {
            loadClientData(selectedClient.cliente_id);
        }
    }, [selectedClient]);

    const loadClients = async () => {
        try {
            setLoading(true);
            const data = await clientesAPI.listar();
            setClients(data);
        } catch (err: any) {
            console.error('Erro ao carregar clientes:', err);
        } finally {
            setLoading(false);
        }
    };

    const loadClientData = async (clienteId: number) => {
        try {
            console.log('Carregando dados do cliente:', clienteId);
            const [loc, ocu, doc, gan] = await Promise.all([
                localizacoesAPI.buscarPorCliente(clienteId),
                ocupacoesAPI.buscarPorCliente(clienteId),
                documentosAPI.buscarPorCliente(clienteId),
                outrosGanhosAPI.buscarPorCliente(clienteId)
            ]);
            console.log('Dados recebidos:', { loc, ocu, doc, gan });
            setLocalizacoes(loc);
            setOcupacoes(ocu);
            setDocumentos(doc);
            setOutrosGanhos(gan);
            console.log('Estados atualizados');
        } catch (err: any) {
            console.error('Erro ao carregar dados do cliente:', err);
        }
    };

    const handleClientSuccess = async () => {
        await loadClients();
        setSuccessMessage('Cliente adicionado com sucesso!');
        setTimeout(() => setSuccessMessage(null), 3000);
    };

    const handleDataUpdate = () => {
        if (selectedClient) {
            loadClientData(selectedClient.cliente_id);
            setSuccessMessage('Dados atualizados com sucesso!');
            setTimeout(() => setSuccessMessage(null), 3000);
        }
    };

    const handleDeleteClient = async () => {
        if (!selectedClient || !confirm('Tem certeza que deseja remover este cliente e todos os seus dados?')) return;

        try {
            await clientesAPI.deletar(selectedClient.cliente_id);
            await loadClients();
            setSelectedClient(null);
            setSuccessMessage('Cliente e todos os dados removidos com sucesso!');
            setTimeout(() => setSuccessMessage(null), 3000);
        } catch (err: any) {
            console.error('Erro ao remover cliente:', err);
        }
    };

    return (
        <div className="p-8 bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50 min-h-full">
            {/* Modais */}
            <AdicionarClienteModal
                isOpen={showAdicionarModal}
                onClose={() => setShowAdicionarModal(false)}
                onSuccess={handleClientSuccess}
            />

            <EditarLocalizacaoModal
                isOpen={showEditarLocalizacao}
                onClose={() => setShowEditarLocalizacao(false)}
                onSuccess={handleDataUpdate}
                localizacao={null}
                clienteId={selectedClient?.cliente_id || 0}
            />

            <EditarOcupacaoModal
                isOpen={showEditarOcupacao}
                onClose={() => setShowEditarOcupacao(false)}
                onSuccess={handleDataUpdate}
                ocupacao={null}
                clienteId={selectedClient?.cliente_id || 0}
            />

            <EditarDocumentoModal
                isOpen={showEditarDocumento}
                onClose={() => setShowEditarDocumento(false)}
                onSuccess={handleDataUpdate}
                documento={null}
                clienteId={selectedClient?.cliente_id || 0}
            />

            <EditarOutrosGanhosModal
                isOpen={showEditarGanhos}
                onClose={() => setShowEditarGanhos(false)}
                onSuccess={handleDataUpdate}
                ganho={null}
                clienteId={selectedClient?.cliente_id || 0}
            />

            {/* Cabeçalho */}
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-3">
                        <UserCircleIcon className="w-10 h-10 text-blue-600" />
                        Gestão de Clientes
                    </h1>
                    <p className="text-gray-600 mt-1">Sistema para gerenciamento de clientes e dados</p>
                </div>
                <button
                    onClick={() => setShowAdicionarModal(true)}
                    className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                    <PlusIcon className="w-5 h-5" />
                    Novo Cliente
                </button>
            </div>

            {/* Seletor de Cliente */}
            <div className="mb-6">
                <div className="bg-white rounded-lg shadow-md p-4">
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Selecionar Cliente
                    </label>
                    <div className="relative">
                        <button
                            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                            className="w-full flex items-center justify-between p-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                        >
                            <div className="flex items-center gap-2">
                                {selectedClient ? (
                                    <>
                                        <UserCircleIcon className="w-5 h-5 text-gray-500" />
                                        <span>{selectedClient.nome} - {selectedClient.telefone}</span>
                                    </>
                                ) : (
                                    <span className="text-gray-500">Selecione um cliente...</span>
                                )}
                            </div>
                            <ChevronDownIcon className={`w-5 h-5 text-gray-400 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} />
                        </button>

                        {isDropdownOpen && (
                            <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                                {loading ? (
                                    <div className="p-2 text-center text-gray-500">Carregando...</div>
                                ) : clients.length === 0 ? (
                                    <div className="p-2 text-center text-gray-500">Nenhum cliente encontrado</div>
                                ) : (
                                    clients.map(client => (
                                        <button
                                            key={client.cliente_id}
                                            onClick={() => {
                                                setSelectedClient(client);
                                                setIsDropdownOpen(false);
                                                setActiveTab('info');
                                            }}
                                            className="w-full flex items-center gap-2 p-2 hover:bg-gray-50 text-left"
                                        >
                                            <UserCircleIcon className="w-4 h-4 text-gray-500" />
                                            <span className="text-sm">{client.nome} - {client.telefone}</span>
                                        </button>
                                    ))
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Mensagem de Status */}
            {successMessage && (
                <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-2">
                    <CheckCircleIcon className="w-5 h-5 text-green-500" />
                    <p className="text-gray-800">{successMessage}</p>
                </div>
            )}

            {/* Conteúdo Principal */}
            <div className="bg-white rounded-lg shadow-md">
                {!selectedClient ? (
                    /* Tela de Boas-Vindas */
                    <div className="p-8 text-center">
                        <BuildingLibraryIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                        <h2 className="text-xl font-bold text-gray-800 mb-2">
                            Bem-vindo ao Sistema de Gestão de Clientes
                        </h2>
                        <p className="text-gray-600">
                            Selecione um cliente para visualizar seus dados ou adicione um novo cliente.
                        </p>
                    </div>
                ) : (
                    /* Cliente Selecionado */
                    <div>
                        {/* Header do Cliente */}
                        <div className="bg-gray-50 p-4 border-b border-gray-200 flex justify-between items-center">
                            <div>
                                <h2 className="text-xl font-bold text-gray-800">{selectedClient.nome}</h2>
                                <p className="text-gray-600">{selectedClient.telefone}</p>
                            </div>
                            <button
                                onClick={handleDeleteClient}
                                className="flex items-center gap-2 bg-red-600 text-white px-3 py-2 rounded-lg hover:bg-red-700 transition-colors"
                            >
                                <TrashIcon className="w-4 h-4" />
                                Remover Cliente
                            </button>
                        </div>

                        {/* Abas */}
                        <div className="border-b border-gray-200">
                            <div className="flex">
                                <button
                                    onClick={() => setActiveTab('info')}
                                    className={`flex items-center gap-2 px-4 py-3 border-b-2 font-medium text-sm ${
                                        activeTab === 'info' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-800'
                                    }`}
                                >
                                    <UserCircleIcon className="w-4 h-4" />
                                    Informações
                                </button>
                                <button
                                    onClick={() => setActiveTab('locations')}
                                    className={`flex items-center gap-2 px-4 py-3 border-b-2 font-medium text-sm ${
                                        activeTab === 'locations' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-800'
                                    }`}
                                >
                                    <MapPinIcon className="w-4 h-4" />
                                    Localização
                                </button>
                                <button
                                    onClick={() => setActiveTab('occupations')}
                                    className={`flex items-center gap-2 px-4 py-3 border-b-2 font-medium text-sm ${
                                        activeTab === 'occupations' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-800'
                                    }`}
                                >
                                    <BriefcaseIcon className="w-4 h-4" />
                                    Ocupação
                                </button>
                                <button
                                    onClick={() => setActiveTab('documents')}
                                    className={`flex items-center gap-2 px-4 py-3 border-b-2 font-medium text-sm ${
                                        activeTab === 'documents' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-800'
                                    }`}
                                >
                                    <DocumentIcon className="w-4 h-4" />
                                    Documentos
                                </button>
                                <button
                                    onClick={() => setActiveTab('income')}
                                    className={`flex items-center gap-2 px-4 py-3 border-b-2 font-medium text-sm ${
                                        activeTab === 'income' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-800'
                                    }`}
                                >
                                    <CurrencyDollarIcon className="w-4 h-4" />
                                    Outros Ganhos
                                </button>
                            </div>
                        </div>

                        <div className="p-6">
                            {activeTab === 'info' && (
                                <div>
                                    <h3 className="text-lg font-bold text-gray-800 mb-4">Informações Pessoais</h3>
                                    <div className="grid md:grid-cols-2 gap-4">
                                        <div className="space-y-3">
                                            <div className="p-3 bg-gray-50 rounded-lg">
                                                <span className="text-sm text-gray-600">Nome:</span>
                                                <p className="font-medium">{selectedClient.nome}</p>
                                            </div>
                                            <div className="p-3 bg-gray-50 rounded-lg">
                                                <span className="text-sm text-gray-600">Sexo:</span>
                                                <p className="font-medium">{selectedClient.sexo}</p>
                                            </div>
                                            <div className="p-3 bg-gray-50 rounded-lg">
                                                <span className="text-sm text-gray-600">Nacionalidade:</span>
                                                <p className="font-medium">{selectedClient.nacionalidade}</p>
                                            </div>
                                        </div>
                                        <div className="space-y-3">
                                            <div className="p-3 bg-gray-50 rounded-lg">
                                                <span className="text-sm text-gray-600">Data de Nascimento:</span>
                                                <p className="font-medium">{new Date(selectedClient.data_nascimento).toLocaleDateString()}</p>
                                            </div>
                                            <div className="p-3 bg-gray-50 rounded-lg">
                                                <span className="text-sm text-gray-600">Telefone:</span>
                                                <p className="font-medium">{selectedClient.telefone}</p>
                                            </div>
                                            <div className="p-3 bg-gray-50 rounded-lg">
                                                <span className="text-sm text-gray-600">Email:</span>
                                                <p className="font-medium">{selectedClient.email || 'Não informado'}</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {activeTab === 'locations' && (
                                <div>
                                    <div className="flex justify-between items-center mb-6">
                                        <h3 className="text-xl font-bold text-gray-800">Localização do Cliente ({localizacoes.length} registros)</h3>
                                        <button
                                            onClick={() => setShowEditarLocalizacao(true)}
                                            className="flex items-center gap-2 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
                                        >
                                            <PlusIcon className="w-4 h-4" />
                                            {localizacoes.length === 0 ? 'Adicionar' : 'Editar'}
                                        </button>
                                    </div>

                                    {/* Debug info */}
                                    <div className="mb-4 p-2 bg-blue-50 border border-blue-200 rounded">
                                        <p className="text-xs text-blue-800">Debug: clientId = {selectedClient?.cliente_id}, localizacoes.length = {localizacoes.length}</p>
                                        {localizacoes.length > 0 && (
                                            <pre className="text-xs text-blue-700 mt-1">{JSON.stringify(localizacoes, null, 2)}</pre>
                                        )}
                                    </div>

                                    {localizacoes.length === 0 ? (
                                        <div className="text-center py-12">
                                            <MapPinIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                                            <p className="text-gray-500 text-lg mb-4">Nenhuma localização cadastrada</p>
                                            <button
                                                onClick={() => setShowEditarLocalizacao(true)}
                                                className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
                                            >
                                                Adicionar Localização
                                            </button>
                                        </div>
                                    ) : (
                                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                            {localizacoes.map(location => (
                                                <div key={location.localizacao_id} className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
                                                    <div className="flex items-start justify-between mb-4">
                                                        <div className="flex items-center gap-2">
                                                            <MapPinIcon className="w-6 h-6 text-red-600" />
                                                            <h4 className="font-semibold text-gray-800">Localização</h4>
                                                        </div>
                                                        <button
                                                            onClick={() => localizacoesAPI.deletar(location.localizacao_id).then(handleDataUpdate)}
                                                            className="text-red-500 hover:text-red-700 p-1 rounded hover:bg-red-50 transition-colors"
                                                        >
                                                            <TrashIcon className="w-4 h-4" />
                                                        </button>
                                                    </div>

                                                    <div className="space-y-3">
                                                        <div className="flex justify-between">
                                                            <span className="text-sm text-gray-600">Província:</span>
                                                            <span className="text-sm font-medium">{location.provincia}</span>
                                                        </div>
                                                        <div className="flex justify-between">
                                                            <span className="text-sm text-gray-600">Cidade:</span>
                                                            <span className="text-sm font-medium">{location.cidade}</span>
                                                        </div>
                                                        <div className="flex justify-between">
                                                            <span className="text-sm text-gray-600">Distrito:</span>
                                                            <span className="text-sm font-medium">{location.distrito}</span>
                                                        </div>
                                                        <div className="flex justify-between">
                                                            <span className="text-sm text-gray-600">Bairro:</span>
                                                            <span className="text-sm font-medium">{location.bairro}</span>
                                                        </div>
                                                        <div className="flex justify-between">
                                                            <span className="text-sm text-gray-600">Quarteirão:</span>
                                                            <span className="text-sm font-medium">{location.quarteirao}</span>
                                                        </div>
                                                        <div className="flex justify-between">
                                                            <span className="text-sm text-gray-600">Nº Casa:</span>
                                                            <span className="text-sm font-medium">{location.numero_da_casa}</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}

                            {activeTab === 'occupations' && (
                                <div>
                                    <div className="flex justify-between items-center mb-6">
                                        <h3 className="text-xl font-bold text-gray-800">Ocupação Profissional do Cliente</h3>
                                        <button
                                            onClick={() => setShowEditarOcupacao(true)}
                                            className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                                        >
                                            <PlusIcon className="w-4 h-4" />
                                            {ocupacoes.length === 0 ? 'Adicionar' : 'Editar'}
                                        </button>
                                    </div>

                                    {ocupacoes.length === 0 ? (
                                        <div className="text-center py-12">
                                            <BriefcaseIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                                            <p className="text-gray-500 text-lg mb-4">Nenhuma ocupação cadastrada</p>
                                            <button
                                                onClick={() => setShowEditarOcupacao(true)}
                                                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                                            >
                                                Adicionar Ocupação
                                            </button>
                                        </div>
                                    ) : (
                                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                            {ocupacoes.map(occupation => (
                                                <div key={occupation.ocupacao_id} className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
                                                    <div className="flex items-start justify-between mb-4">
                                                        <div className="flex items-center gap-2">
                                                            <BriefcaseIcon className="w-6 h-6 text-green-600" />
                                                            <h4 className="font-semibold text-gray-800">{occupation.nome}</h4>
                                                        </div>
                                                        <button
                                                            onClick={() => ocupacoesAPI.deletar(occupation.ocupacao_id).then(handleDataUpdate)}
                                                            className="text-red-500 hover:text-red-700 p-1 rounded hover:bg-red-50 transition-colors"
                                                        >
                                                            <TrashIcon className="w-4 h-4" />
                                                        </button>
                                                    </div>

                                                    <div className="mb-4">
                                                        <p className="text-gray-700 text-sm">{occupation.descricao || 'Sem descrição'}</p>
                                                    </div>

                                                    <div className="space-y-2">
                                                        <div className="flex justify-between">
                                                            <span className="text-sm text-gray-600">Código:</span>
                                                            <span className="text-sm font-medium">{occupation.codigo || 'N/A'}</span>
                                                        </div>
                                                        <div className="flex justify-between">
                                                            <span className="text-sm text-gray-600">Setor:</span>
                                                            <span className="text-sm font-medium">{occupation.setor_economico}</span>
                                                        </div>
                                                        <div className="flex justify-between">
                                                            <span className="text-sm text-gray-600">Categoria de Risco:</span>
                                                            <span className={`text-sm font-medium px-2 py-1 rounded ${
                                                                occupation.categoria_risco === 'Baixo' ? 'bg-green-100 text-green-800' :
                                                                occupation.categoria_risco === 'Medio' ? 'bg-yellow-100 text-yellow-800' :
                                                                occupation.categoria_risco === 'Alto' ? 'bg-orange-100 text-orange-800' :
                                                                'bg-red-100 text-red-800'
                                                            }`}>
                                                                {occupation.categoria_risco}
                                                            </span>
                                                        </div>
                                                        {occupation.renda_minima && (
                                                            <div className="flex justify-between">
                                                                <span className="text-sm text-gray-600">Renda Mínima:</span>
                                                                <span className="text-sm font-medium">{occupation.renda_minima} MT</span>
                                                            </div>
                                                        )}
                                                        {occupation.estabilidade_emprego && (
                                                            <div className="flex justify-between">
                                                                <span className="text-sm text-gray-600">Estabilidade:</span>
                                                                <span className="text-sm font-medium">{occupation.estabilidade_emprego}</span>
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}

                            {activeTab === 'documents' && (
                                <div>
                                    <div className="flex justify-between items-center mb-6">
                                        <h3 className="text-xl font-bold text-gray-800">Documentos do Cliente</h3>
                                        <button
                                            onClick={() => setShowEditarDocumento(true)}
                                            className="flex items-center gap-2 bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition-colors"
                                        >
                                            <PlusIcon className="w-4 h-4" />
                                            {documentos.length === 0 ? 'Adicionar' : 'Editar'}
                                        </button>
                                    </div>

                                    {documentos.length === 0 ? (
                                        <div className="text-center py-12">
                                            <DocumentIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                                            <p className="text-gray-500 text-lg mb-4">Nenhum documento cadastrado</p>
                                            <button
                                                onClick={() => setShowEditarDocumento(true)}
                                                className="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition-colors"
                                            >
                                                Adicionar Documento
                                            </button>
                                        </div>
                                    ) : (
                                        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                                            {documentos.map(document => (
                                                <div key={document.documento_id} className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
                                                    <div className="flex items-start justify-between mb-4">
                                                        <div className="flex items-center gap-2">
                                                            <DocumentIcon className="w-6 h-6 text-orange-600" />
                                                            <h4 className="font-semibold text-gray-800">{document.tipo_documento}</h4>
                                                        </div>
                                                        <div className="flex gap-1">
                                                            <button
                                                                onClick={() => documentosAPI.download && documentosAPI.download(document.documento_id)}
                                                                className="text-blue-500 hover:text-blue-700 p-1 rounded hover:bg-blue-50 transition-colors"
                                                                title="Download"
                                                            >
                                                                <ArrowDownTrayIcon className="w-4 h-4" />
                                                            </button>
                                                            <button
                                                                onClick={() => documentosAPI.deletar(document.documento_id).then(handleDataUpdate)}
                                                                className="text-red-500 hover:text-red-700 p-1 rounded hover:bg-red-50 transition-colors"
                                                                title="Excluir"
                                                            >
                                                                <TrashIcon className="w-4 h-4" />
                                                            </button>
                                                        </div>
                                                    </div>

                                                    <div className="space-y-3">
                                                        <div className="flex justify-between">
                                                            <span className="text-sm text-gray-600">Número:</span>
                                                            <span className="text-sm font-medium font-mono">{document.numero_documento}</span>
                                                        </div>
                                                        <div className="flex justify-between">
                                                            <span className="text-sm text-gray-600">Emissão:</span>
                                                            <span className="text-sm font-medium">{new Date(document.data_emissao).toLocaleDateString()}</span>
                                                        </div>
                                                        {document.data_validade && (
                                                            <div className="flex justify-between">
                                                                <span className="text-sm text-gray-600">Validade:</span>
                                                                <span className="text-sm font-medium">{new Date(document.data_validade).toLocaleDateString()}</span>
                                                            </div>
                                                        )}
                                                        {document.arquivo && (
                                                            <div className="mt-4 p-3 bg-orange-50 border border-orange-200 rounded-lg">
                                                                <p className="text-xs text-orange-800 flex items-center gap-1">
                                                                    <DocumentIcon className="w-3 h-3" />
                                                                    Arquivo anexado
                                                                </p>
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}

                            {activeTab === 'income' && (
                                <div>
                                    <div className="flex justify-between items-center mb-6">
                                        <h3 className="text-xl font-bold text-gray-800">Outros Ganhos do Cliente</h3>
                                        <button
                                            onClick={() => setShowEditarGanhos(true)}
                                            className="flex items-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors"
                                        >
                                            <PlusIcon className="w-4 h-4" />
                                            {outrosGanhos.length === 0 ? 'Adicionar' : 'Editar'}
                                        </button>
                                    </div>

                                    {outrosGanhos.length === 0 ? (
                                        <div className="text-center py-12">
                                            <CurrencyDollarIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                                            <p className="text-gray-500 text-lg mb-4">Nenhum outro ganho cadastrado</p>
                                            <button
                                                onClick={() => setShowEditarGanhos(true)}
                                                className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors"
                                            >
                                                Adicionar Ganho
                                            </button>
                                        </div>
                                    ) : (
                                        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                                            {outrosGanhos.map(income => (
                                                <div key={income.ganho_id} className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
                                                    <div className="flex items-start justify-between mb-4">
                                                        <div className="flex items-center gap-2">
                                                            <CurrencyDollarIcon className="w-6 h-6 text-purple-600" />
                                                            <h4 className="font-semibold text-gray-800">{income.descricao}</h4>
                                                        </div>
                                                        <button
                                                            onClick={() => outrosGanhosAPI.deletar(income.ganho_id).then(handleDataUpdate)}
                                                            className="text-red-500 hover:text-red-700 p-1 rounded hover:bg-red-50 transition-colors"
                                                        >
                                                            <TrashIcon className="w-4 h-4" />
                                                        </button>
                                                    </div>

                                                    <div className="space-y-3">
                                                        <div className="flex justify-between">
                                                            <span className="text-sm text-gray-600">Valor:</span>
                                                            <span className="text-lg font-bold text-purple-600">{income.valor.toLocaleString()} MT</span>
                                                        </div>
                                                        <div className="flex justify-between">
                                                            <span className="text-sm text-gray-600">Frequência:</span>
                                                            <span className={`text-sm font-medium px-2 py-1 rounded ${
                                                                income.frequencia === 'MENSAL' ? 'bg-blue-100 text-blue-800' :
                                                                income.frequencia === 'ANUAL' ? 'bg-green-100 text-green-800' :
                                                                income.frequencia === 'DIARIO' ? 'bg-yellow-100 text-yellow-800' :
                                                                'bg-gray-100 text-gray-800'
                                                            }`}>
                                                                {income.frequencia || 'N/A'}
                                                            </span>
                                                        </div>

                                                        {/* Cálculo aproximado baseado na frequência */}
                                                        {income.frequencia && (
                                                            <div className="mt-4 p-3 bg-purple-50 border border-purple-200 rounded-lg">
                                                                <p className="text-xs text-purple-800">
                                                                    Estimativa: {
                                                                        income.frequencia === 'DIARIO' ? `${(income.valor * 30).toLocaleString()} MT/mês` :
                                                                        income.frequencia === 'SEMANAL' ? `${(income.valor * 4).toLocaleString()} MT/mês` :
                                                                        income.frequencia === 'MENSAL' ? `${income.valor.toLocaleString()} MT/mês` :
                                                                        income.frequencia === 'TRIMESTRAL' ? `${Math.round(income.valor / 3).toLocaleString()} MT/mês` :
                                                                        income.frequencia === 'SEMESTRAL' ? `${Math.round(income.valor / 6).toLocaleString()} MT/mês` :
                                                                        income.frequencia === 'ANUAL' ? `${Math.round(income.valor / 12).toLocaleString()} MT/mês` :
                                                                        'Valor único'
                                                                    }
                                                                </p>
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default GestaoClientes;
