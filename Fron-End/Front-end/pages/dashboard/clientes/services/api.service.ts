// Serviço centralizado de API para gestão de clientes

import {
    Cliente,
    Localizacao,
    Ocupacao,
    Documento,
    OutroGanho,
    ClienteCompleto
} from '../types';

const API_BASE = 'http://localhost:8000/api';

// Helper para obter token de autenticação
const getAuthHeaders = () => {
    const token = localStorage.getItem('authToken');
    return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };
};

// ==================== CLIENTES ====================

export const clientesAPI = {
    listar: async (): Promise<Cliente[]> => {
        const response = await fetch(`${API_BASE}/clientes/listar`, {
            headers: getAuthHeaders()
        });
        if (!response.ok) throw new Error('Erro ao listar clientes');
        return response.json();
    },

    buscarPorId: async (id: number): Promise<Cliente> => {
        const response = await fetch(`${API_BASE}/clientes/buscar/${id}`, {
            headers: getAuthHeaders()
        });
        if (!response.ok) throw new Error('Erro ao buscar cliente');
        return response.json();
    },

    criar: async (data: Partial<Cliente>): Promise<Cliente> => {
        const response = await fetch(`${API_BASE}/clientes/criar`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao criar cliente');
        }
        return response.json();
    },

    atualizar: async (id: number, data: Partial<Cliente>): Promise<Cliente> => {
        const response = await fetch(`${API_BASE}/clientes/atualizar/${id}`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error('Erro ao atualizar cliente');
        return response.json();
    },

    deletar: async (id: number): Promise<void> => {
        const response = await fetch(`${API_BASE}/clientes/remover/${id}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        if (!response.ok) throw new Error('Erro ao deletar cliente');
    },

    criarCompleto: async (data: ClienteCompleto): Promise<any> => {
        const response = await fetch(`${API_BASE}/clientes/criar-completo`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao criar cliente completo');
        }
        return response.json();
    }
};

// ==================== LOCALIZAÇÕES ====================

export const localizacoesAPI = {
    listar: async (): Promise<Localizacao[]> => {
        const response = await fetch(`${API_BASE}/localizacoes/listar`, {
            headers: getAuthHeaders()
        });
        if (!response.ok) throw new Error('Erro ao listar localizações');
        return response.json();
    },

    buscarPorCliente: async (clienteId: number): Promise<Localizacao[]> => {
        const response = await fetch(`${API_BASE}/localizacoes/cliente/${clienteId}`, {
            headers: getAuthHeaders()
        });
        if (!response.ok) throw new Error('Erro ao buscar localizações do cliente');
        return response.json();
    },

    criar: async (data: Partial<Localizacao>): Promise<Localizacao> => {
        const response = await fetch(`${API_BASE}/localizacoes/criar`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao criar localização');
        }
        return response.json();
    },

    atualizar: async (id: number, data: Partial<Localizacao>): Promise<Localizacao> => {
        const response = await fetch(`${API_BASE}/localizacoes/atualizar/${id}`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error('Erro ao atualizar localização');
        return response.json();
    },

    deletar: async (id: number): Promise<void> => {
        const response = await fetch(`${API_BASE}/localizacoes/remover/${id}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        if (!response.ok) throw new Error('Erro ao deletar localização');
    }
};

// ==================== OCUPAÇÕES ====================

export const ocupacoesAPI = {
    listar: async (): Promise<Ocupacao[]> => {
        const response = await fetch(`${API_BASE}/ocupacoes/listar`, {
            headers: getAuthHeaders()
        });
        if (!response.ok) throw new Error('Erro ao listar ocupações');
        return response.json();
    },

    buscarPorCliente: async (clienteId: number): Promise<Ocupacao[]> => {
        const response = await fetch(`${API_BASE}/ocupacoes/cliente/${clienteId}`, {
            headers: getAuthHeaders()
        });
        if (!response.ok) throw new Error('Erro ao buscar ocupações do cliente');
        return response.json();
    },

    criar: async (data: Partial<Ocupacao>): Promise<Ocupacao> => {
        const response = await fetch(`${API_BASE}/ocupacoes/criar`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao criar ocupação');
        }
        return response.json();
    },

    atualizar: async (id: number, data: Partial<Ocupacao>): Promise<Ocupacao> => {
        const response = await fetch(`${API_BASE}/ocupacoes/atualizar/${id}`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error('Erro ao atualizar ocupação');
        return response.json();
    },

    deletar: async (id: number): Promise<void> => {
        const response = await fetch(`${API_BASE}/ocupacoes/remover/${id}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        if (!response.ok) throw new Error('Erro ao deletar ocupação');
    }
};

// ==================== DOCUMENTOS ====================

export const documentosAPI = {
    listar: async (): Promise<Documento[]> => {
        const response = await fetch(`${API_BASE}/documentos/listar`, {
            headers: getAuthHeaders()
        });
        if (!response.ok) throw new Error('Erro ao listar documentos');
        return response.json();
    },

    buscarPorCliente: async (clienteId: number): Promise<Documento[]> => {
        const response = await fetch(`${API_BASE}/documentos/cliente/${clienteId}`, {
            headers: getAuthHeaders()
        });
        if (!response.ok) throw new Error('Erro ao buscar documentos do cliente');
        return response.json();
    },

    criar: async (data: FormData): Promise<Documento> => {
        const token = localStorage.getItem('authToken');
        const response = await fetch(`${API_BASE}/documentos/criar`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
                // Não incluir Content-Type para FormData
            },
            body: data
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao criar documento');
        }
        return response.json();
    },

    atualizar: async (id: number, data: Partial<Documento>): Promise<Documento> => {
        const response = await fetch(`${API_BASE}/documentos/atualizar/${id}`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error('Erro ao atualizar documento');
        return response.json();
    },

    deletar: async (id: number): Promise<void> => {
        const response = await fetch(`${API_BASE}/documentos/remover/${id}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        if (!response.ok) throw new Error('Erro ao deletar documento');
    },

    download: async (id: number): Promise<Response> => {
        const response = await fetch(`${API_BASE}/documentos/download/${id}`, {
            headers: getAuthHeaders()
        });
        if (!response.ok) throw new Error('Erro ao fazer download do documento');
        return response;
    }
};

// ==================== OUTROS GANHOS ====================

export const outrosGanhosAPI = {
    listar: async (): Promise<OutroGanho[]> => {
        const response = await fetch(`${API_BASE}/outros-ganhos/listar`, {
            headers: getAuthHeaders()
        });
        if (!response.ok) throw new Error('Erro ao listar outros ganhos');
        return response.json();
    },

    buscarPorCliente: async (clienteId: number): Promise<OutroGanho[]> => {
        const response = await fetch(`${API_BASE}/outros-ganhos/cliente/${clienteId}`, {
            headers: getAuthHeaders()
        });
        if (!response.ok) throw new Error('Erro ao buscar outros ganhos do cliente');
        return response.json();
    },

    criar: async (data: Partial<OutroGanho>): Promise<OutroGanho> => {
        const response = await fetch(`${API_BASE}/outros-ganhos/criar`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao criar outro ganho');
        }
        return response.json();
    },

    atualizar: async (id: number, data: Partial<OutroGanho>): Promise<OutroGanho> => {
        const response = await fetch(`${API_BASE}/outros-ganhos/atualizar/${id}`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error('Erro ao atualizar outro ganho');
        return response.json();
    },

    deletar: async (id: number): Promise<void> => {
        const response = await fetch(`${API_BASE}/outros-ganhos/remover/${id}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        if (!response.ok) throw new Error('Erro ao deletar outro ganho');
    }
};
