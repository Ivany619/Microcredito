
import React from 'react';

const Cobrancas: React.FC = () => {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Gestão de Cobranças</h1>
      <div className="bg-white p-6 rounded-lg shadow-md">
        <p className="text-gray-700">
          Esta seção foca na gestão de pagamentos em atraso. Os administradores podem visualizar uma lista de clientes inadimplentes, registrar tentativas de contato, e iniciar processos de negociação de dívidas para regularizar a situação dos pagamentos.
        </p>
      </div>
    </div>
  );
};

export default Cobrancas;
