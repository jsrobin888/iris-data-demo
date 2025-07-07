'use client';

import { useState, useEffect } from 'react';
import { Chart as ChartJS, LinearScale, PointElement, LineElement, Tooltip, Legend } from 'chart.js';
import { Scatter } from 'react-chartjs-2';
import { IrisData } from '@/types';

ChartJS.register(LinearScale, PointElement, LineElement, Tooltip, Legend);

interface DashboardProps {
  user: { user: string; access: string };
  onLogout: () => void;
}

export default function Dashboard({ user, onLogout }: DashboardProps) {
  const [data, setData] = useState<IrisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [visibleSeries, setVisibleSeries] = useState({
    sepal_width: true,
    petal_length: true,
    petal_width: true
  });
  const [yRange, setYRange] = useState({ min: 0, max: 8 });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await fetch('/api/data');
      if (response.ok) {
        const result = await response.json();
        setData(result);
      }
    } catch (err) {
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await fetch('/api/logout', { method: 'POST' });
    onLogout();
  };

  const toggleSeries = (series: keyof typeof visibleSeries) => {
    setVisibleSeries(prev => ({
      ...prev,
      [series]: !prev[series]
    }));
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg text-red-600">Failed to load data</div>
      </div>
    );
  }

  const colors = {
    sepal_width: 'rgb(255, 99, 132)',
    petal_length: 'rgb(54, 162, 235)',
    petal_width: 'rgb(75, 192, 192)'
  };

  const createChartData = (xData: number[], xLabel: string) => {
    const datasets = [];
    const seriesKeys = Object.keys(visibleSeries) as (keyof typeof visibleSeries)[];

    for (const series of seriesKeys) {
      if (visibleSeries[series]) {
        datasets.push({
          label: series.replace('_', ' '),
          data: xData.map((x, i) => ({
            x,
            y: data[series][i]
          })),
          backgroundColor: colors[series],
          borderColor: colors[series],
          borderWidth: 1
        });
      }
    }

    return { datasets };
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        title: {
          display: true,
          text: 'Value'
        }
      },
      y: {
        title: {
          display: true,
          text: 'Value'
        },
        min: yRange.min,
        max: yRange.max
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-2xl font-bold text-gray-900">
              Iris Dataset - {data.species.charAt(0).toUpperCase() + data.species.slice(1)} Data
            </h1>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
            >
              Logout
            </button>
          </div>

          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <div className="flex flex-wrap gap-6 items-center">
              <div className="flex gap-4">
                {Object.keys(visibleSeries).map((series) => (
                  <label key={series} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={visibleSeries[series as keyof typeof visibleSeries]}
                      onChange={() => toggleSeries(series as keyof typeof visibleSeries)}
                      className="w-4 h-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                    <span className="text-sm font-medium text-gray-700">
                      {series.replace('_', ' ')}
                    </span>
                  </label>
                ))}
              </div>

              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-700">Y-axis range:</span>
                <input
                  type="number"
                  value={yRange.min}
                  onChange={(e) => setYRange(prev => ({ ...prev, min: Number(e.target.value) }))}
                  className="w-16 px-2 py-1 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                />
                <span className="text-gray-500">to</span>
                <input
                  type="number"
                  value={yRange.max}
                  onChange={(e) => setYRange(prev => ({ ...prev, max: Number(e.target.value) }))}
                  className="w-16 px-2 py-1 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">Plot 1: Sepal Length vs Values</h3>
              <div style={{ height: '400px' }}>
                <Scatter
                  data={createChartData(data.sepal_length, 'Sepal Length')}
                  options={{
                    ...chartOptions,
                    scales: {
                      ...chartOptions.scales,
                      x: { ...chartOptions.scales.x, title: { ...chartOptions.scales.x.title, text: 'Sepal Length' } }
                    }
                  }}
                />
              </div>
            </div>

            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">Plot 2: Petal Length vs Values</h3>
              <div style={{ height: '400px' }}>
                <Scatter
                  data={createChartData(data.petal_length, 'Petal Length')}
                  options={{
                    ...chartOptions,
                    scales: {
                      ...chartOptions.scales,
                      x: { ...chartOptions.scales.x, title: { ...chartOptions.scales.x.title, text: 'Petal Length' } }
                    }
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}