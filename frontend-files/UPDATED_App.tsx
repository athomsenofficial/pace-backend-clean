import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from '@/shared/components/layout'
import { Dashboard, InitialMEL, FinalMEL, HowTo } from '@/pages'
import { DocumentGenerator } from '@/pages/DocumentGenerator'
import { TestSupabase } from './TestSupabase'

function App() {

  // Mock login for development - DISABLED for simplified version
  // useEffect(() => {
  //   if (!isAuthenticated) {
  //     mockLogin('editor') // Change to 'admin' or 'super_admin' to test different roles
  //   }
  // }, [isAuthenticated])

  return (
    <BrowserRouter>
      <Routes>
        {/* Main App Routes with Layout */}
        <Route path="/" element={<Layout><Dashboard /></Layout>} />
        <Route path="/initial-mel" element={<Layout><InitialMEL /></Layout>} />
        <Route path="/final-mel" element={<Layout><FinalMEL /></Layout>} />
        <Route path="/how-to" element={<Layout><HowTo /></Layout>} />
        <Route path="/document-generator" element={<Layout><DocumentGenerator /></Layout>} />

        {/* Hidden Routes - Temporarily disabled */}
        {/* <Route path="/memo-generator" element={<Layout><MemoGenerator /></Layout>} /> */}
        {/* <Route path="/reports" element={<Layout><Reports /></Layout>} /> */}
        {/* <Route path="/settings" element={<Layout><Settings /></Layout>} /> */}
        {/* <Route path="/account" element={<Layout><Account /></Layout>} /> */}

        {/* Admin Routes - Protected */}
        {/* <Route
          path="/admin"
          element={
            hasPermission('admin') ? (
              <Layout><AdminDashboard /></Layout>
            ) : (
              <Navigate to="/" replace />
            )
          }
        /> */}

        {/* Test Route (without layout) */}
        <Route path="/test-supabase" element={<TestSupabase />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
