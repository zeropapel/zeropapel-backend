import { Button } from '@/components/ui/button';
import { 
  FileText, 
  Upload, 
  Shield, 
  BarChart3, 
  Users,
  Settings,
  Home
} from 'lucide-react';
import { useAuth } from '../../hooks/useAuth.jsx';

export const Sidebar = ({ isOpen, currentPage, onNavigate, onClose }) => {
  const { user } = useAuth();

  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home },
    { id: 'documents', label: 'Meus Documentos', icon: FileText },
    { id: 'upload', label: 'Enviar Documento', icon: Upload },
    { id: 'audit', label: 'Auditoria', icon: Shield },
  ];

  // Admin-only items
  if (user?.is_admin) {
    navigationItems.push(
      { id: 'analytics', label: 'Relatórios', icon: BarChart3 },
      { id: 'users', label: 'Usuários', icon: Users },
      { id: 'settings', label: 'Configurações', icon: Settings }
    );
  }

  const handleNavigation = (pageId) => {
    onNavigate(pageId);
    onClose && onClose();
  };

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}
      
      {/* Sidebar */}
      <aside className={`
        fixed top-0 left-0 z-50 h-full w-64 bg-white border-r border-gray-200 transform transition-transform duration-300 ease-in-out
        lg:relative lg:translate-x-0 lg:z-auto
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center space-x-2 p-6 border-b border-gray-200">
            <FileText className="h-8 w-8 text-blue-600" />
            <h2 className="text-xl font-bold text-gray-900">ZeroPapel</h2>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentPage === item.id;
              
              return (
                <Button
                  key={item.id}
                  variant={isActive ? 'default' : 'ghost'}
                  className={`w-full justify-start ${
                    isActive 
                      ? 'bg-blue-600 text-white hover:bg-blue-700' 
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                  onClick={() => handleNavigation(item.id)}
                >
                  <Icon className="mr-3 h-4 w-4" />
                  {item.label}
                </Button>
              );
            })}
          </nav>

          {/* User info */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-medium">
                  {user?.email?.substring(0, 2).toUpperCase()}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {user?.email}
                </p>
                <p className="text-xs text-gray-500">
                  {user?.is_admin ? 'Administrador' : 'Usuário'}
                </p>
              </div>
            </div>
            
            {/* Usage info for non-admin users */}
            {!user?.is_admin && (
              <div className="mt-3 p-2 bg-gray-50 rounded-lg">
                <div className="flex justify-between text-xs text-gray-600">
                  <span>Documentos assinados</span>
                  <span>{user?.free_documents_signed || 0}/5</span>
                </div>
                <div className="mt-1 w-full bg-gray-200 rounded-full h-1.5">
                  <div 
                    className="bg-blue-600 h-1.5 rounded-full" 
                    style={{ 
                      width: `${Math.min(((user?.free_documents_signed || 0) / 5) * 100, 100)}%` 
                    }}
                  ></div>
                </div>
              </div>
            )}
          </div>
        </div>
      </aside>
    </>
  );
};

