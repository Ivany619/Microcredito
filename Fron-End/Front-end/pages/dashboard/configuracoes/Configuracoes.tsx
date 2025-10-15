
import React from 'react';

const Configuracoes: React.FC = () => {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Configurações</h1>
      <div className="bg-white p-6 rounded-lg shadow-md">
        <p className="text-gray-700">
          Nesta seção, os administradores podem configurar as regras do sistema. Isso inclui a criação e edição de diferentes tipos de produtos de crédito, a gestão de utilizadores do painel de administração e a personalização de templates de comunicação automática com os clientes.
        </p>
      </div>
    </div>
  );
};

export default Configuracoes;
