import React, { createContext, useContext, useEffect, useState } from 'react';
import { djangoAPI } from '../api/axios.jsx';
import { useNavigate } from 'react-router-dom';
import toast from "react-hot-toast";

const AdminContext = createContext()

export const useAdmin =  () => {
    return useContext(AdminContext)
}

const AdminProvider = ({ children }) => {
    
    let navigate = useNavigate()

    const [user, setUser] = useState({
        username: "",
        role: "",   
        isLogged: false
    });
    
    useEffect(() => {
        console.log("se recrago la pagina")
        const userSession =  JSON.parse(sessionStorage.getItem("user"))
        const token = sessionStorage.getItem("token");
    
        if (userSession && token) {
            setUser({
                username: userSession.username,
                role: userSession.username == "admin" ? "admin" : "user",
                isLogged: true
            });
        }
    }, []);
    

    const logout = async () => {
        try {
            await djangoAPI.post("users/logout/");

            sessionStorage.clear(); //Limpiar los datos que pudieron haber quedado en sessionStorage

            toast.success("Sesión cerrada" )
            navigate("/");
        } catch (error) {
            console.error(error.response?.data);
            toast.error("No se pudo cerrar sesión.");
        }
    }

    return(
        <AdminContext.Provider value={{ logout, user, setUser }}>
            {children}
        </AdminContext.Provider>
    )

}

export default AdminProvider;