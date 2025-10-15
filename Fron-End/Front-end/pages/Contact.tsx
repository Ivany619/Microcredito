
import React, { useState } from 'react';

const Contact: React.FC = () => {
  const [formState, setFormState] = useState({ name: '', email: '', message: '' });
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormState(prevState => ({ ...prevState, [name]: value }));
  };
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Here you would typically handle form submission (e.g., API call)
    console.log('Form submitted:', formState);
    setSubmitted(true);
    setFormState({ name: '', email: '', message: '' });
  };
  
  return (
    <div className="bg-white py-20 animate-fade-in">
      <div className="container mx-auto px-6">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-extrabold text-brand-blue-dark">Entre em Contacto</h1>
          <p className="text-xl text-gray-600 mt-4 max-w-3xl mx-auto">
            Tem alguma questão? A nossa equipa está pronta para ajudar.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-16">
          {/* Contact Form */}
          <div className="bg-gray-50 p-8 rounded-xl shadow-lg">
            {submitted ? (
              <div className="flex flex-col items-center justify-center h-full text-center py-10">
                <h2 className="text-2xl font-bold text-brand-blue-dark mb-2">Obrigado!</h2>
                <p className="text-gray-700 mb-6">A sua mensagem foi enviada com sucesso. Entraremos em contacto em breve.</p>
                <button
                  onClick={() => setSubmitted(false)}
                  className="bg-brand-blue text-white font-bold py-3 px-6 rounded-lg hover:bg-brand-blue-dark transition-colors duration-300"
                >
                  Escrever Outra Mensagem
                </button>
              </div>
            ) : (
              <form onSubmit={handleSubmit}>
                <div className="mb-6">
                  <label htmlFor="name" className="block text-gray-700 font-semibold mb-2">Nome Completo</label>
                  <input type="text" id="name" name="name" value={formState.name} onChange={handleChange} required className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-blue" />
                </div>
                <div className="mb-6">
                  <label htmlFor="email" className="block text-gray-700 font-semibold mb-2">Email</label>
                  <input type="email" id="email" name="email" value={formState.email} onChange={handleChange} required className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-blue" />
                </div>
                <div className="mb-6">
                  <label htmlFor="message" className="block text-gray-700 font-semibold mb-2">Mensagem</label>
                  <textarea id="message" name="message" value={formState.message} onChange={handleChange} required rows={5} className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-blue"></textarea>
                </div>
                <button type="submit" className="w-full bg-brand-blue text-white font-bold py-3 px-6 rounded-lg hover:bg-brand-blue-dark transition-colors duration-300">
                  Enviar Mensagem
                </button>
              </form>
            )}
          </div>

          {/* Contact Info */}
          <div className="space-y-8">
            <div>
              <h3 className="text-2xl font-bold text-brand-blue-dark mb-2">O nosso Escritório</h3>
              <p className="text-lg text-gray-700">Av. 25 de Setembro, Nº 1234</p>
              <p className="text-lg text-gray-700">Maputo, Moçambique</p>
            </div>
             <div>
              <h3 className="text-2xl font-bold text-brand-blue-dark mb-2">Contacto Direto</h3>
              <p className="text-lg text-gray-700">Email: <a href="mailto:contacto@lacos.co.mz" className="text-brand-blue hover:underline">contacto@lacos.co.mz</a></p>
              <p className="text-lg text-gray-700">Telefone: <a href="tel:+258841234567" className="text-brand-blue hover:underline">+258 84 123 4567</a></p>
            </div>
            <div>
              <h3 className="text-2xl font-bold text-brand-blue-dark mb-2">Horário</h3>
              <p className="text-lg text-gray-700">Segunda a Sexta: 08:00 - 17:00</p>
              <p className="text-lg text-gray-700">Sábado: 09:00 - 13:00</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Contact;
