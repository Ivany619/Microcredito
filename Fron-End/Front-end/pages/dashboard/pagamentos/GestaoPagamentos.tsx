import React, { useState } from 'react';
import { CalendarIcon } from '../../../components/icons/CalendarIcon';
import { FundsIcon } from '../../../components/icons/FundsIcon';
import { BaobabIcon } from '../../../components/icons/BaobabIcon';

// A simple Icon for the payment methods
const PaymentIcon: React.FC<{ method: string }> = ({ method }) => {
    // In a real app, you would have specific icons for each payment method
    return <span className="mr-2 text-xl">💵</span>;
};

// Placeholder data for clients and loans
const clients = [
    { id: 1, name: 'João Silva' },
    { id: 2, name: 'Maria Santos' },
];

const loans = [
    { id: 1, name: 'Empréstimo #1' },
    { id: 2, name: 'Empréstimo #2' },
];

// Mock payment data
const mockPayments = [
    {
        pagamento_id: 1,
        emprestimo_id: 1,
        cliente_id: 1,
        valor_pago: 500.00,
        data_pagamento: '2024-07-28T10:00:00Z',
        metodo_pagamento: 'M-Pesa',
        referencia_pagamento: 'MPESA12345',
    },
    {
        pagamento_id: 2,
        emprestimo_id: 2,
        cliente_id: 2,
        valor_pago: 1200.50,
        data_pagamento: '2024-07-27T15:30:00Z',
        metodo_pagamento: 'Transferência Bancária',
        referencia_pagamento: 'TB-67890',
    },
];

const GestaoPagamentos: React.FC = () => {
    const [payments, setPayments] = useState(mockPayments);
    const [isModalOpen, setIsModalOpen] = useState(false);

    // Form state
    const [emprestimoId, setEmprestimoId] = useState('');
    const [clienteId, setClienteId] = useState('');
    const [valorPago, setValorPago] = useState('');
    const [dataPagamento, setDataPagamento] = useState('');
    const [metodoPagamento, setMetodoPagamento] = useState('Numerario');
    const [referenciaPagamento, setReferenciaPagamento] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        const newPayment = {
            pagamento_id: payments.length + 1,
            emprestimo_id: parseInt(emprestimoId, 10),
            cliente_id: parseInt(clienteId, 10),
            valor_pago: parseFloat(valorPago),
            data_pagamento: new Date(dataPagamento).toISOString(),
            metodo_pagamento: metodoPagamento,
            referencia_pagamento: referenciaPagamento,
        };
        setPayments([...payments, newPayment]);
        setIsModalOpen(false);
        // Reset form
        setEmprestimoId('');
        setClienteId('');
        setValorPago('');
        setDataPagamento('');
        setMetodoPagamento('Numerario');
        setReferenciaPagamento('');
    };
    
    const paymentMethods = ['Numerario', 'Transferência Bancária', 'M-Pesa', 'E-Mola', 'MKesh', 'Penhor', 'Outro'];


    return (
        <div className="p-6 bg-gray-50 min-h-screen text-gray-800">
            <header className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                    <BaobabIcon className="w-8 h-8 mr-3 text-green-600" />
                    Gestão de Pagamentos
                </h1>
                <button
                    onClick={() => setIsModalOpen(true)}
                    className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg shadow-md transition-transform transform hover:scale-105 flex items-center"
                >
                     <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    Adicionar Pagamento
                </button>
            </header>
            
            {isModalOpen && (
                <div className="fixed inset-0 bg-black bg-opacity-50 z-40 flex items-center justify-center">
                    <div className="bg-white rounded-xl shadow-2xl p-8 m-4 max-w-2xl w-full relative transform transition-all duration-300 ease-in-out scale-100">
                        <button onClick={() => setIsModalOpen(false)} className="absolute top-4 right-4 text-gray-500 hover:text-gray-800 text-2xl font-bold">
                            &times;
                        </button>
                        <h2 className="text-2xl font-bold mb-6 text-gray-800">Novo Pagamento</h2>
                        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {/* Cliente */}
                            <div className="flex flex-col">
                                <label htmlFor="clienteId" className="mb-2 font-semibold text-gray-700">Cliente</label>
                                <select id="clienteId" value={clienteId} onChange={(e) => setClienteId(e.target.value)} className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition">
                                    <option value="">Selecione um cliente</option>
                                    {clients.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                                </select>
                            </div>
                            {/* Empréstimo */}
                            <div className="flex flex-col">
                                <label htmlFor="emprestimoId" className="mb-2 font-semibold text-gray-700">Empréstimo</label>
                                <select id="emprestimoId" value={emprestimoId} onChange={(e) => setEmprestimoId(e.target.value)} className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition">
                                    <option value="">Selecione um empréstimo</option>
                                    {loans.map(l => <option key={l.id} value={l.id}>{l.name}</option>)}
                                </select>
                            </div>
                            {/* Valor Pago */}
                            <div className="flex flex-col">
                                <label htmlFor="valorPago" className="mb-2 font-semibold text-gray-700 flex items-center"><FundsIcon className="w-5 h-5 mr-2 text-green-600"/>Valor Pago</label>
                                <input type="number" id="valorPago" value={valorPago} onChange={(e) => setValorPago(e.target.value)} className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition" placeholder="Ex: 500.00"/>
                            </div>
                             {/* Data Pagamento */}
                             <div className="flex flex-col">
                                <label htmlFor="dataPagamento" className="mb-2 font-semibold text-gray-700 flex items-center"><CalendarIcon className="w-5 h-5 mr-2 text-green-600"/>Data do Pagamento</label>
                                <input type="datetime-local" id="dataPagamento" value={dataPagamento} onChange={(e) => setDataPagamento(e.target.value)} className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition"/>
                            </div>
                            {/* Método de Pagamento */}
                            <div className="flex flex-col">
                                <label htmlFor="metodoPagamento" className="mb-2 font-semibold text-gray-700">Método de Pagamento</label>
                                <select id="metodoPagamento" value={metodoPagamento} onChange={(e) => setMetodoPagamento(e.target.value)} className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition">
                                    {paymentMethods.map(method => <option key={method} value={method}>{method}</option>)}
                                </select>
                            </div>
                             {/* Referência do Pagamento */}
                             <div className="flex flex-col">
                                <label htmlFor="referenciaPagamento" className="mb-2 font-semibold text-gray-700">Referência do Pagamento</label>
                                <input type="text" id="referenciaPagamento" value={referenciaPagamento} onChange={(e) => setReferenciaPagamento(e.target.value)} className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition" placeholder="Ex: MPESA123XYZ"/>
                            </div>
                            <div className="md:col-span-2 flex justify-end">
                                <button type="submit" className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg shadow-md transition-transform transform hover:scale-105">
                                    Salvar Pagamento
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-xl font-semibold mb-4 text-gray-700">Histórico de Pagamentos</h2>
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-gray-100">
                            <tr>
                                <th className="p-4 font-semibold">Cliente</th>
                                <th className="p-4 font-semibold">Valor Pago</th>
                                <th className="p-4 font-semibold">Data</th>
                                <th className="p-4 font-semibold">Método</th>
                                <th className="p-4 font-semibold">Referência</th>
                            </tr>
                        </thead>
                        <tbody>
                            {payments.map(p => (
                                <tr key={p.pagamento_id} className="border-b hover:bg-gray-50">
                                    <td className="p-4">{clients.find(c => c.id === p.cliente_id)?.name}</td>
                                    <td className="p-4 font-medium text-green-600">MZN {p.valor_pago.toFixed(2)}</td>
                                    <td className="p-4">{new Date(p.data_pagamento).toLocaleDateString()}</td>
                                    <td className="p-4 flex items-center">
                                        <PaymentIcon method={p.metodo_pagamento} />
                                        {p.metodo_pagamento}
                                    </td>
                                    <td className="p-4 text-gray-600">{p.referencia_pagamento}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default GestaoPagamentos;
