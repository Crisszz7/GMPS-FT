import React, { useActionState } from "react";
import { djangoAPI } from "../api/axios.jsx";
import {
  ArrowToBottomStrokeIcon, FileDetailIcon, FileXIcon, 
  UserCheckIcon, UserXIcon, EditAltIcon, HistoryIcon, 
  ArchiveIcon
} from "../icons/index.jsx";
import { toast } from "react-hot-toast";
import { useState } from "react";
import { Link } from "react-router-dom";

export const TableComponent = ({ applicants }) => { 
  console.log(applicants)
  const [selectedApplicants, setSelectedApplicants] = useState([]);
  const [search, setSearch] = useState("");

  const filteredUsers = applicants.filter(applicant => 
    applicant.work_type.toLowerCase().includes(search.toLocaleLowerCase()) ||
    applicant.municipality.toLowerCase().includes(search.toLocaleLowerCase())  &&
    !applicant.archived && !applicant.approved
  )


  const user = JSON.parse(sessionStorage.getItem("user"))


  const updateUserStatus = async (applicantID, approvedValue) => {
    try {
      await djangoAPI.patch(`/users/whatsapp-users/${applicantID}/`, {
        approved: approvedValue,
        archived: true, 
      });
      toast.success("Postulante actualizado correctamente");
    } catch (error) {
      console.error(error);
      toast.error("No se pudo actualizar el estado del postulante");
    }
  };
  
  const createHistory = async(applicantID) => {
    try {
      await djangoAPI.post(`/users/history-users/`, {
        "user": applicantID,
        "comments": "",
      })
      toast.success("Se archivo al usuario")
    } catch (error) {
      console.error(error);
      toast.error("No se pudo crear el historial")
    }
  }


  const buttonSendApproved = async(applicantID, approved, place) => {
    console.log("aprovado", approved)
    console.log("place", place)
    try {
      await djangoAPI.post(`/messages/send_approved/`, {
        "applicant": applicantID,
        "approved": approved,
        "place": place,
      })
      toast.success("Se envio el mensaje correctamente")
    } catch (error) {
      console.error(error) 
    }

  }

  const [applicantToEdit, setApplicantToEdit] = useState(null)
  const [newNombre, setNewNombre] = useState("")
  const [newDocumento, setNewDocumento] = useState("")
  const [newTelefono, setNewTelefono] = useState("")
  const [newExperiencia, setNewExperiencia] = useState("")
  const [newDireccion, setNewDireccion] = useState("")
  const [newMunicipio, setNewMunicipio] = useState("")
  
  
  const replaceNumberToWhatsapp = (number) => {
    const newNumber = number.replace("whatsapp:+", "")
    return newNumber
  }
  
  const typeWorkClassName = (workType) => {
    if(workType === "Dato no encontrado -IA"){
      return "text-red-500 p-2 font-bold bg-red-100 rounded-full text-xs max-w-auto";
    }if (workType == "Campo") {
      return "text-green-800 p-2 font-bold bg-green-100 rounded-full text-xs max-w-auto";
    }else if (workType == "Poscosecha") {
      return "text-blue-800 p-2 font-bold bg-blue-100 rounded-full text-xs max-w-auto";
    }else if(workType == "No especificado") {
      return "text-gray-800 p-2 font-bold bg-gray-100 rounded-full text-xs max-w-auto";
    } else {
      return "text-purple-800 p-2 font-bold bg-purple-100 rounded-full text-xs max-w-auto";
    }
  }

  const withAsksClassName = (state) => {
    if(state === "En asesoria") {
      return "text-purple-800 p-2 font-bold bg-purple-100 rounded-full text-xs max-w-auto ";
    }else {
      return 
    }
  }

  const startEdit = (applicant) => {
    setApplicantToEdit(applicant.id)
    setNewNombre(applicant.name)
    setNewDocumento(applicant.document)
    setNewTelefono(applicant.phone_number)
    setNewExperiencia(applicant.experience)
    setNewDireccion(applicant.address)
    setNewMunicipio(applicant.municipality)
  }

  const SaveEditApplicant = async(id) => {
    console.log({
      id,
      name: newNombre,
      document: newDocumento,
      phone_number: newTelefono,
      experience: newExperiencia,
      address: newDireccion,
      municipality: newMunicipio
    });
    

    if (!newNombre || !newDocumento || !newTelefono || !newExperiencia || !newDireccion || !newMunicipio) {
      toast.error("Por favor completa todos los campos.");
      return;
    }
    try {
      await djangoAPI.put(`/users/whatsapp-users/${id}/`, {
        "name": newNombre,
        "document": newDocumento,
        "phone_number": newTelefono,
        "experience": newExperiencia,
        "address": newDireccion,
        "municipality": newMunicipio 
      })

      toast.success("Postulante editado")
      setApplicantToEdit(null)
      setNewNombre("")
      setNewDocumento("")
      setNewTelefono("")
      setNewExperiencia("")
      setNewDireccion("")
      setNewMunicipio("")
    } catch (error) {
      console.log(error.response?.data || error.message);
      toast.error("Error al guardar el postulante");
    }
  }

  const alertClassName = (Nombre, Documento, Telefono, Experiencia, Direccion, Municipio) => {
    let isEmpty = [Nombre, Documento, Telefono, Experiencia, Direccion, Municipio]
    for (let index = 0; index < isEmpty.length; index++) {
      const element = isEmpty[index];
      if(element === null || element === undefined || element === "") {
        return "p-2  bg-orange-100 rounded";
      }
    }
  }

  const sendToOtherBranch = async(data) => {
    data.preventDefault()
    try {
      const checkboxes = data.target.querySelectorAll('input[name="selectedApplicant"]:checked');
      const selectedApplicants = Array.from(checkboxes).map(checkbox => checkbox.value);

      if (selectedApplicants.length === 0) {
        alert("Por favor, selecciona al menos un postulante")
        return
      }

      await djangoAPI.post("/users/changue-applicant-place/", {
        "applicants": selectedApplicants,
        "place": data.target.selectOtherPlace.value
      })
      toast.success("Se enviaron correctamente los postulantes")
    } catch (error) {
      console.log(error)
    }
  }

  const downloadExcel = async(data) => {
    data.preventDefault()
    try {
      const checkboxes = document.querySelectorAll('input[name="selectedApplicant"]:checked');
      const selectedApplicants = Array.from(checkboxes).map(checkbox => checkbox.value);
      
      console.log(selectedApplicants)

      if (selectedApplicants.length === 0) {
        alert("Por favor, selecciona al menos un postulante")
        return
      }

      const response = await djangoAPI.post(
        "/users/download-applicants/",
        { applicants: selectedApplicants },
        { responseType: 'blob' }
      );

      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      });

      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'Postulantes.xlsx';
      link.click();
      URL.revokeObjectURL(url);

      console.log(response)
    } catch (error) {
      console.log(error)
    }

  }

  return (
    <div className="overflow-y-auto w-full p-4 ">
      <Link to="/history-user/" className="w-10 h-10 absolute top-10 right-10 cursor-pointer bg-white border border-gray-300 p-2 rounded-full hover:bg-[#1F3361] hover:text-[#FFD40A] transition-all duration-300 " >
        <HistoryIcon applicant={applicants} />
      </Link>
      <div className="w-full flex h-auto p-3 gap-4 bg-white rounded-t-md text-black text-xs">
        <div className="flex items-center  ">
          <span className="bg-red-100 p-2 rounded-full"></span>
          <p className="ml-2  "> Datos No encontrados</p>
        </div>
        <div className="flex items-center">
          <span className="bg-orange-100 p-2 rounded-full"></span>
          <p className="ml-2"> Faltan Datos </p>
        </div>
      </div>
      <form onSubmit={sendToOtherBranch} className="bg-white border-t border-gray-300">
      <input className=" text-sm p-1 border border-gray-400 rounded-lg m-2 bg-gray-100" type="search" name="" value={search} id="" placeholder="Buscar " onChange={(e) => setSearch(e.target.value)}/>
        <select name="selectOtherPlace" id="" className="border-b border-gray-300 ">
          <option value={0}> ... </option>
          <option value={1}> Aguas Claras</option>
          <option value={2}> Caribe </option>
          <option value={3}> Manantiales </option>
          <option value={4}> Olas </option>
        </select>
        <button className="p-2 border border-gray-400 rounded-lg text-sm m-2 bg-white text-neutral-900 cursor-pointer hover:text-blue-900 hover:bg-blue-100 transition-all duration-300" type="submit"> Enviar a otra sede </button>
       <button type="button" className="p-2 border border-gray-400 rounded-lg m-2 text-sm text-neutral-900 bg-white cursor-pointer hover:text-green-900 hover:bg-green-100 transition-all duration-300" onClick={downloadExcel}> Descargar como Excel </button>
        <div className="max-h-96 overflow-y-auto relative">
          <table className="min-w-full bg-white rounded-md ">
          <thead className="text-[#989da7] text-xs text-left font-medium bg-[#f9fafb] sticky top-0 left-0">
            <tr className="border-b border-t border-gray-300 p-2 ">
              <th className="p-2"><input type="checkbox" className="checkbox-[#1f3361]" 
               onChange={(e) => {
                if (e.target.checked) {
                  setSelectedApplicants(applicants.map(app => app.id));
                } else {
                  setSelectedApplicants([]);
                }
              }}/></th>
              <th className="p-2">LABOR</th>
              <th className="p-2">Estado</th>
              <th className="p-2">WHATSAPP ORIGEN</th>
              <th className="p-2">NOMBRE</th>
              <th className="p-2">DOCUMENTO</th>
              <th className="p-2">EXPERIENCIA</th>
              <th className="p-2">MUNICIPIO - CIUDAD</th>
              <th className="p-2">DIRECCION</th>
              <th className="p-2"><FileDetailIcon/> </th>
              <th className="p-2">ACCIONES</th>
            </tr>
          </thead>
          <tbody >
          {filteredUsers.map(applicant => (
              <>
              {applicantToEdit === applicant.id  ? (
                <tr key={applicant.id} className=" hover:bg-blue-50 transition-all duration-300 text-sm p-2">
                  <td> </td>
                  <td></td>
                  <td></td>
                  <td> <input className="border border-gray-400 p-2 border-dashed" type="text" value={newTelefono} onChange={(e) => setNewTelefono(e.target.value)} /></td>
                  <td> <input className="border border-gray-400 p-2 border-dashed" type="text" value={newNombre} onChange={(e) => setNewNombre(e.target.value)} /></td>
                  <td> <input className="border border-gray-400 p-2 border-dashed" type="text" value={newDocumento} onChange={(e) => setNewDocumento(e.target.value)} /></td>
                  <td> <input className="border border-gray-400 p-2 border-dashed" type="text" value={newExperiencia} onChange={(e) => setNewExperiencia(e.target.value)} /></td>
                  <td> <input className="border border-gray-400 p-2 border-dashed" type="text" value={newMunicipio} onChange={(e) => setNewMunicipio(e.target.value)} /></td>
                  <td> <input className="border border-gray-400 p-2 border-dashed" type="text" value={newDireccion} onChange={(e) => setNewDireccion(e.target.value)} /></td>
                  <td> <button type="button" className="p-2 border border-gray-400 rounded-lg text-sm m-2 bg-white text-neutral-900 cursor-pointer hover:text-blue-900 hover:bg-blue-100 transition-all duration-300"
                  onClick={(e) => {e.preventDefault()
                    SaveEditApplicant(applicant.id)}}
                  > Guardar </button></td>
                  </tr>
              ) : (applicant.archived !== true && applicant.approved !== true) ? (
                <tr key={applicant.id} className={alertClassName(applicant.name, applicant.document, applicant.phone_number, applicant.experience, applicant.address, applicant.municipality) + " hover:bg-blue-50 transition-all duration-300 text-sm p-2" } >
                  <>
                  <td className="p-2 border-b border-gray-300">
                      <input className="checkbox" type="checkbox" name="selectedApplicant" id="" value={applicant.id} 
                      checked={selectedApplicants.includes(applicant.id)}
                        onChange={(e) => {
                          const id = applicant.id;
                          if (e.target.checked) {
                            setSelectedApplicants(prev => [...prev, id]);
                          } else {
                            setSelectedApplicants(prev => prev.filter(item => item !== id));
                          }
                        }} />
                  </td>
                  <td className="border-b p-2 border-gray-300"><p className={typeWorkClassName(applicant.work_type)}>{applicant.work_type}</p></td>
                  <td className="border-b p-2 border-gray-300"><p className={withAsksClassName(applicant.state)}>{applicant.state}</p></td>
                  <td className="border-b p-2 border-gray-300"><a className=" p-2 cursor-pointer hover:underline" href={"https://wa.me/" + replaceNumberToWhatsapp(applicant.phone_number)}
                  target="_blank"
                  rel="noopener noreferrer"
                  >{replaceNumberToWhatsapp(applicant.phone_number)}</a></td>
                  <td className="border-b p-2 border-gray-300 font-semibold">{applicant.name}</td>
                  <td className="border-b p-2 border-gray-300 ">{applicant.document}</td> 
                  <td className="border-b p-2 border-gray-300 ">{applicant.experience}</td>
                  <td className="border-b p-2 border-gray-300 ">{applicant.municipality}</td>
                  <td className="border-b p-2 border-gray-300">{applicant.address}</td>
                  <td className=" border-b border-gray-300 ">
                    <a href={applicant.cv_full_url} target="_blank" rel="noopener noreferrer" className=" ">
                      {applicant.cv_full_url ? <ArrowToBottomStrokeIcon className="text-blue-500 border rounded p-1 hover:bg-blue-500 hover:text-white transition-all duration-300 "/>
                      : <FileXIcon className="text-gray-300 cursor-not-allowed "/>
                      }
                    </a>
                  </td>
                  <td className=" p-2 border-b border-gray-300">
                    <div className="flex justify-between gap-3">
                      <UserCheckIcon className="bg-white rounded-full border border-gray-400 p-1  hover:bg-green-100 transition-all duration-300 cursor-pointer" 
                        onClick={(e) => {e.preventDefault();     
                        buttonSendApproved(applicant.id, true, applicant.place_to_work); 
                        createHistory(applicant.id)
                        updateUserStatus(applicant.id, true)}} />
                      <UserXIcon className="bg-white rounded-full border border-gray-400 p-1  hover:bg-red-100 transition-all duration-300 cursor-pointer" 
                        onClick={(e) => {e.preventDefault(); 
                        buttonSendApproved(applicant.id, false, applicant.place_to_work); 
                        createHistory(applicant.id)
                        updateUserStatus(applicant.id, false)}}/>
                      <ArchiveIcon className="bg-white rounded-full border border-gray-400 p-1  hover:bg-yellow-100 transition-all duration-300 cursor-pointer"
                        onClick={(e) => {e.preventDefault() ;
                        createHistory(applicant.id)
                        updateUserStatus(applicant.id, false)
                        }}
                        />
                      <EditAltIcon className="bg-white rounded-full border border-gray-400 p-1  hover:bg-blue-100 transition-all duration-300 cursor-pointer" 
                      onClick={() => startEdit(applicant) }
                       />
                    </div>
                  </td>
                  </>
              </tr>
                ) : (
                  <>
                  </>
                )}
            </>
          ))}
          </tbody>
        </table>
        </div>
      </form>
    </div>
  );
};