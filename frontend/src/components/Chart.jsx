import React from 'react'
import { Line, Pie, Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  BarElement,
  Title,
  Tooltip,
  Legend
)

export function LineChart({ data, title }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-lg font-bold mb-4 text-gray-800">{title}</h3>
      <Line data={data} options={{
        responsive: true,
        plugins: {
          legend: { display: true, position: 'top' },
        },
        scales: {
          y: { beginAtZero: true },
        },
      }} />
    </div>
  )
}

export function PieChart({ data, title }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-lg font-bold mb-4 text-gray-800">{title}</h3>
      <div style={{ maxWidth: '300px', margin: '0 auto' }}>
        <Pie data={data} options={{
          responsive: true,
          plugins: {
            legend: { display: true, position: 'bottom' },
          },
        }} />
      </div>
    </div>
  )
}

export function BarChart({ data, title }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-lg font-bold mb-4 text-gray-800">{title}</h3>
      <Bar data={data} options={{
        responsive: true,
        plugins: {
          legend: { display: true, position: 'top' },
        },
        scales: {
          y: { beginAtZero: true },
        },
      }} />
    </div>
  )
}
