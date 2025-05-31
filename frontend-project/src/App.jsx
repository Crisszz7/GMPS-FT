import { BrowserRouter, Routes, Route, Navigate, Router, useLocation } from "react-router-dom";
import AppRoutes from "./routes/AppRoutes.jsx";

function App(){
  return(
    <BrowserRouter>
      <AppRoutes /> {/* Importacion de rutas (componente)*/}
    </BrowserRouter>
  
  )
}

export default App


  // const [users, SetUsers] = useState([])
  // //Funcion asincrona para esperar la respuesta de API en django 
  // useEffect(() => {
  //   const fetchData = async () => {
  //   try {
  //       const res = await djangoAPI.get('users/place-trigal-users/')
  //       SetUsers(res.data)
  //     } catch (error) {
  //     console.log((error));
  //   }
  // }
  //   fetchData()
  // }, [])