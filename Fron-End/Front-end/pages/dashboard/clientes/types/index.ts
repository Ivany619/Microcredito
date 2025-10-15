// Tipos centralizados para gestão de clientes

export interface Cliente {
    cliente_id?: number;
    nome: string;
    sexo: 'Masculino' | 'Feminino' | 'Outro';
    telefone: string;
    email?: string;
    nacionalidade: 'Moçambicana' | 'Estrangeira';
    data_nascimento: string; // Formato date (YYYY-MM-DD)
    data_cadastro?: string;
}

export interface Localizacao {
    localizacao_id?: number;
    cliente_id: number;
    provincia: string;
    cidade: string;
    distrito: string;
    bairro?: string;
    quarteirao?: string;
    numero_da_casa?: string;
}

export interface Ocupacao {
    ocupacao_id?: number;
    cliente_id: number;
    codigo: string;
    nome: string;
    descricao?: string;
    setor_economico: string; // Allow string for form handling
    categoria_risco: string; // Allow string for form handling
    renda_minima?: number;
    estabilidade_emprego: string; // Allow string for form handling
    ativo?: boolean;
}

export interface Documento {
    documento_id: number;
    cliente_id: number;
    tipo_documento: string;
    numero_documento: string;
    data_emissao?: string;
    data_validade?: string;
    arquivo?: string;
}

export interface OutroGanho {
    ganho_id: number;
    cliente_id: number;
    descricao: string;
    valor: number;
    frequencia?: string;
}

export interface DocumentoForm {
    tipo_documento: string;
    numero_documento: string;
    data_emissao: string;
    data_validade: string;
    arquivo: File | null;
}

export interface ClienteCompleto {
    cliente: Partial<Cliente>;
    localizacao?: Partial<Localizacao>;
    ocupacao?: Partial<Ocupacao>;
    documentos?: DocumentoForm[];
    outros_ganhos?: Partial<OutroGanho>[];
}

// For form usage, allowing empty strings for required fields initially
export interface ClienteForm {
    nome: string;
    sexo: string; // Allow empty string initially
    telefone: string;
    nacionalidade: string; // Allow empty string initially
    data_nascimento: string;
    email?: string;
    data_cadastro?: string;
}

export interface OcupacaoForm extends Partial<Ocupacao> {
    setor_economico: string; // Allow string initially
    categoria_risco: string; // Allow string initially
    estabilidade_emprego: string; // Allow string initially
}

export interface ApiResponse<T> {
    success: boolean;
    data?: T;
    error?: string;
    message?: string;
}
