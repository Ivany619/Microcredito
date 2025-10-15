
import React, { useState, useMemo } from 'react';

// Icons
import { GrowthIcon } from '../components/icons/GrowthIcon';
import { CommunityIcon } from '../components/icons/CommunityIcon';
import { SpeedIcon } from '../components/icons/SpeedIcon';
import { BaobabIcon } from '../components/icons/BaobabIcon';
import { ShieldIcon } from '../components/icons/ShieldIcon';
import { PersonalIcon } from '../components/icons/PersonalIcon';
import { AgricultureIcon } from '../components/icons/AgricultureIcon';
import { ApplicationIcon } from '../components/icons/ApplicationIcon';
import { ApprovalIcon } from '../components/icons/ApprovalIcon';
import { FundsIcon } from '../components/icons/FundsIcon';
import { Financial3DIcon } from '../components/icons/Financial3DIcon';
import { CalendarIcon } from '../components/icons/CalendarIcon';
import { InfoIcon } from '../components/icons/InfoIcon';


// Reusable components previously on separate pages
const FeatureCard: React.FC<{ icon: React.ReactNode; title: string; children: React.ReactNode; delay: string }> = ({ icon, title, children, delay }) => (
    <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 ease-in-out animate-fade-in-up" style={{ animationDelay: delay }}>
        <div className="flex items-center justify-center h-16 w-16 rounded-full bg-brand-blue-light text-white mb-6">
            {icon}
        </div>
        <h3 className="text-2xl font-bold text-brand-blue-dark mb-3">{title}</h3>
        <p className="text-gray-600">{children}</p>
    </div>
);

const ValueCard: React.FC<{icon: React.ReactNode, title: string, text: string}> = ({ icon, title, text }) => (
    <div className="flex items-start space-x-4">
        <div className="flex-shrink-0 text-brand-blue">{icon}</div>
        <div>
            <h3 className="text-xl font-bold text-brand-blue-dark">{title}</h3>
            <p className="text-gray-600 mt-1">{text}</p>
        </div>
    </div>
);

const ServiceCard: React.FC<{ icon: React.ReactNode; title: string; description: string; }> = ({ icon, title, description }) => (
    <div className="bg-white rounded-lg shadow-lg p-8 text-center hover:shadow-xl transition-shadow duration-300 transform hover:-translate-y-1">
        <div className="flex items-center justify-center h-20 w-20 rounded-full bg-brand-blue text-white mx-auto mb-6">
            {icon}
        </div>
        <h3 className="text-2xl font-bold text-brand-blue-dark mb-4">{title}</h3>
        <p className="text-gray-600">{description}</p>
    </div>
);

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

const Home: React.FC = () => {
    const [amount, setAmount] = useState<number>(25000);
    const [months, setMonths] = useState<number>(12);
    const INTEREST_RATE = 0.20;

    const { totalRepayment, monthlyPayment } = useMemo(() => {
        const total = amount * (1 + INTEREST_RATE);
        const monthly = total / months;
        return { totalRepayment: total, monthlyPayment: monthly };
    }, [amount, months]);

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('pt-MZ', { style: 'currency', currency: 'MZN' }).format(value);
    };

    const [formState, setFormState] = useState({ name: '', email: '', message: '' });
    const [submitted, setSubmitted] = useState(false);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setFormState(prevState => ({ ...prevState, [name]: value }));
    };

    const contactEmail = 'LacosMicrocredito@gmail.co.mz';
    
    const mailtoHref = useMemo(() => {
        const subject = `Contacto do site Lacos Microcrédito - De: ${formState.name}`;
        const body = `Nome: ${formState.name}\nEmail para resposta: ${formState.email}\n\nMensagem:\n${formState.message}`;
        return `mailto:${contactEmail}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    }, [formState]);

    const isFormValid = useMemo(() => {
        return formState.name.trim() !== '' && formState.email.trim() !== '' && formState.message.trim() !== '';
    }, [formState]);
    
    const handleSendMessageClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
        if (!isFormValid) {
            e.preventDefault();
        } else {
            setSubmitted(true);
        }
    };

    const handleResetForm = () => {
        setFormState({ name: '', email: '', message: '' });
        setSubmitted(false);
    };

    const handleLinkClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
        e.preventDefault();
        document.querySelector(href)?.scrollIntoView({ behavior: 'smooth' });
    };

  return (
    <div className="animate-fade-in">
      <section 
        id="inicio"
        className="relative bg-brand-blue-dark text-white py-20 md:py-32"
        style={{backgroundImage: "url('https://images.unsplash.com/photo-1593113598332-cd288d649414?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D')", backgroundSize: 'cover', backgroundPosition: 'center' }}
      >
        <div className="absolute inset-0 bg-brand-blue-dark opacity-70"></div>
        <div className="container mx-auto px-6 text-center relative z-10">
          <h1 className="text-4xl md:text-6xl font-extrabold mb-4 animate-fade-in-up">
            Impulsionando Sonhos, <br />
            <span className="text-brand-gold">Construindo Futuros em Moçambique.</span>
          </h1>
          <p className="text-lg md:text-xl max-w-3xl mx-auto mb-8 animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
            Crédito rápido, justo e transparente para alavancar o seu negócio e os seus projectos pessoais.
          </p>
          <div className="animate-fade-in-up" style={{ animationDelay: '0.6s' }}>
            <a 
              href="#simulador" 
              onClick={(e) => handleLinkClick(e, '#simulador')}
              className="bg-brand-gold text-brand-blue-dark font-bold py-4 px-8 rounded-full text-lg hover:bg-yellow-400 transition-transform transform hover:scale-105 duration-300 shadow-lg"
            >
              Simule o seu Empréstimo
            </a>
          </div>
        </div>
      </section>

      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-6">
            <div className="text-center mb-12">
                <h2 className="text-4xl font-extrabold text-brand-blue-dark">Porquê a Lacos Microcrédito?</h2>
                <p className="text-lg text-gray-600 mt-4 max-w-2xl mx-auto">Somos mais que um empréstimo, somos o seu parceiro de crescimento.</p>
            </div>
            <div className="grid md:grid-cols-3 gap-10">
                <FeatureCard icon={<GrowthIcon />} title="Crescimento" delay="0s">
                    Oferecemos o capital que precisa para expandir o seu negócio, comprar equipamento ou investir em novas oportunidades.
                </FeatureCard>
                <FeatureCard icon={<CommunityIcon />} title="Comunidade" delay="0.2s">
                    O nosso sucesso está ligado ao sucesso das comunidades que servimos. Investimos em pessoas e no potencial local.
                </FeatureCard>
                <FeatureCard icon={<SpeedIcon />} title="Rapidez e Confiança" delay="0.4s">
                    Processo de candidatura simplificado com aprovação rápida para que não perca nenhuma oportunidade.
                </FeatureCard>
            </div>
        </div>
      </section>
      
      <section id="sobre" className="bg-white py-20">
        <div className="container mx-auto px-6">
            <div className="text-center mb-16">
                <BaobabIcon className="w-20 h-20 mx-auto text-brand-blue-dark mb-4"/>
                <h2 className="text-5xl font-extrabold text-brand-blue-dark">Sobre a Lacos Microcrédito</h2>
                <p className="text-xl text-gray-600 mt-4 max-w-3xl mx-auto">
                    Fortalecendo as raizes da nossa comunidade, um empréstimo de cada vez.
                </p>
            </div>
            <div className="grid md:grid-cols-2 gap-16 items-center">
                <div className="flex items-center justify-center min-h-[300px] md:min-h-full">
                    <Financial3DIcon className="w-64 h-64 text-brand-gold animate-float" />
                </div>
                <div>
                    <h3 className="text-3xl font-bold text-brand-blue-dark mb-4">A Nossa Missão</h3>
                    <p className="text-lg text-gray-700 mb-6">
                        A nossa missão é ser o principal catalisador de crescimento económico para micro e pequenos empreendedores em Moçambique. Acreditamos no poder do capital para transformar vidas, negócios e comunidades inteiras. A Lacos Microcrédito existe para criar laços de confiança e prosperidade, oferecendo acesso a serviços financeiros de forma justa, transparente e digna.
                    </p>
                    <h3 className="text-3xl font-bold text-brand-blue-dark mb-4">A Nossa Visão</h3>
                    <p className="text-lg text-gray-700">
                        Visualizamos um Moçambique onde cada empreendedor, independentemente do seu ponto de partida, tem as ferramentas e o apoio necessários para construir um futuro sustentável. Queremos ser reconhecidos não apenas como uma instituição financeira, mas como um pilar de desenvolvimento comunitário.
                    </p>
                </div>
            </div>
            <div className="py-20 mt-16 bg-gray-50 rounded-xl">
                 <div className="text-center mb-12">
                    <h3 className="text-4xl font-extrabold text-brand-blue-dark">Os Nossos Valores</h3>
                    <p className="text-lg text-gray-600 mt-4 max-w-2xl mx-auto">Os princípios que guiam cada decisão que tomamos.</p>
                </div>
                <div className="grid md:grid-cols-3 gap-10 max-w-6xl mx-auto">
                    <ValueCard icon={<CommunityIcon className="w-10 h-10"/>} title="Empoderamento" text="Capacitamos os nossos clientes com recursos financeiros e confiança para que alcancem a sua independência." />
                    <ValueCard icon={<ShieldIcon className="w-10 h-10"/>} title="Integridade" text="Operamos com total transparência e honestidade. As nossas taxas são claras e sem surpresas." />
                    <ValueCard icon={<GrowthIcon className="w-10 h-10"/>} title="Parceria" text="Vemos cada cliente como um parceiro. O seu crescimento é o nosso objectivo final e celebramos cada sucesso." />
                </div>
            </div>
        </div>
      </section>

      <section id="servicos" className="bg-gray-50 py-20">
        <div className="container mx-auto px-6">
            <div className="text-center mb-16">
                <h2 className="text-5xl font-extrabold text-brand-blue-dark">Os Nossos Serviços de Crédito</h2>
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
                <h3 className="text-4xl font-extrabold text-brand-gold mb-4">Taxa de Juro Transparente</h3>
                <p className="text-2xl font-bold mb-2">
                    Todos os nossos empréstimos têm uma taxa de juro fixa de <span className="text-brand-gold text-4xl">20%</span>.
                </p>
                <p className="text-lg text-gray-300 max-w-4xl mx-auto">
                    Sem custos escondidos, sem complicações. Acreditamos que a transparência é a base da confiança. O valor que simula é o valor que paga.
                </p>
            </div>
        </div>
      </section>

      <section id="como-funciona" className="bg-white py-20">
            <div className="container mx-auto px-6">
                <div className="text-center mb-16">
                    <h2 className="text-5xl font-extrabold text-brand-blue-dark">Como Funciona</h2>
                    <p className="text-xl text-gray-600 mt-4 max-w-3xl mx-auto">
                        Obter o seu empréstimo é um processo simples, rápido e transparente. Siga estes 3 passos.
                    </p>
                </div>
                <div className="max-w-3xl mx-auto">
                    <div className="relative space-y-12">
                        <div className="absolute left-6 top-6 bottom-6 w-0.5 bg-brand-gold/50" aria-hidden="true"></div>
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
        </section>

      <section id="simulador" className="bg-gray-50 py-20">
        <div className="container mx-auto px-6">
            <div className="text-center mb-16">
                <h2 className="text-5xl font-extrabold text-brand-blue-dark">Simulador de Crédito</h2>
                <p className="text-xl text-gray-600 mt-4 max-w-3xl mx-auto">
                    Planeie o seu futuro. Veja como um empréstimo da Lacos pode caber no seu orçamento de forma transparente.
                </p>
            </div>
            <div className="max-w-5xl mx-auto bg-white rounded-2xl shadow-2xl p-8 md:p-12">
                <div className="grid lg:grid-cols-2 gap-12">
                    {/* Controls */}
                    <div className="space-y-10">
                        <div>
                            <div className="flex items-center justify-between mb-4">
                                <label htmlFor="amount" className="text-lg font-semibold text-gray-700 flex items-center gap-2">
                                    <FundsIcon className="w-6 h-6 text-brand-blue"/>
                                    Valor do Empréstimo
                                </label>
                                <span className="text-2xl font-bold text-brand-blue">
                                    {formatCurrency(amount)}
                                </span>
                            </div>
                            <input
                                type="range"
                                id="amount"
                                min="1000"
                                max="100000"
                                step="1000"
                                value={amount}
                                onChange={(e) => setAmount(Number(e.target.value))}
                                className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer range-lg accent-brand-blue"
                                aria-label="Valor do Empréstimo"
                            />
                             <div className="flex justify-between text-sm text-gray-500 mt-2">
                                <span>1.000 MZN</span>
                                <span>100.000 MZN</span>
                            </div>
                        </div>
                        <div>
                           <div className="flex items-center justify-between mb-4">
                                <label htmlFor="months" className="text-lg font-semibold text-gray-700 flex items-center gap-2">
                                    <CalendarIcon className="w-6 h-6 text-brand-blue"/>
                                    Prazo de Pagamento
                                </label>
                                <span className="text-2xl font-bold text-brand-blue">
                                    {months} meses
                                </span>
                            </div>
                            <input
                                type="range"
                                id="months"
                                min="3"
                                max="36"
                                step="1"
                                value={months}
                                onChange={(e) => setMonths(Number(e.target.value))}
                                className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer range-lg accent-brand-blue"
                                aria-label="Prazo de Pagamento"
                            />
                            <div className="flex justify-between text-sm text-gray-500 mt-2">
                                <span>3 meses</span>
                                <span>36 meses</span>
                            </div>
                        </div>
                        <div className="bg-brand-blue/10 p-4 rounded-lg flex items-start gap-4">
                            <InfoIcon className="w-6 h-6 text-brand-blue flex-shrink-0 mt-1" />
                            <div>
                                <h4 className="font-bold text-brand-blue-dark">Taxa de Juro Transparente</h4>
                                <p className="text-sm text-gray-700 mt-1">
                                    A nossa taxa de juro é <strong>fixa em 20%</strong> para todos os empréstimos. Sem custos escondidos, sem surpresas. O valor que simula é o valor que paga.
                                </p>
                            </div>
                        </div>
                    </div>
                    {/* Results */}
                    <div className="space-y-6">
                        <h3 className="text-2xl font-bold text-brand-blue-dark text-center lg:text-left">Resultado da Simulação</h3>
                        <div className="bg-brand-blue-dark text-white rounded-xl p-6 text-center shadow-lg transform hover:scale-105 transition-transform duration-300">
                             <p className="text-sm text-gray-300 mb-1">Prestação Mensal</p>
                             <p className="text-5xl font-extrabold text-brand-gold" aria-live="polite">
                                {formatCurrency(monthlyPayment)}
                            </p>
                        </div>
                         <div className="grid grid-cols-2 gap-4">
                            <div className="bg-gray-100 p-4 rounded-lg text-center hover:shadow-md transition-shadow">
                                <p className="text-sm text-gray-600 mb-1">Taxa de Juro</p>
                                <p className="text-2xl font-bold text-brand-blue">20%</p>
                            </div>
                            <div className="bg-gray-100 p-4 rounded-lg text-center hover:shadow-md transition-shadow">
                                <p className="text-sm text-gray-600 mb-1">Total de Juros</p>
                                <p className="text-2xl font-bold text-brand-blue">{formatCurrency(amount * INTEREST_RATE)}</p>
                            </div>
                        </div>
                        <div className="bg-white border-2 border-gray-200 p-6 rounded-lg">
                            <div className="flex justify-between items-center mb-4">
                               <p className="font-semibold text-gray-700">Total a Pagar</p>
                               <p className="text-2xl font-bold text-brand-blue-dark">{formatCurrency(totalRepayment)}</p>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2.5 relative overflow-hidden">
                                <div className="absolute top-0 left-0 h-full bg-brand-blue" style={{ width: `${(amount / totalRepayment) * 100}%` }}></div>
                                <div className="absolute top-0 right-0 h-full bg-brand-gold" style={{ width: `${((amount * INTEREST_RATE) / totalRepayment) * 100}%` }}></div>
                            </div>
                            <div className="flex justify-between text-xs text-gray-500 mt-2">
                                <span><span className="inline-block w-2 h-2 rounded-full bg-brand-blue mr-1"></span>Valor: {formatCurrency(amount)}</span>
                                <span><span className="inline-block w-2 h-2 rounded-full bg-brand-gold mr-1"></span>Juros: {formatCurrency(amount * INTEREST_RATE)}</span>
                            </div>
                        </div>
                        <a 
                            href="#contacto"
                            onClick={(e) => handleLinkClick(e, '#contacto')}
                            className="w-full block text-center bg-brand-gold text-brand-blue-dark font-bold py-4 px-8 rounded-full text-lg hover:bg-yellow-400 transition-transform transform hover:scale-105 duration-300 shadow-lg"
                        >
                            Solicitar Este Crédito
                        </a>
                        <p className="text-xs text-center text-gray-500">
                            * Estes valores são apenas uma simulação. A aprovação final está sujeita a análise de crédito.
                        </p>
                    </div>
                </div>
            </div>
        </div>
      </section>

      <section id="contacto" className="bg-white py-20">
        <div className="container mx-auto px-6">
            <div className="text-center mb-12">
                <h2 className="text-5xl font-extrabold text-brand-blue-dark">Entre em Contacto</h2>
                <p className="text-xl text-gray-600 mt-4 max-w-3xl mx-auto">
                    Tem alguma questão? A nossa equipa está pronta para ajudar.
                </p>
            </div>
            <div className="grid md:grid-cols-2 gap-16">
                <div className="bg-gray-50 p-8 rounded-xl shadow-lg">
                    {submitted ? (
                        <div className="flex flex-col items-center justify-center h-full text-center py-10">
                            <h3 className="text-2xl font-bold text-brand-blue-dark mb-3">Obrigado pelo seu contacto!</h3>
                            <p className="text-gray-700 mb-6 max-w-sm">A sua aplicação de email foi aberta. Por favor, complete e envie a mensagem para nos contactar.</p>
                            <button
                                onClick={handleResetForm}
                                className="bg-brand-blue text-white font-bold py-3 px-6 rounded-lg hover:bg-brand-blue-dark transition-colors duration-300"
                            >
                                Escrever Outra Mensagem
                            </button>
                        </div>
                    ) : (
                        <form>
                            <div className="mb-6">
                                <label htmlFor="name-home" className="block text-gray-700 font-semibold mb-2">Nome Completo</label>
                                <input type="text" id="name-home" name="name" value={formState.name} onChange={handleChange} required className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-blue" />
                            </div>
                            <div className="mb-6">
                                <label htmlFor="email-home" className="block text-gray-700 font-semibold mb-2">Email</label>
                                <input type="email" id="email-home" name="email" value={formState.email} onChange={handleChange} required className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-blue" />
                            </div>
                            <div className="mb-6">
                                <label htmlFor="message-home" className="block text-gray-700 font-semibold mb-2">Mensagem</label>
                                <textarea id="message-home" name="message" value={formState.message} onChange={handleChange} required rows={5} className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-blue"></textarea>
                            </div>
                            <a 
                                href={isFormValid ? mailtoHref : undefined}
                                onClick={handleSendMessageClick}
                                className={`w-full block text-center font-bold py-3 px-6 rounded-lg transition-colors duration-300 ${
                                    isFormValid 
                                    ? 'bg-brand-blue text-white hover:bg-brand-blue-dark cursor-pointer' 
                                    : 'bg-gray-400 text-gray-100 cursor-not-allowed'
                                }`}
                                aria-disabled={!isFormValid}
                            >
                                Enviar Mensagem
                            </a>
                        </form>
                    )}
                </div>
                <div className="space-y-8">
                    <div>
                        <h3 className="text-2xl font-bold text-brand-blue-dark mb-2">O nosso Escritório</h3>
                        <p className="text-lg text-gray-700">Av. 25 de Setembro, Nº 1234</p>
                        <p className="text-lg text-gray-700">Maputo, Moçambique</p>
                    </div>
                    <div>
                        <h3 className="text-2xl font-bold text-brand-blue-dark mb-2">Contacto Direto</h3>
                        <p className="text-lg text-gray-700">Email: <a href="mailto:LacosMicrocredito@gmail.co.mz" className="text-brand-blue hover:underline">LacosMicrocredito@gmail.co.mz</a></p>
                        <p className="text-lg text-gray-700">Telefone: <a href="tel:+258875104607" className="text-brand-blue hover:underline">+258 87 510 4607</a></p>
                    </div>
                    <div>
                        <h3 className="text-2xl font-bold text-brand-blue-dark mb-2">Horário</h3>
                        <p className="text-lg text-gray-700">Segunda a Sexta: 08:00 - 17:00</p>
                        <p className="text-lg text-gray-700">Sábado: 09:00 - 13:00</p>
                    </div>
                </div>
            </div>
        </div>
      </section>

       <section className="bg-brand-blue text-white py-20">
        <div className="container mx-auto px-6 text-center">
          <h2 className="text-4xl font-extrabold mb-4">Pronto para dar o próximo passo?</h2>
          <p className="text-xl mb-8 max-w-3xl mx-auto">
            Veja como o nosso microcrédito pode transformar a sua visão em realidade. O processo é simples e rápido.
          </p>
           <a 
              href="#como-funciona"
              onClick={(e) => handleLinkClick(e, '#como-funciona')}
              className="bg-white text-brand-blue font-bold py-4 px-8 rounded-full text-lg hover:bg-gray-200 transition-transform transform hover:scale-105 duration-300 shadow-lg"
            >
            Descubra Como Funciona
          </a>
        </div>
      </section>
    </div>
  );
};

export default Home;