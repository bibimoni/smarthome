import { createBrowserRouter } from 'react-router-dom'

import ProtectedRoute from './ProtectedRoutes'
import MainLayout from '@components/layout/MainLayout.jsx'
import Unauthorized from '@pages/common/Unauthorized.jsx'

import Register from '@pages/Authentication/Register.jsx'
import Login from '@pages/Authentication/Login.jsx'
import ForgetPassword from '@pages/Authentication/ForgetPassword.jsx'
import Home from '@pages/Menu/Home.jsx'
import Dashboard from '@pages/Menu/Dashboard.jsx'
import ThresholdConfig from '@pages/Menu/ThresholdConfig.jsx'
import DeviceControl from '@pages/Menu/DeviceControl.jsx'
import ActivityHistory from '@pages/Menu/ActivityHistory.jsx'
import SceneList from '@pages/Scene/SceneList.jsx'
import SceneCreate from '@pages/Scene/SceneCreate.jsx'

export const router = createBrowserRouter([
   {
      path: '/',
      element: <MainLayout />,
      children: [
         { index: true, element: <Home /> },
         { path: 'unauthorized', element: <Unauthorized /> },
         { path: 'register', element: <Register /> },
         { path: 'login', element: <Login /> },
         { path: 'forget-password', element: <ForgetPassword /> },
         {
            element: <ProtectedRoute />,
            children: [
               {
                  // path: '/user',
                  children: [
                     { path: 'dashboard', element: <Dashboard /> },
                     { path: 'thresholds', element: <ThresholdConfig /> },
                     { path: 'device-control', element: <DeviceControl /> },
                     { path: 'activity-history', element: <ActivityHistory /> },
                     { path: 'scenes', element: <SceneList /> },
                     { path: 'scenes/create', element: <SceneCreate /> },
                     { path: 'scenes/:id/edit', element: <SceneCreate /> },
                  ],
               },
            ],
         },
      ],
   },
])
