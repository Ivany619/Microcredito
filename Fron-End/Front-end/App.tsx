
import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';

// Import Components
import Header from './components/Header';
import Footer from './components/Footer';

// Import Pages
import Home from './pages/Home';
import About from './pages/About';
import Services from './pages/Services';
import HowItWorks from './pages/HowItWorks';
import Simulator from './pages/Simulator';
import Contact from './pages/Contact';
import AdminLogin from './pages/admin/AdminLogin';
import AdminDashboard from './pages/dashboard/AdminDashboard';
import GestaoClientes from './pages/dashboard/clientes/GestaoClientes';
import GestaoEmprestimos from './pages/dashboard/emprestimos/GestaoEmprestimos';
import GestaoPagamentos from './pages/dashboard/pagamentos/GestaoPagamentos';
import Notificacoes from './pages/dashboard/notificacoes/Notificacoes';
import AnaliseCredito from './pages/dashboard/analise-credito/AnaliseCredito';
import Cobrancas from './pages/dashboard/cobrancas/Cobrancas';
import Relatorios from './pages/dashboard/relatorios/Relatorios';
import Configuracoes from './pages/dashboard/configuracoes/Configuracoes';

// Layout para páginas públicas que incluem Header e Footer
const PublicLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <div className="bg-brand-gray min-h-screen flex flex-col font-sans text-gray-800">
        <Header />
        <main className="flex-grow">
            {children}
        </main>
        <Footer />
    </div>
);

// Componente de verificação de autenticação para a rota de admin
const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const isAdmin = sessionStorage.getItem('isAdmin') === 'true';
    return isAdmin ? <>{children}</> : <Navigate to="/admin/login" />;
};


const App: React.FC = () => {
    return (
        <Router>
            <Routes>
                {/* Rotas Públicas */}
                <Route path="/" element={<PublicLayout><Home /></PublicLayout>} />
                <Route path="/about" element={<PublicLayout><About /></PublicLayout>} />
                <Route path="/services" element={<PublicLayout><Services /></PublicLayout>} />
                <Route path="/how-it-works" element={<PublicLayout><HowItWorks /></PublicLayout>} />
                <Route path="/simulator" element={<PublicLayout><Simulator /></PublicLayout>} />
                <Route path="/contact" element={<PublicLayout><Contact /></PublicLayout>} />

                {/* Rotas de Admin */}
                <Route path="/admin/login" element={<AdminLogin />} />
                <Route
                    path="/admin/dashboard"
                    element={
                        <PrivateRoute>
                            <AdminDashboard />
                        </PrivateRoute>
                    }
                >
                    <Route index element={<Navigate to="clientes" />} />
                    <Route path="clientes" element={<GestaoClientes />} />
                    <Route path="emprestimos" element={<GestaoEmprestimos />} />
                    <Route path="pagamentos" element={<GestaoPagamentos />} />
                    <Route path="notificacoes" element={<Notificacoes />} />
                    <Route path="analise-credito" element={<AnaliseCredito />} />
                    <Route path="cobrancas" element={<Cobrancas />} />
                    <Route path="relatorios" element={<Relatorios />} />
                    <Route path="configuracoes" element={<Configuracoes />} />
                </Route>

                {/* Redirecionar para home se a rota não for encontrada */}
                <Route path="*" element={<Navigate to="/" />} />
            </Routes>
        </Router>
    );
};

export default App;
