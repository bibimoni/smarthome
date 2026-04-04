import { createBrowserRouter } from 'react-router-dom'

import MainLayout from '@components/layout/MainLayout.jsx'
import Unauthorized from '@pages/common/Unauthorized.jsx'

import Register from '@pages/Authentication/Register.jsx'
import Login from '@pages/Authentication/Login.jsx'
import ForgetPassword from '@pages/Authentication/ForgetPassword.jsx'
import Home from '@pages/Menu/Home.jsx'
import Dashboard from '@pages/Menu/Dashboard.jsx'
import DeviceControl from '@pages/Menu/DeviceControl.jsx'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <MainLayout />,
    children: [
      { index: true, element: <Home /> },
      { path: 'dashboard', element: <Dashboard /> },
      { path: 'device-control', element: <DeviceControl /> },
      { path: 'unauthorized', element: <Unauthorized /> },
      { path: 'register', element: <Register /> },
      { path: 'login', element: <Login /> },
      { path: 'forget-password', element: <ForgetPassword /> },
    ],
  },
])
