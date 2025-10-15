
import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from '../../components/dashboard/sidebar/Sidebar';

const AdminDashboard: React.FC = () => {
    return (
        <div className="flex h-screen bg-gray-100">
            <div className="flex-shrink-0">
                <Sidebar />
            </div>
            <main className="flex-grow p-6 overflow-y-auto">
                <div className="min-h-full">
                    <Outlet />
                </div>
            </main>
        </div>
    );
};

export default AdminDashboard;
