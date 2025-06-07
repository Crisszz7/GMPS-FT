import React, { useEffect, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend,
  BarElement
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { faker } from '@faker-js/faker';
import { djangoAPI } from '../api/axios.jsx';
import { Applicants } from '../pages/Applicants.jsx';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
);

const options = {
  responsive: true,
  plugins: {
    legend: {
      position: 'top',
      align: 'start',
    },
    title: {
      display: true,
      text: 'Aplicaciones',
    },
  },
};

const labels = []

export function MyChart() {
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    const getApplicantsData = async () => {
      try {
        const response = await djangoAPI.get("users/whatsapp-users");
        const dataDelBackend = response.data;
        const fechas = []
        for (let index = 0; index < dataDelBackend.length; index++) {
            const element = dataDelBackend[index];
            labels[index] = element.date_request
        }
        // Simula contar cuántos usuarios aplicaron por día (ajusta esto según tu backend)
        const counts = labels.map(() => labels.length );

        const data = {
          labels,
          datasets: [
            {
              label: 'Aplicaciones',
              data: counts  ,
              borderColor: '#1F3361',
              backgroundColor: '#1F3361',
            },
          ],
        };

        setChartData(data);
      } catch (error) {
        console.error("Hubo un error:", error);
      }
    };

    getApplicantsData();
  }, []);

  return chartData ? <Bar options={options} data={chartData} /> : <p>Cargando...</p>;
}
