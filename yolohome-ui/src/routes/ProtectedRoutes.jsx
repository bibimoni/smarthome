import React from 'react'
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { getCurrentUser } from '@services/auth.service'; 

const ProtectedRoute = () => {
   const user = getCurrentUser(); // Hàm này check xem có Token/User trong localStorage không
   const location = useLocation();

   if (!user) {
      // Nếu không có user, đuổi ra trang login ngay
      return <Navigate to="/login" state={{ from: location }} replace />;
   }

   return <Outlet />;
};

export default ProtectedRoute