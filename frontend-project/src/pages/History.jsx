import React, { useEffect, useState } from "react";
import { djangoAPI } from "../api/axios.jsx";
import {toast} from "react-hot-toast";
import { HistoryIcon, TrashIcon, EditAltIcon, ChevronLeftSquareIcon} from "../icons/index.jsx";
import { Link } from "react-router-dom";


export const MyHistory = () => {

    const [history, setHistory] = useState([])
    const [selectedUser, setSelectedUser] = useState(null);
    const [ userHistoryToEdit, setUserHisoryToEdit] = useState(null);
    const [ newComment, setNewComment] = useState("");

    const getHistory = async () => {
        try {
          const response = await djangoAPI.get(`/users/history-users/`);
          setHistory(response.data);
        } catch (error) {
          console.error(error);
        }
      };

      const colorData = (isApproved) => {
        console.log("aprobado:" + isApproved)
        if (isApproved) {
          return "border border-gray-300 bg-green-100 hover:bg-blue-100"
        }else{
          return "border border-gray-300  bg-gray-100 hover:bg-blue-100"
        }
      }
      
      const getHistoryUserDetails = async (userId) => {
        try {
          const response = await djangoAPI.get(`/users/whatsapp-users/${userId}/`);
          setSelectedUser(response.data);
        } catch (error) {
          console.error(error);
        }
      };

      const commentStart = (historyRecord) => {
        setUserHisoryToEdit(historyRecord.id)
        setNewComment(historyRecord.comments)
      }

      
      const saveComment = async(userHistoryId) => {
        try {
          await djangoAPI.patch(`/users/history-users/${userHistoryId}/` , {
            "comments" : newComment,
          })
          setUserHisoryToEdit(null)
          setNewComment("")
          toast.success("Se guardo el comentario")
        } catch (error) {
          console.error(error)
        }
      }
      
      const confirmDelete = (historyUserid, whatsappUserId) => {
        if (window.confirm("Esta usted seguro de eliminar completa y parcialmente la postulación del usuario ?")) {
            deleteUserHistory(historyUserid, whatsappUserId)
        }
      }

      const deleteUserHistory = async(historyUserid, whatsappUserId) => {
        try {
            await djangoAPI.delete(`users/history-users/${historyUserid}/`)
            await djangoAPI.delete(`users/whatsapp-users/${whatsappUserId}/`)
            toast.success("Se borraron todos los datos del usuario")
            getHistory();
        } catch (error) {
            toast.error("No se puedo borrar el usuario " + error)
        }
    }

      useEffect(() => {
        getHistory();
      }, [newComment]);

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
          <h1 className="text-[#1F3361] font-bold text-4xl mb-2 flex justify-center "> <HistoryIcon className="m-2 items-center"/> Archivo  </h1>
          <Link to="/applicants-user/" className="text-[#1F3361] cursor-pointer hover:bg-[#1F3361] hover:text-white font-bold transition duration-300 bg-white inline-flex p-2 border border-gray-300 m-2">
            <ChevronLeftSquareIcon/> 
            Volver a postulantes 
          </Link>
          <form action="">
          <table className="bg-white border border-gray-300 rounded w-full">
            <thead className="text-[#989da7] text-xs text-left font-medium bg-[#f9fafb] sticky top-0 left-0">
              <tr className="border-b border-t border-gray-300 p-2 ">
                <th className="p-2">Ver usuario</th>
                <th className="p-2">Comentarios</th>
                <th className="p-2"> Restaurar postulación </th>
                <th className="p-2">Fecha</th>
                <th> Acciones </th>
              </tr>
            </thead>
            <tbody >
              {history.map((record) => (
                <tr key={record.id} className={colorData(record.approved)}>
                  {userHistoryToEdit === record.id ?  (
                    <>
                    <td className="p-2">
                      <button type="button" onClick={() => {getHistoryUserDetails(record.user) }}> Ver datos </button>
                    </td>
                    <td>
                      <input className="border-dashed border-2 border-gray-800 bg-gray-200 p-1 rounded w-full" 
                        type="text" value={newComment} onChange={(e) => setNewComment(e.target.value)} 
                      />
                    </td>
                    <td> </td>
                    <td> </td>
                    <td className="p-2">
                      <button type="submit" onClick={(e) => { e.preventDefault() ;
                         saveComment(record.id)}}> Guardar 
                      </button>
                    </td>
                    </>
                  ) : (
                    <>
                    <td className="p-2">
                      <button type="button" onClick={() => getHistoryUserDetails(record.user)}> Ver datos </button>
                    </td>
                    <td className="p-2">{record.comments}</td>
                    <td>
                       <button type="button" className="cursor-pointer hover:underline" 
                        onClick={() => restoreUser(record.user , record.id)}>
                        Restaurar
                      </button>
                    </td>
                    <td>{new Date(record.date).toLocaleString()}</td>
                    <td > 
                    <div className="flex ">
                      <TrashIcon className="cursor-pointer" 
                        onClick={() => confirmDelete(record.id, record.user)}
                      />
                      <EditAltIcon className="cursor-pointer" 
                        onClick={() => {commentStart(record)}} />
                    </div>
                  </td>
                  </>
                  ) }

                </tr>
              ))}
            </tbody>
          </table>
          </form>
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