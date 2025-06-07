import { Routes, Route, useLocation } from "react-router-dom";
import { Login } from "../pages/Login.jsx";
import { DashboardAdmin } from "../admin/DashboardAdmin.jsx";
import { MessagesBilly } from "../admin/MessagesBilly.jsx";
import { Sedes } from "../pages/Sedes.jsx";
import { Toaster } from 'react-hot-toast';
import AdminProvider from '../context/UserContext.jsx';
import { MessageProvider } from "../context/MessageContext.jsx";
import { AnimatePresence, motion } from 'framer-motion';
import { Dashboard } from "../pages/Dashboard.jsx";
import { MessagesWhatsapp } from "../pages/MessagesWhatsapp.jsx";
import { Applicants } from "../pages/Applicants.jsx";
import { MyHistory } from "../pages/History.jsx";

function AppRoutes() {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">

      <AdminProvider>
        <MessageProvider>
        <Toaster 
          position="top-center"
          toastOptions={{
            style: {
              backgroundColor: '#222',
              padding: '16px',
              color: 'white',
              boxShadow: '0 0 6px rgba(0, 0, 0, 0.1)',
              width: '300px',
              fontWeight: 'bold',
            },
          }}
        />{/* Rutas de la aplicacion */} 
        <Routes location={location} key={location.pathname}>  {/* Esto permite que Framer Motion detecte cuándo cambia la ruta y aplique animaciones.*/}
          <Route path="/" element={ 
            <motion.div
              initial={{ opacity: 0, x: -100 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 100 }}
              transition={{ duration: 0.8 }}
            >
              <Login />
            </motion.div>
          }/>

          <Route path="dashboard/" element={ <DashboardAdmin /> } /> 

          <Route path="dashboard-user/" element={ <Dashboard /> } /> 

          <Route  path="messages-template-user/" element={<MessagesWhatsapp /> } />

          <Route path="applicants-user/" element ={ <Applicants /> } />

          <Route path="history-user/" element={<MyHistory />}/>

          <Route path="messages/" element={
            <motion.div
                initial ={{opacity: 0, x: -100}}
                animate ={{opacity: 1, x: 0}}
                exit={{opacity: 0, x: 100}}
                transition={{duration: 0.5}}
            >
                <MessagesBilly />
            </motion.div>
            } />
            <Route path="sedes/" element={
                <motion.div 
                    initial ={{opacity: 0, x: -100}}
                    animate ={{opacity: 1, x: 0}}
                    exit={{opacity: 0, x: 100}}
                    transition={{duration: 0.5}}
                >
                    <Sedes />
                </motion.div>
            } />
        </Routes>
        </MessageProvider>
      </AdminProvider>
    </AnimatePresence>
  );
}

export default AppRoutes ;
