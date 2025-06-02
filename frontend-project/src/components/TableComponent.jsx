import React, { useState } from "react";
import { djangoAPI } from "../api/axios.jsx";
import {ArrowToBottomStrokeIcon, FileDetailIcon, FileXIcon, UserCheckIcon, UserXIcon} from "../icons/index.jsx";

export const TableComponent = ({ applicants }) => {

  const typeWorkClassName = (worType) => {
    if(worType === "Dato no encontrado -IA"){
      return "text-red-500 p-2 font-bold bg-red-100 rounded-full text-xs max-w-auto";
    }if (worType == "Campo") {
      return "text-green-800 p-2 font-bold bg-green-100 rounded-full text-xs max-w-auto";
    }else {
      return "text-blue-800 p-2 font-bold bg-blue-100 rounded-full text-xs max-w-auto";
    }
  }

  const withAsksClassName = (state) => {
    if(state === "En asesoria") {
      return "text-purple-800 p-2 font-bold bg-purple-100 rounded-full text-xs max-w-auto";
    }else {
      return "text-yellow-800 p-2 font-bold bg-yellow-100 rounded-full text-xs max-w-auto";
    }
  }

  const alertClassName = (Nombre, Documento, Telefono, Experiencia, Direccion) => {
    let isEmpty = [Nombre, Documento, Telefono, Experiencia, Direccion]
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

      await djangoAPI.post("/users/changue-applicant-place/", {
        "applicants": selectedApplicants,
        "place": data.target.selectOtherPlace.value
      })
    } catch (error) {
      console.log(error)
    }
  }

  return (
    <div className="overflow-y-auto w-full p-4 ">
      <div className="w-full flex h-auto p-3 gap-4  rounded-t-md text-black text-xs">
        <div className="flex items-center  ">
          <span className="bg-red-100 p-2 rounded-full"></span>
          <p className="ml-2  "> Datos No encontrados</p>
        </div>
        <div className="flex items-center">
          <span className="bg-orange-100 p-2 rounded-full"></span>
          <p className="ml-2"> Faltan Datos </p>
        </div>
      </div>
      <form onSubmit={sendToOtherBranch}>
        <select name="selectOtherPlace" id="">
          <option value={0}> ... </option>
          <option value={1}> Aguas Claras</option>
          <option value={2}> Caribe </option>
          <option value={3}> Manantiales </option>
          <option value={4}> Olas </option>
        </select>

        <button className="p-2 border rounded"> Enviar a otra sede </button>
      <table className="min-w-full bg-white rounded-md">
        <thead className="text-[#989da7] text-xs text-left font-medium bg-[#f9fafb]">
          <tr className="border-b border-t border-gray-300 p-2">
            <th className="p-2"><input type="checkbox" /></th>
            <th className="p-2">LABOR</th>
            <th className="p-2">Estado</th>
            <th className="p-2">NOMBRE</th>
            <th className="p-2">DOCUMENTO</th>
            <th className="p-2">TELEFONO</th>
            <th className="p-2">EXPERIENCIA</th>
            <th className="p-2">DIRECCION</th>
            <th className="p-2"><FileDetailIcon/> </th>
            <th className="p-2">ACCIONES</th>
          </tr>
        </thead>
        <tbody >
          {applicants.map((applicant) => (
            <tr key={applicant.id} className= {alertClassName(applicant.name, applicant.document, applicant.phone_number, applicant.experience, applicant.address) + " hover:bg-blue-50 transition-all duration-300 text-sm p-2" } >
              <td className="p-2 border-b border-gray-300">
                  <input type="checkbox" name="selectedApplicant" id="" value={applicant.id} />
              </td>
              <td className="border-b p-2 border-gray-300"><p className={typeWorkClassName(applicant.work_type)}>{applicant.work_type}</p></td>
              <td className="border-b p-2 border-gray-300"><p className={withAsksClassName(applicant.state)}>{applicant.state}</p></td>
              <td className="border-b p-2 border-gray-300 font-semibold">{applicant.name}</td>
              <td className="border-b p-2 border-gray-300 ">{applicant.document}</td>
              <td className="border-b p-2 border-gray-300">{applicant.phone_number}</td>
              <td className="border-b p-2 border-gray-300 ">{applicant.experience}</td>
              <td className="border-b p-2 border-gray-300">{applicant.address}</td>
              <td className=" border-b border-gray-300 ">
                <a href={applicant.cv_full_url} target="_blank" rel="noopener noreferrer" className=" ">
                  {applicant.cv_full_url ? <ArrowToBottomStrokeIcon className="text-blue-500 border rounded p-1 hover:bg-blue-500 hover:text-white transition-all duration-300 "/>
                  : <FileXIcon className="text-gray-300 cursor-not-allowed "/>
                  }
                </a>
              </td>
              <td className="flex justify-between p-3 border-b border-gray-300">
                <UserCheckIcon/>
                <UserXIcon/>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      </form>
    </div>
  );
};
