import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/common/Navbar';
import { Sidebar } from './components/common/Sidebar';
import { DashboardPage } from './pages/DashboardPage';
import { DocumentsPage } from './pages/DocumentsPage';
import { DocumentDetailPage } from './pages/DocumentDetailPage';
import { VerificationQueuePage } from './pages/VerificationQueuePage';
import { VerificationStudioPage } from './pages/VerificationStudioPage';
import { LandRecordsPage } from './pages/LandRecordsPage';
import { GISMapPage } from './pages/GISMapPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { AuditPage } from './pages/AuditPage';
import { LoginPage } from './pages/LoginPage';
import { DocumentItem, VerificationTask, AnalyticsDashboardData } from './types';
import { api } from './services/api';

const AppContent: React.FC = () => {
  const { user } = useAuth();

  // Navigation State
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [selectedDocId, setSelectedDocId] = useState<number | null>(null);
  const [selectedTaskId, setSelectedTaskId] = useState<number | null>(null);
  const [selectedRecordId, setSelectedRecordId] = useState<number | null>(null);
  const [focusSurveyNo, setFocusSurveyNo] = useState<string | undefined>(undefined);

  // Data state
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [tasks, setTasks] = useState<VerificationTask[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsDashboardData | null>(null);

  // Load app data
  const refreshData = async () => {
    try {
      const [docsData, tasksData, analyticsData] = await Promise.all([
        api.listDocuments(),
        api.listVerificationTasks('ALL'),
        api.getAnalyticsDashboard(),
      ]);
      setDocuments(docsData);
      setTasks(tasksData);
      setAnalytics(analyticsData);
    } catch (err) {
      console.error('Data refresh failed', err);
    }
  };

  useEffect(() => {
    if (user) {
      refreshData();
      const interval = setInterval(refreshData, 12000); // 12s polling
      return () => clearInterval(interval);
    }
  }, [user]);

  const pendingCount = tasks.filter((t) => t.status === 'PENDING').length;

  const navigateTo = (tab: string, param?: any) => {
    setSelectedDocId(null);
    setSelectedTaskId(null);
    if (tab === 'map' && typeof param === 'string') {
      setFocusSurveyNo(param);
    }
    if (tab === 'records' && typeof param === 'number') {
      setSelectedRecordId(param);
    } else if (tab === 'records' && !param) {
      setSelectedRecordId(null);
    }
    setActiveTab(tab);
  };

  const openDocumentDetail = (doc: DocumentItem) => {
    setSelectedDocId(doc.id);
  };

  const openVerificationStudio = (taskId: number) => {
    setSelectedTaskId(taskId);
  };

  // If user is not authenticated, display dedicated Login Page (Step 1 & 2)
  if (!user) {
    return <LoginPage onLoginSuccess={refreshData} />;
  }

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col selection:bg-emerald-500/30 selection:text-emerald-200">
      {/* Top Navigation */}
      <Navbar activeTab={activeTab} setActiveTab={navigateTo} />

      {/* Main Layout Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Persistent Sidebar */}
        <Sidebar
          activeTab={activeTab}
          setActiveTab={navigateTo}
          pendingCount={pendingCount}
        />

        {/* Scrollable Content Viewport */}
        <main className="flex-1 p-6 overflow-y-auto max-w-7xl mx-auto w-full">
          {/* Sub-view: Document Detail */}
          {selectedDocId !== null ? (
            <DocumentDetailPage
              documentId={selectedDocId}
              onBack={() => setSelectedDocId(null)}
              onNavigateToVerification={() => {
                setSelectedDocId(null);
                navigateTo('verification');
              }}
            />
          ) : selectedTaskId !== null ? (
            /* Sub-view: Verification Studio */
            <VerificationStudioPage
              taskId={selectedTaskId}
              onBack={() => setSelectedTaskId(null)}
              onVerifiedSuccess={() => {
                setSelectedTaskId(null);
                refreshData();
                navigateTo('records');
              }}
            />
          ) : activeTab === 'dashboard' ? (
            <DashboardPage
              analytics={analytics}
              recentDocs={documents}
              onNavigate={navigateTo}
              onOpenUpload={() => navigateTo('documents')}
            />
          ) : activeTab === 'documents' ? (
            <DocumentsPage
              documents={documents}
              onRefresh={refreshData}
              onSelectDocument={openDocumentDetail}
              onNavigateToVerification={() => navigateTo('verification')}
            />
          ) : activeTab === 'verification' ? (
            <VerificationQueuePage
              tasks={tasks}
              onSelectTask={openVerificationStudio}
              onRefresh={refreshData}
            />
          ) : activeTab === 'records' ? (
            <LandRecordsPage
              initialRecordId={selectedRecordId}
              onNavigateToMap={(sNo) => navigateTo('map', sNo)}
            />
          ) : activeTab === 'map' ? (
            <GISMapPage
              initialSurveyNo={focusSurveyNo}
              onNavigateToRecord={(recId) => navigateTo('records', recId)}
            />
          ) : activeTab === 'analytics' ? (
            <AnalyticsPage analytics={analytics} />
          ) : activeTab === 'audit' ? (
            <AuditPage />
          ) : (
            <DashboardPage
              analytics={analytics}
              recentDocs={documents}
              onNavigate={navigateTo}
              onOpenUpload={() => navigateTo('documents')}
            />
          )}
        </main>
      </div>
    </div>
  );
};

export function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
