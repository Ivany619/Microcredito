
import React from 'react';
import { BaobabIcon } from '../components/icons/BaobabIcon';
import { CommunityIcon } from '../components/icons/CommunityIcon';
import { GrowthIcon } from '../components/icons/GrowthIcon';
import { ShieldIcon } from '../components/icons/ShieldIcon';

const ValueCard: React.FC<{icon: React.ReactNode, title: string, text: string}> = ({ icon, title, text }) => (
    <div className="flex items-start space-x-4">
        <div className="flex-shrink-0 text-brand-blue">{icon}</div>
        <div>
            <h3 className="text-xl font-bold text-brand-blue-dark">{title}</h3>
            <p className="text-gray-600 mt-1">{text}</p>
        </div>
    </div>
);


const About: React.FC = () => {
  return (
    <div className="bg-white animate-fade-in">
        <div className="container mx-auto px-6 py-16">
            <div className="text-center mb-16">
                <BaobabIcon className="w-20 h-20 mx-auto text-brand-blue-dark mb-4"/>
                <h1 className="text-5xl font-extrabold text-brand-blue-dark">Sobre a Lacos Microcrédito</h1>
                <p className="text-xl text-gray-600 mt-4 max-w-3xl mx-auto">
                    Fortalecendo as raizes da nossa comunidade, um empréstimo de cada vez.
                </p>
            </div>

            <div className="grid md:grid-cols-2 gap-16 items-center">
                <div>
                    <img 
                        src="https://picsum.photos/800/600?random=2" 
                        alt="Comunidade Moçambicana"
                        className="rounded-xl shadow-2xl"
                    />
                </div>
                <div>
                    <h2 className="text-3xl font-bold text-brand-blue-dark mb-4">A Nossa Missão</h2>
                    <p className="text-lg text-gray-700 mb-6">
                        A nossa missão é ser o principal catalisador de crescimento económico para micro e pequenos empreendedores em Moçambique. Acreditamos no poder do capital para transformar vidas, negócios e comunidades inteiras. A Lacos Microcrédito existe para criar laços de confiança e prosperidade, oferecendo acesso a serviços financeiros de forma justa, transparente e digna.
                    </p>
                    <h2 className="text-3xl font-bold text-brand-blue-dark mb-4">A Nossa Visão</h2>
                    <p className="text-lg text-gray-700">
                        Visualizamos um Moçambique onde cada empreendedor, independentemente do seu ponto de partida, tem as ferramentas e o apoio necessários para construir um futuro sustentável. Queremos ser reconhecidos não apenas como uma instituição financeira, mas como um pilar de desenvolvimento comunitário.
                    </p>
                </div>
            </div>

            <div className="py-20 mt-16 bg-gray-50 rounded-xl">
                 <div className="text-center mb-12">
                    <h2 className="text-4xl font-extrabold text-brand-blue-dark">Os Nossos Valores</h2>
                    <p className="text-lg text-gray-600 mt-4 max-w-2xl mx-auto">Os princípios que guiam cada decisão que tomamos.</p>
                </div>
                <div className="grid md:grid-cols-3 gap-10 max-w-6xl mx-auto">
                    <ValueCard icon={<CommunityIcon className="w-10 h-10"/>} title="Empoderamento" text="Capacitamos os nossos clientes com recursos financeiros e confiança para que alcancem a sua independência." />
                    <ValueCard icon={<ShieldIcon className="w-10 h-10"/>} title="Integridade" text="Operamos com total transparência e honestidade. As nossas taxas são claras e sem surpresas." />
                    <ValueCard icon={<GrowthIcon className="w-10 h-10"/>} title="Parceria" text="Vemos cada cliente como um parceiro. O seu crescimento é o nosso objectivo final e celebramos cada sucesso." />
                </div>
            </div>
        </div>
    </div>
  );
};

export default About;
