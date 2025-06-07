import React, { useEffect, useState } from "react";
import { djangoAPI } from "../api/axios.jsx";
import {toast} from "react-hot-toast";

export const MyHistory = () => {

    const [history, setHistory] = useState([])
    const [selectedUser, setSelectedUser] = useState(null);

    const getHistory = async () => {
        try {
          const response = await djangoAPI.get(`/users/history-users/`);
          setHistory(response.data);
        } catch (error) {
          console.error(error);
        }
      };
      
      const getHistoryUserDetails = async (userId) => {
        try {
          const response = await djangoAPI.get(`/users/whatsapp-users/${userId}/`);
          setSelectedUser(response.data);
        } catch (error) {
          console.error(error);
        }
      };

      useEffect(() => {
        getHistory();
      }, []);
      
      const restoreUser = async (userId, historyId) => {
        try {
          await djangoAPI.patch(`/users/whatsapp-users/${userId}/`, {
            archived: false,
            approved: false,
          });
          await djangoAPI.delete(`/users/history-users/${historyId}/`);
          toast.success("Postulante restaurado correctamente");
          getHistory();

        } catch (error) {
          console.error(error);
          toast.error("No se pudo restaurar el postulante");
        }
      };
      
      return (
        <div className="bg-[#f3f4f6] w-full h-dvh p-2">
          <h1 className="text-[#1F3361] font-bold text-4xl mb-2 flex items-center"> Historial </h1>
          <table className="bg-white border border-gray-300 rounded w-full">
            <thead className="text-[#989da7] text-xs text-left font-medium bg-[#f9fafb] sticky top-0 left-0">
              <tr className="border-b border-t border-gray-300 p-2 ">
                <th className="p-2">Ver usuario</th>
                <th className="p-2">Comentarios</th>
                <th className="p-2"> Restaurar postulación </th>
                <th className="p-2">Fecha</th>
              </tr>
            </thead>
            <tbody >
              {history.map((record) => (
                <tr key={record.id}>
                  <td className="p-2">
                    <button onClick={() => getHistoryUserDetails(record.user)}>
                      Ver datos
                    </button>
                  </td>
                  <td className="p-2">{record.comments}</td>
                  <td>
                    <button className="cursor-pointer hover:underline" 
                     onClick={() => restoreUser(record.user , record.id)}>
                      Restaurar
                    </button>
                  </td>
                  <td>{new Date(record.date).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
      
          {selectedUser && (
            <div className="mt-4 p-4 border rounded bg-white">
              <h2 className="text-[#1F3361] font-bold text-2xl mb-2 flex items-center"> Datos del Usuario </h2>
              <div className="flex flex-wrap gap-5 ">
                 <p className="bg-gray-100 p-2 inline-block rounded-lg"> <strong> Nombre </strong> {selectedUser.name} </p>
                 <p className="bg-gray-100 p-2 inline-block rounded-lg"> <strong> Telefono </strong> {selectedUser.phone_number} </p>
                 <p className="bg-gray-100 p-2 inline-block rounded-lg"> <strong> Documento </strong> {selectedUser.document} </p>
                 <p className="bg-gray-100 p-2 inline-block rounded-lg"> <strong> Municipio </strong> {selectedUser.municipality} </p>
                 <p className="bg-gray-100 p-2 inline-block rounded-lg"> <strong> Dirección </strong> {selectedUser.address} </p>
                 <p className="bg-gray-100 p-2 inline-block rounded-lg"> <strong> Experiencia </strong> {selectedUser.experience} </p>
                 <p className="bg-gray-100 p-2 inline-block rounded-lg"> <strong> Trabajo </strong> {selectedUser.work_type} </p>
                 <p className="bg-gray-100 p-2 inline-block rounded-lg"> <strong> Aprobado </strong> {selectedUser.approved ? "Sí" : "No"} </p>
                 <p className="bg-gray-100 p-2 inline-block rounded-lg"> <strong> Archivado </strong> {selectedUser.archived ? "Sí" : "No"} </p>
              </div>
            </div>
          )}
        </div>
      );
      
}  