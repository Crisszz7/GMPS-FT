import  axios  from "axios";

export const djangoAPI = axios.create({
    baseURL:"http://127.0.0.1:8000/api/",
    withCredentials: true
})

//interceptadores de axios
//Aca se carga automaticamente el token en cada petiicoion que se haga a la API 
djangoAPI.interceptors.request.use(
    (peticion) => {
        const token = sessionStorage.getItem("token")

        if (token){
            peticion.headers.Authorization = `Token ${token}` // Token registrado para enviar la petición 
        }

        return peticion
    },
    (error) => Promise.reject(error) // si la peticion falla 
)





