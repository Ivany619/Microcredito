
import React, { useState, useMemo } from 'react';

const Simulator: React.FC = () => {
  const [amount, setAmount] = useState<number>(5000);
  const [months, setMonths] = useState<number>(12);
  const INTEREST_RATE = 0.20;

  const { totalRepayment, monthlyPayment } = useMemo(() => {
    const total = amount * (1 + INTEREST_RATE);
    const monthly = total / months;
    return {
      totalRepayment: total,
      monthlyPayment: monthly,
    };
  }, [amount, months]);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-MZ', { style: 'currency', currency: 'MZN' }).format(value);
  };

  return (
    <div className="bg-gray-50 py-20 animate-fade-in">
        <div className="container mx-auto px-6">
            <div className="text-center mb-12">
                <h1 className="text-5xl font-extrabold text-brand-blue-dark">Simulador de Empréstimo</h1>
                <p className="text-xl text-gray-600 mt-4 max-w-3xl mx-auto">
                    Planeie o seu futuro. Veja como um empréstimo da Lacos pode caber no seu orçamento.
                </p>
            </div>

            <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-2xl p-8 md:p-12">
                <div className="grid md:grid-cols-2 gap-10">
                    {/* Input Section */}
                    <div className="space-y-8">
                        <div>
                            <label htmlFor="amount" className="text-lg font-semibold text-gray-700 block mb-2">
                                Quantia do Empréstimo: <span className="text-brand-blue font-bold">{formatCurrency(amount)}</span>
                            </label>
                            <input
                                type="range"
                                id="amount"
                                min="1000"
                                max="100000"
                                step="1000"
                                value={amount}
                                onChange={(e) => setAmount(Number(e.target.value))}
                                className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer range-lg accent-brand-blue"
                            />
                        </div>
                        <div>
                            <label htmlFor="months" className="text-lg font-semibold text-gray-700 block mb-2">
                                Prazo de Pagamento: <span className="text-brand-blue font-bold">{months} meses</span>
                            </label>
                            <input
                                type="range"
                                id="months"
                                min="3"
                                max="36"
                                step="1"
                                value={months}
                                onChange={(e) => setMonths(Number(e.target.value))}
                                className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer range-lg accent-brand-blue"
                            />
                        </div>
                    </div>
                    
                    {/* Results Section */}
                    <div className="bg-brand-blue-dark text-white rounded-xl p-8 flex flex-col justify-center text-center">
                        <h3 className="text-lg font-semibold text-gray-300 mb-2">Prestação Mensal</h3>
                        <p className="text-5xl font-extrabold text-brand-gold mb-6">
                            {formatCurrency(monthlyPayment)}
                        </p>
                        
                        <div className="text-left space-y-2 text-gray-200">
                           <div className="flex justify-between items-center">
                               <span>Valor Solicitado:</span>
                               <span className="font-semibold">{formatCurrency(amount)}</span>
                           </div>
                           <div className="flex justify-between items-center">
                               <span>Taxa de Juro (20%):</span>
                               <span className="font-semibold">{formatCurrency(amount * INTEREST_RATE)}</span>
                           </div>
                           <div className="flex justify-between items-center border-t border-brand-blue-light pt-2 mt-2">
                               <span className="font-bold">Total a Pagar:</span>
                               <span className="font-bold text-lg">{formatCurrency(totalRepayment)}</span>
                           </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
  );
};

export default Simulator;
