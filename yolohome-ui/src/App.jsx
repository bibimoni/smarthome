import { router } from '@routes/AppRoutes.jsx'
import { RouterProvider } from 'react-router-dom'
import { AuthProvider } from './context/authContext'

function App() {
   return (
      <AuthProvider>
         <RouterProvider router={router} />
      </AuthProvider>
   )
}

export default App
