
import React from 'react';

const AnaliseCredito: React.FC = () => {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Análise de Crédito</h1>
      <div className="bg-white p-6 rounded-lg shadow-md">
        <p className="text-gray-700">
          Esta página é dedicada à avaliação de novos pedidos de empréstimo. Aqui, os administradores podem revisar as informações dos solicitantes, analisar a documentação e aprovar ou recusar propostas de crédito com base nas políticas da instituição.
        </p>
      </div>
    </div>
  );
};

export default AnaliseCredito;
