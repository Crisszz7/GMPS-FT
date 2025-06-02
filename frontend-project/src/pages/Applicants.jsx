import { djangoAPI } from "../api/axios.jsx";
import { useState, useEffect } from "react";
import { NavbarComponent } from "../components/NavbarComponent.jsx";
import { TableComponent } from "../components/TableComponent.jsx";

export const Applicants = () => {
    const [applicants, setApplicants] = useState([]);
    const user = JSON.parse(sessionStorage.getItem("user"))

    const getApplicants = async () => {
        try {
            const response = await djangoAPI.get("users/whatsapp-users");
            setApplicants(response.data);
        } catch (error) {
            console.log(error);
        }
    };

    useEffect(() => {
        const fetchInitial = async () => {
            await getApplicants();
        };

        fetchInitial();

        const interval = setInterval(() => {
            getApplicants(); 
        }, 1000); 

        return () => clearInterval(interval); 
    }, []);

    return (
        <div className="flex montserrat">
            <NavbarComponent />
            <div className="w-full p-4 bg-[#f3f4f6]">
                <h1 className="text-4xl font-bold mb-4 text-[#1F3361]">Postulantes - {user.sede}</h1>
                <p className="text-gray-700 ">Postulantes que usaron el canal de <strong className="text-[#1F3361]">WhatsApp</strong> para aplicar a <strong>{user.sede}</strong></p>
                <TableComponent applicants={applicants} />
            </div>
        </div>
    );
};
