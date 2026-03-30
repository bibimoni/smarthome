import { createBrowserRouter, Navigate } from 'react-router-dom'

// Common --------------------------------------------------------------------------
import MainLayout from '@components/layout/MainLayout.jsx'
import Unauthorized from '@pages/common/Unauthorized.jsx'

// Authentication -------------------------------------------------------------------
import Register from '@pages/Authentication/Register.jsx'
import Login from '@pages/Authentication/Login.jsx'
import ForgetPassword from '@pages/Authentication/ForgetPassword.jsx'

// Scene (UC-5) --------------------------------------------------------------------
import SceneList from '@pages/Scene/SceneList.jsx'
import SceneCreate from '@pages/Scene/SceneCreate.jsx'

export const router = createBrowserRouter([
   {
      path: '/',
      element: <MainLayout />,
      children: [
         { path: 'unauthorized', element: <Unauthorized /> },
         { path: 'register', element: <Register /> },
         { path: 'login', element: <Login /> },
         { path: 'forget-password', element: <ForgetPassword /> },
         { path: 'scenes', element: <SceneList /> },
         { path: 'scenes/create', element: <SceneCreate /> },
      ],
   },
])
