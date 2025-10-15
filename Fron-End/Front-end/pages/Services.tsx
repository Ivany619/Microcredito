
import React from 'react';
import { GrowthIcon } from '../components/icons/GrowthIcon';
import { PersonalIcon } from '../components/icons/PersonalIcon';
import { AgricultureIcon } from '../components/icons/AgricultureIcon';

const ServiceCard: React.FC<{ icon: React.ReactNode; title: string; description: string; }> = ({ icon, title, description }) => (
    <div className="bg-white rounded-lg shadow-lg p-8 text-center hover:shadow-xl transition-shadow duration-300 transform hover:-translate-y-1">
        <div className="flex items-center justify-center h-20 w-20 rounded-full bg-brand-blue text-white mx-auto mb-6">
            {icon}
        </div>
        <h3 className="text-2xl font-bold text-brand-blue-dark mb-4">{title}</h3>
        <p className="text-gray-600">{description}</p>
    </div>
);

const Services: React.FC = () => {
  return (
    <div className="bg-gray-50 py-20 animate-fade-in">
        <div className="container mx-auto px-6">
            <div className="text-center mb-16">
                <h1 className="text-5xl font-extrabold text-brand-blue-dark">Os Nossos Serviços de Crédito</h1>
                <p className="text-xl text-gray-600 mt-4 max-w-3xl mx-auto">
                    Soluções financeiras pensadas para as necessidades específicas do mercado Moçambicano.
                </p>
            </div>
            
            <div className="grid md:grid-cols-3 gap-10">
                <ServiceCard 
                    icon={<GrowthIcon className="w-10 h-10" />} 
                    title="Crédito para Negócios"
                    description="Ideal para expandir o seu stock, comprar novo equipamento, ou investir em marketing. Dê ao seu negócio o impulso que ele precisa para crescer."
                />
                <ServiceCard 
                    icon={<AgricultureIcon className="w-10 h-10" />} 
                    title="Crédito Agrícola"
                    description="Financiamento para a compra de sementes, fertilizantes, e equipamento. Apoiamos os agricultores a garantir uma colheita próspera e sustentável."
                />
                <ServiceCard 
                    icon={<PersonalIcon className="w-10 h-10" />} 
                    title="Crédito Pessoal"
                    description="Para objectivos pessoais como formação, melhorias na habitação, ou para fazer face a despesas inesperadas. Uma ajuda para a sua estabilidade."
                />
            </div>

            <div className="mt-20 bg-brand-blue-dark text-white p-10 rounded-xl shadow-2xl text-center">
                <h2 className="text-4xl font-extrabold text-brand-gold mb-4">Taxa de Juro Transparente</h2>
                <p className="text-2xl font-bold mb-2">
                    Todos os nossos empréstimos têm uma taxa de juro fixa de <span className="text-brand-gold text-4xl">20%</span>.
                </p>
                <p className="text-lg text-gray-300 max-w-4xl mx-auto">
                    Sem custos escondidos, sem complicações. Acreditamos que a transparência é a base da confiança. O valor que simula é o valor que paga.
                </p>
            </div>
        </div>
    </div>
  );
};

export default Services;
