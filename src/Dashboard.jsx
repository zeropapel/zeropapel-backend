import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  FileText, 
  Upload, 
  CheckCircle, 
  Clock, 
  TrendingUp,
  Shield,
  Users,
  BarChart3
} from 'lucide-react';
import { documentsAPI, auditAPI } from '../../lib/api';
import { useAuth } from '../../hooks/useAuth.jsx';

export const Dashboard = ({ onNavigate }) => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalDocuments: 0,
    signedDocuments: 0,
    pendingDocuments: 0,
    recentActivity: []
  });
  const [auditStats, setAuditStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // Fetch documents
        const documentsResponse = await documentsAPI.getDocuments({ per_page: 100 });
        const documents = documentsResponse.data.documents || [];
        
        // Calculate stats
        const totalDocuments = documents.length;
        const signedDocuments = documents.filter(doc => doc.status === 'signed').length;
        const pendingDocuments = documents.filter(doc => doc.status === 'pending').length;
        
        setStats({
          totalDocuments,
          signedDocuments,
          pendingDocuments,
          recentActivity: documents.slice(0, 5) // Last 5 documents
        });

        // Fetch audit stats
        try {
          const auditResponse = await auditAPI.getAuditStats({ days: 30 });
          setAuditStats(auditResponse.data);
        } catch (auditError) {
          console.error('Error fetching audit stats:', auditError);
        }

      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'signed':
        return 'text-green-600 bg-green-100';
      case 'pending':
        return 'text-yellow-600 bg-yellow-100';
      case 'uploaded':
        return 'text-blue-600 bg-blue-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'signed':
        return 'Assinado';
      case 'pending':
        return 'Pendente';
      case 'uploaded':
        return 'Enviado';
      default:
        return status;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">
          Bem-vindo, {user?.email}!
        </h1>
        <p className="text-blue-100">
          Gerencie seus documentos e assinaturas digitais de forma segura e eficiente.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Total de Documentos
            </CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalDocuments}</div>
            <p className="text-xs text-muted-foreground">
              Documentos na plataforma
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Documentos Assinados
            </CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.signedDocuments}</div>
            <p className="text-xs text-muted-foreground">
              Assinaturas concluídas
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Pendentes
            </CardTitle>
            <Clock className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats.pendingDocuments}</div>
            <p className="text-xs text-muted-foreground">
              Aguardando assinatura
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Limite Gratuito
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {user?.free_documents_signed || 0}/5
            </div>
            <p className="text-xs text-muted-foreground">
              Documentos assinados
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Ações Rápidas</CardTitle>
          <CardDescription>
            Acesse rapidamente as funcionalidades principais
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button 
              onClick={() => onNavigate('upload')}
              className="h-20 flex flex-col space-y-2"
            >
              <Upload className="h-6 w-6" />
              <span>Enviar Documento</span>
            </Button>
            
            <Button 
              variant="outline"
              onClick={() => onNavigate('documents')}
              className="h-20 flex flex-col space-y-2"
            >
              <FileText className="h-6 w-6" />
              <span>Meus Documentos</span>
            </Button>
            
            <Button 
              variant="outline"
              onClick={() => onNavigate('audit')}
              className="h-20 flex flex-col space-y-2"
            >
              <Shield className="h-6 w-6" />
              <span>Auditoria</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Atividade Recente</CardTitle>
            <CardDescription>
              Seus documentos mais recentes
            </CardDescription>
          </CardHeader>
          <CardContent>
            {stats.recentActivity.length > 0 ? (
              <div className="space-y-3">
                {stats.recentActivity.map((doc) => (
                  <div key={doc.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <FileText className="h-4 w-4 text-gray-500" />
                      <div>
                        <p className="text-sm font-medium truncate max-w-48">
                          {doc.filename}
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(doc.created_at).toLocaleDateString('pt-BR')}
                        </p>
                      </div>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(doc.status)}`}>
                      {getStatusText(doc.status)}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <FileText className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>Nenhum documento encontrado</p>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="mt-2"
                  onClick={() => onNavigate('upload')}
                >
                  Enviar primeiro documento
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Audit Summary */}
        {auditStats && (
          <Card>
            <CardHeader>
              <CardTitle>Resumo de Auditoria</CardTitle>
              <CardDescription>
                Últimos 30 dias
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Total de logs</span>
                  <span className="font-medium">{auditStats.total_logs}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Documentos enviados</span>
                  <span className="font-medium">{auditStats.documents_uploaded}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Documentos assinados</span>
                  <span className="font-medium">{auditStats.documents_signed}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Solicitações enviadas</span>
                  <span className="font-medium">{auditStats.signature_requests_sent}</span>
                </div>
              </div>
              
              <Button 
                variant="outline" 
                size="sm" 
                className="w-full mt-4"
                onClick={() => onNavigate('audit')}
              >
                <BarChart3 className="h-4 w-4 mr-2" />
                Ver relatório completo
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

