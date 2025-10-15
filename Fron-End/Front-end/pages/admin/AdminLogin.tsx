import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BaobabIcon } from '../../components/icons/BaobabIcon';

const AdminLogin: React.FC = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        const isAdmin = sessionStorage.getItem('isAdmin') === 'true';
        if (isAdmin) {
            navigate('/admin/dashboard');
        }
    }, [navigate]);

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const response = await fetch('http://localhost:8000/api/auth/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: new URLSearchParams({
                    username,
                    password
                })
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('authToken', data.access_token);
                sessionStorage.setItem('isAdmin', 'true');
                navigate('/admin/dashboard');
            } else {
                setError('Credenciais inválidas. Tente novamente.');
            }
        } catch (err) {
            setError('Erro de conexão. Tente novamente.');
        }
    };

    return (
        <div className="relative min-h-screen bg-gray-100 flex items-center justify-center p-4 sm:p-6 lg:p-8">
            {/* Fundo com gradiente e formas */}
            <div className="absolute inset-0 bg-gradient-to-br from-brand-blue-dark via-blue-800 to-gray-900 opacity-95"></div>
            <div className="absolute top-0 left-0 w-64 h-64 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-50 animate-blob"></div>
            <div className="absolute bottom-0 right-0 w-64 h-64 bg-blue-400 rounded-full mix-blend-multiply filter blur-xl opacity-50 animate-blob animation-delay-2000"></div>

            <div className="relative w-full max-w-md p-8 space-y-6 bg-white/10 backdrop-blur-xl rounded-2xl shadow-2xl text-white border border-white/20">
                
                <div className="text-center">
                    <div className="flex justify-center mb-4">
                        <BaobabIcon width={70} height={70} />
                    </div>
                    <h1 className="text-3xl font-bold">Acesso Restrito</h1>
                    <p className="text-blue-100">Bem-vindo à área de administração.</p>
                </div>

                <form className="space-y-6" onSubmit={handleLogin}>
                    <div>
                        <label htmlFor="username" className="text-sm font-semibold text-blue-100">
                            Username
                        </label>
                        <input
                            id="username"
                            name="username"
                            type="text"
                            required
                            className="w-full px-4 py-3 mt-2 text-gray-800 bg-white/80 rounded-lg border-2 border-transparent focus:bg-white focus:border-blue-400 focus:outline-none transition duration-300"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="ivany.massinga"
                        />
                    </div>

                    <div>
                        <label htmlFor="password" className="text-sm font-semibold text-blue-100">
                            Password
                        </label>
                        <input
                            id="password"
                            name="password"
                            type="password"
                            required
                            className="w-full px-4 py-3 mt-2 text-gray-800 bg-white/80 rounded-lg border-2 border-transparent focus:bg-white focus:border-blue-400 focus:outline-none transition duration-300"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Sua senha"
                        />
                    </div>

                    {error && (
                        <div className="p-3 text-sm text-center text-red-200 bg-red-500/50 rounded-lg">
                            {error}
                        </div>
                    )}

                    <div>
                        <button
                            type="submit"
                            className="w-full px-4 py-3 font-bold text-white bg-brand-blue-dark rounded-lg shadow-lg hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-300 transition-all duration-300 ease-in-out transform hover:scale-105"
                        >
                            Login
                        </button>
                    </div>
                </form>
            </div>

            {/* Animação CSS para os blobs */}
            <style>{`
                .animate-blob {
                    animation: blob 7s infinite;
                }
                .animation-delay-2000 {
                    animation-delay: -2s;
                }
                @keyframes blob {
                    0% { transform: translate(0px, 0px) scale(1); }
                    33% { transform: translate(30px, -50px) scale(1.1); }
                    66% { transform: translate(-20px, 20px) scale(0.9); }
                    100% { transform: translate(0px, 0px) scale(1); }
                }
            `}</style>
        </div>
    );
};

export default AdminLogin;
