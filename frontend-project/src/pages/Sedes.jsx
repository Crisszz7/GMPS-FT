import { useEffect } from "react";
import { NavbarComponent } from "../components/NavbarComponent";
import { djangoAPI } from "../api/axios.jsx";
import { useState } from "react";
import sedesIMG from "../assets/imgs/sedesIMG.jpg";
import { useAdmin } from "../context/UserContext.jsx";

export const Sedes = () => {

    const [users, setUsers] = useState([])
    const [sedes, setSedes] = useState([]) 


    useEffect(() => {
        const getUsers = async () => {
            try {
                const response = await djangoAPI.get("/users/administer-users/")
                setUsers(response.data)
            } catch (error) {
                console.log(error)
            }
        }
        const getSedes = async () => {
            try {
                const response = await djangoAPI.get("/users/place-trigal-users/")
                setSedes(response.data)
            } catch (error) {
                console.log(error)
            }
        }
        getSedes()
        getUsers()
    }, [])



    const handleSubmit = async (e) => {
        e.preventDefault()
        try {
            const response = await djangoAPI.post("/users/administer-users/", {
                username: e.target.username.value,
                password: e.target.password.value,
                email: e.target.email.value,
                place_to_administer: e.target.place_to_administer.value
            })
            console.log(response)
        } catch (error) {
            console.error("Error al registrar sede:", error.response?.data || error.message);
        }
    }

    return (
        <div className="w-full h-full flex bg-[#f2f2f2] montserrat">
            <NavbarComponent />
            <div className="basis-full h-auto p-3 bg-[#f3f4f6]">
                <h1 className="text-4xl font-bold mb-4 text-[#1F3361]"> Sedes Trigal </h1>
                <h2 className="text-2xl font-bold mb-4 text-[#1F3361]"> Lista de sedes  </h2>
                <div className="w-full h-auto p-4 grid grid-cols-5 gap-4 ">
                    {sedes.map(sede => (
                        <>
                        {sede.name_place_trigal == "Trigal" ? (
                            null
                        ) : 
                        <div key={sede.id} className="bg-white p-2 max-h-max hover:scale-105 transition-all duration-300">
                            <img src={sedesIMG} alt="" className="object-cover w-full rounded-lg  "/>
                            <p className="font-bold "> {sede.name_place_trigal} </p>
                            <p> {users.map(user => user.place_to_administer == sede.id ? user.username : null)} </p>
                            <p> {users.map(user => user.place_to_administer == sede.id ? user.email : null)} </p>
                        </div>
                        }
                        </>
                        
                    ))}
                </div>
                <div>
                    <hr />
                     <p> formulario de registro de sede </p>
                     <form onSubmit={(e) => handleSubmit(e)} className="flex flex-col gap-2 bg-white"> 
                        <input type="text" name="username" placeholder="username" />
                        <input type="text" name="password" placeholder="password" />
                        <input type="text" name="email" placeholder="email" />
                        <select name="place_to_administer" id="" className="bg-blue-100 p-3">
                            {sedes.map((sede, index) => (
                                <option key={index} value={sede.id}> {sede.name_place_trigal} </option>
                            ))}
                        </select>
                        <button type="submit"> registrar </button>
                     </form>
                </div>
            </div>

        </div>
    )
}   