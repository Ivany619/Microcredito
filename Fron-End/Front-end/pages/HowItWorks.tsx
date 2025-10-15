
import React from 'react';
import { ApplicationIcon } from '../components/icons/ApplicationIcon';
import { ApprovalIcon } from '../components/icons/ApprovalIcon';
import { FundsIcon } from '../components/icons/FundsIcon';

const Step: React.FC<{ icon: React.ReactNode; number: number; title: string; description: string; delay: string }> = ({ icon, number, title, description, delay }) => (
    <div className="relative pl-16 animate-fade-in-up" style={{ animationDelay: delay }}>
        <div className="absolute left-0 top-0 flex items-center justify-center h-12 w-12 rounded-full bg-brand-gold text-brand-blue-dark font-extrabold text-2xl shadow-md">
            {number}
        </div>
        <div className="bg-white p-8 rounded-xl shadow-lg">
            <div className="text-brand-blue mb-4">{icon}</div>
            <h3 className="text-2xl font-bold text-brand-blue-dark mb-3">{title}</h3>
            <p className="text-gray-600">{description}</p>
        </div>
    </div>
);

const HowItWorks: React.FC = () => {
    return (
        <div className="bg-gray-50 py-20 animate-fade-in">
            <div className="container mx-auto px-6">
                <div className="text-center mb-16">
                    <h1 className="text-5xl font-extrabold text-brand-blue-dark">Como Funciona</h1>
                    <p className="text-xl text-gray-600 mt-4 max-w-3xl mx-auto">
                        Obter o seu empréstimo é um processo simples, rápido e transparente. Siga estes 3 passos.
                    </p>
                </div>

                <div className="max-w-3xl mx-auto">
                    <div className="relative space-y-12">
                        {/* Connecting line */}
                        <div className="absolute left-6 top-6 bottom-6 w-0.5 bg-brand-gold/50"></div>

                        <Step
                            number={1}
                            icon={<ApplicationIcon className="w-12 h-12" />}
                            title="Preencha a Candidatura"
                            description="Use o nosso formulário online para submeter o seu pedido. Precisamos de algumas informações básicas sobre si e sobre o seu projecto. Leva apenas alguns minutos."
                            delay="0s"
                        />

                        <Step
                            number={2}
                            icon={<ApprovalIcon className="w-12 h-12" />}
                            title="Aprovação Rápida"
                            description="A nossa equipa analisa a sua candidatura de forma eficiente. Na maioria dos casos, receberá uma resposta dentro de 24 horas. Valorizamos o seu tempo."
                            delay="0.2s"
                        />

                        <Step
                            number={3}
                            icon={<FundsIcon className="w-12 h-12" />}
                            title="Receba os Fundos"
                            description="Após a aprovação, o dinheiro é depositado diretamente na sua conta. Rápido e seguro, para que possa começar a trabalhar nos seus objectivos imediatamente."
                            delay="0.4s"
                        />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default HowItWorks;
