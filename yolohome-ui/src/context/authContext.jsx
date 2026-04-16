import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isLogged, setIsLogged] = useState(!!localStorage.getItem('access_token'));

  // Hàm này sẽ được gọi sau khi gọi API login thành công
  const login = (access_token) => {
    localStorage.setItem('access_token', access_token);
    setIsLogged(true);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setIsLogged(false);
  };

  return (
    <AuthContext.Provider value={{ isLogged, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);